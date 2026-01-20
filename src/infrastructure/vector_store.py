# infrastructure/vector_store.py
import os
import shutil
from typing import List

from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings

# ⬇️ 引入我们的核心模型
from src.core.models.domain_models import LifeEvent


class KnowledgeBase:
    def __init__(self, persist_dir: str = "./data/chroma_db", reset_db: bool = False):
        # ... (这部分保持不变) ...
        self.persist_dir = persist_dir
        self.embeddings = OllamaEmbeddings(model="nomic-embed-text:latest")
        if reset_db and os.path.exists(persist_dir):
            shutil.rmtree(persist_dir)
        self.vector_db = Chroma(
            collection_name="echo_board_memory",
            embedding_function=self.embeddings,
            persist_directory=self.persist_dir
        )

    def add_events(self, events: List[LifeEvent]):
        """
        [变更]: 现在接收强类型的 LifeEvent 列表
        """
        if not events:
            return

        # 转换: LifeEvent -> LangChain Document
        docs = [event.to_langchain_document() for event in events]

        # 存入 Chroma (使用 LifeEvent 的 UUID 作为数据库 ID)
        ids = [event.id for event in events]
        self.vector_db.add_documents(documents=docs, ids=ids)

        print(f"💾 [KnowledgeBase] 已存入 {len(events)} 个 LifeEvent 对象。")

    def search(self, query: str, k: int = 5) -> List[LifeEvent]:
        """
        [变更]: 返回 LifeEvent 列表，而不是 Document
        """
        raw_docs = self.vector_db.similarity_search(query, k=k)

        # 转换: LangChain Document -> LifeEvent
        return [LifeEvent.from_langchain_document(doc) for doc in raw_docs]
