import os

from langchain_ollama import OllamaEmbeddings
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
from src.infrastructure.vector_store import vector_store, embeddings
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
    def __init__(self, vector_store: Chroma, embeddings: OllamaEmbeddings):
        # 初始化 Embedding 模型 (这里假设你配置好了 OPENAI_API_KEY 环境变量)
        self.embeddings = embeddings
        self.vector_store = vector_store

    def process_markdown(self, markdown_text):
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

        # D. 注入 Source Type (为未来扩展做准备)
        for doc in final_splits:
            doc.metadata["source_type"] = "obsidian_note"

        print(f"✅ 成功切分为 {len(final_splits)} 个记忆片段")
        return final_splits

    def save_to_memory(self, chunks):
        """存入向量库"""
        self.vector_store.add_documents(chunks)
        print("💾 已存入向量数据库")

    def search(self, query, top_k=3):
        """
        史官的雏形：检索接口
        """
        results = self.vector_store.similarity_search_with_score(query, k=top_k)
        return results

# ==========================================
# 3. 运行测试 (Verify the Core)
# ==========================================
if __name__ == "__main__":
    # A. 启动引擎
    engine = MemoryIngestionEngine(vector_store=vector_store, embeddings=embeddings)

    # B. 注入数据
    print("--- 正在处理数据 ---")
    chunks = engine.process_markdown(OBSIDIAN_MOCK_CONTENT)
    
    # 打印一下切分结果，看看元数据是否保留了 (关键验证点!)
    print("\n[切分样本查看]:")
    print(f"内容: {chunks[1].page_content}")
    print(f"元数据: {chunks[1].metadata}") 
    # 预期输出 metadata: {'Date/Title': '2023-10-10 工作复盘', 'Section': '待办清单', ...}
    
    engine.save_to_memory(chunks)

    # C. 模拟 Agent 检索
    print("\n--- 模拟 Agent 检索 ---")
    
    # 测试 1: 模糊情感检索
    query1 = "我最近为什么感到压力大？"
    print(f"\n🔍 Query: {query1}")
    results1 = engine.search(query1, top_k=3)
    for res, score in results1:
        print(f"- [匹配度] {res.page_content[:50]}... (来自: {res.metadata.get('Date/Title')} > {res.metadata.get('Section')}) [SIM={score:3f}]")

    # 测试 2: 具体事务检索
    query2 = "我要买什么给宠物？"
    print(f"\n🔍 Query: {query2}")
    results2 = engine.search(query2, top_k=3)
    for res, score in results2:
        print(f"- [匹配度] {res.page_content[:50]}... (来自: {res.metadata.get('Section')}) [SIM={score:3f}]")

