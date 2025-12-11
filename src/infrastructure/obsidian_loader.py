import os
from typing import List
from langchain_ollama import OllamaEmbeddings
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
from src.core.models.domain_models import LifeEvent # ⬇️ 引入模型

# ==========================================
# 1. 模拟数据 (Mock Data for MVP)
# 在实际项目中，这里会替换为读取你的 Obsidian 文件夹
# ==========================================
OBSIDIAN_MOCK_CONTENT = """
# 2023-10-10 工作复盘

## 项目 A 的反思
今天项目 A 的进度非常滞后。主要原因是在架构选型上犹豫太久。
我认为我们需要重新评估 Go 语言在目前的适用性。
目前团队对 Go 的掌握程度不够，导致开发效率低下。

## 待办清单
- 记得买猫粮
- 预约牙医
- 读《软件设计之美》第3章

# 2023-10-11 心情日记

## 焦虑时刻
昨晚失眠了，一直在想房贷的事情。
感觉现在的收入结构太单一，抗风险能力差。
"""

# ==========================================
# 2. 核心逻辑：结构化切分 (The Ingestion Logic)
# ==========================================
class MemoryIngestionEngine:
    def __init__(self, knowledge_base):
        self.kb = knowledge_base

    def process_file(self, markdown_text: str, source_name: str = "unknown") -> List[LifeEvent]:
        """
        核心算法：利用 Markdown 标题保留上下文
        """
        # A. 定义我们要切分的层级
        headers_to_split_on = [
            ("#", "Date/Title"),
            ("##", "Section"),
            ("###", "SubSection"),
        ]

        # B. 第一刀：按标题切分 (保留结构元数据)
        markdown_splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=headers_to_split_on
        )
        md_header_splits = markdown_splitter.split_text(markdown_text)

        # C. 第二刀：按字符长度切分 (防止长文溢出，同时保留标题元数据)
        # 这一步对于 "项目 A 的反思" 这种长段落很重要
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50
        )
        final_splits = text_splitter.split_documents(md_header_splits)

        life_events = []
        
        for doc in final_splits:
            # 在这里，我们将弱类型的 doc 封装为强类型的 LifeEvent
            event = LifeEvent(
                content=doc.page_content,
                source_type="obsidian",
                metadata={
                    "source_file": source_name,
                    # 将切分器提取的标题层级放入 metadata
                    **doc.metadata 
                }
            )
            life_events.append(event)

        print(f"⚙️ [Ingestion] 生成了 {len(life_events)} 个 LifeEvent 实体")
        
        # 存入仓库 (调用新的 add_events 方法)
        self.kb.add_events(life_events)
        
        return life_events
