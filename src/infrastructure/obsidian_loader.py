import logging
import os
from typing import List

from langchain_text_splitters import (
    MarkdownHeaderTextSplitter,
    RecursiveCharacterTextSplitter,
)

from src.core.models.domain_models import LifeEvent
from src.infrastructure.mem0_service import UserProfileService
from src.infrastructure.vector_store import KnowledgeBase

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MemoryIngestionEngine:
    def __init__(self, knowledge_base: KnowledgeBase):
        self.kb = knowledge_base
        self.mem0 = UserProfileService()

    def process_file(self, file_content: str, source_name: str = "unknown", save_to_mem0: bool = True) -> List[LifeEvent]:
        """
        处理单个文件内容 (逻辑保持不变)
        :param file_content: 文件内容
        :param source_name: 文件名
        :param save_to_mem0: 是否保存到 Mem0 (默认 True)
        """
        logger.info(f"📄 开始处理文件: {source_name} (长度: {len(file_content)} 字符)")

        # 1. 结构化切分 (按标题)
        headers_to_split_on = [
            ("#", "Date/Title"),
            ("##", "Section"),
            ("###", "SubSection"),
        ]
        markdown_splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=headers_to_split_on
        )
        md_header_splits = markdown_splitter.split_text(file_content)
        logger.info(f"  └─ 结构化切分完成: {len(md_header_splits)} 个片段")

        # 2. 长度切分
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50
        )
        final_splits = text_splitter.split_documents(md_header_splits)
        logger.info(f"  └─ 长度切分完成: {len(final_splits)} 个块")

        # 3. 转换为 LifeEvent
        life_events = []
        for doc in final_splits:
            event = LifeEvent(
                content=doc.page_content,
                source_type="obsidian",
                metadata={
                    "source_file": source_name,
                    **doc.metadata
                }
            )
            life_events.append(event)

        # 4. 存入仓库
        if life_events:
            self.kb.add_events(life_events)
            logger.info(f"✅ 已保存 {len(life_events)} 个事件到向量数据库")
        else:
            logger.warning(f"⚠️ 未从文件 {source_name} 中提取到有效内容")

        if save_to_mem0:
            self.mem0.remember(file_content)

        return life_events

    def ingest_folder(self, folder_path: str, max_files: int = 100):
        """
        [新增功能] 递归扫描文件夹并导入
        :param folder_path: Obsidian 库的根目录路径
        :param max_files: 安全限制，防止一次性读入几千个文件把钱烧光
        """
        logger.info(f"📂 [Loader] 开始扫描目录: {folder_path}")

        if not os.path.exists(folder_path):
            error_msg = f"路径不存在: {folder_path}"
            logger.error(error_msg)
            raise ValueError(error_msg)

        processed_count = 0
        memories_to_add = []
        batch_size = 5  # Batch size for Mem0 to avoid context limits

        # os.walk 递归遍历所有子目录
        for root, dirs, files in os.walk(folder_path):
            # 过滤掉隐藏文件夹 (如 .obsidian, .git)
            dirs[:] = [d for d in dirs if not d.startswith('.')]

            for file in files:
                if processed_count >= max_files:
                    logger.warning(f"🛑 [Loader] 达到最大文件限制 ({max_files})，停止加载。")
                    break

                if file.endswith(".md"):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            content = f.read()

                        # 获取相对路径作为 source_name (例如: "Work/2023-10-10.md")
                        relative_path = os.path.relpath(file_path, folder_path)

                        # 调用之前的单文件处理逻辑, 但不保存到 Mem0
                        self.process_file(content, source_name=relative_path, save_to_mem0=False)

                        memories_to_add.append(content)
                        processed_count += 1
                        logger.info(f"✅ [{processed_count}] 已处理: {relative_path}")

                        # Batch process mem0
                        if len(memories_to_add) >= batch_size:
                            self.mem0.remember(memories_to_add)
                            memories_to_add = []

                    except Exception as e:
                        error_msg = f"跳过文件 {file}: {e}"
                        logger.warning(error_msg)

            if processed_count >= max_files:
                 break

        # Process remaining memories
        if memories_to_add:
            self.mem0.remember(memories_to_add)

        logger.info(f"🎉 [Loader] 批量导入完成，共处理 {processed_count} 个文件。")
