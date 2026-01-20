"""Data models for context and retrieved documents."""

from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ContextDocument(BaseModel):
    """Relevant document chunk retrieved for a query."""

    doc_id: UUID = Field(default_factory=uuid4, description="Unique identifier")
    session_id: UUID = Field(description="Reference to parent ConversationSession")
    chunk_id: str = Field(description="Reference to NoteChunk")
    similarity_score: float = Field(description="Cosine similarity to query (0-1)")
    retrieval_rank: int = Field(description="Position in retrieved results (1-10)")
    note_path: str = Field(description="Source note file path")
    excerpt: str = Field(description="Display excerpt for UI evidence")
    date_context: Optional[str] = Field(default=None, description="Date context from note for relevance")

    model_config = ConfigDict(
        extra="allow",
        json_encoders={
            UUID: lambda v: str(v),
        },
    )

    @field_validator("similarity_score")
    @classmethod
    def validate_similarity_score(cls, v: float) -> float:
        """Ensure similarity score is between 0 and 1."""
        if v < 0 or v > 1:
            raise ValueError("similarity_score must be between 0 and 1")
        return v

    @field_validator("retrieval_rank")
    @classmethod
    def validate_retrieval_rank(cls, v: int) -> int:
        """Ensure retrieval rank is between 1 and 10."""
        if v < 1 or v > 10:
            raise ValueError("retrieval_rank must be between 1 and 10")
        return v

    @field_validator("excerpt")
    @classmethod
    def validate_excerpt(cls, v: str) -> str:
        """Ensure excerpt is not empty."""
        if not v or not v.strip():
            raise ValueError("excerpt cannot be empty")
        return v
