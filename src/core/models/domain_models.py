from pydantic import BaseModel, Field
from typing import Dict, Optional
from datetime import datetime

class LifeEvent(BaseModel):
    """系统的原子数据单位"""
    id: str
    content: str
    source_type: str = "obsidian"
    metadata: Dict = Field(default_factory=dict)
    created_at: Optional[datetime] = None
