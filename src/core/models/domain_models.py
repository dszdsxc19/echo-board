# core/domain_models.py
import uuid
from typing import Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from langchain_core.documents import Document

class LifeEvent(BaseModel):
    """
    领域模型：代表发生过的任何事实（日记、账单、提交记录）。
    它是系统内部流转的唯一货币，不依赖任何外部框架。
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    content: str
    source_type: str  # e.g., "obsidian", "alipay", "github"
    created_at: datetime = Field(default_factory=datetime.now)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        # 允许从 attributes 初始化
        from_attributes = True

    def to_langchain_document(self) -> Document:
        """
        [Adapter]: 将领域模型转换为 LangChain 能够理解的 Document 对象
        用于写入向量数据库。
        """
        # 我们把 id, source_type, created_at 都压入 metadata，以便向量库存储
        full_metadata = self.metadata.copy()
        full_metadata.update({
            "uuid": self.id,
            "source_type": self.source_type,
            "created_at": self.created_at.isoformat()
        })
        
        return Document(
            page_content=self.content,
            metadata=full_metadata
        )

    @classmethod
    def from_langchain_document(cls, doc: Document) -> "LifeEvent":
        """
        [Adapter]: 将检索回来的 Document 还原为领域模型
        """
        meta = doc.metadata.copy()
        
        # 提取核心字段
        uuid_str = meta.pop("uuid", str(uuid.uuid4()))
        source_type = meta.pop("source_type", "unknown")
        created_at_str = meta.pop("created_at", None)
        
        created_at = datetime.now()
        if created_at_str:
            try:
                created_at = datetime.fromisoformat(created_at_str)
            except:
                pass

        return cls(
            id=uuid_str,
            content=doc.page_content,
            source_type=source_type,
            created_at=created_at,
            metadata=meta # 剩下的都是普通元数据
        )