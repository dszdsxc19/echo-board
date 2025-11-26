"""Data models for notes and chunks."""

from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator, ConfigDict


class Note(BaseModel):
    """Represents a markdown note from Obsidian."""

    file_path: str = Field(description="Absolute path to the markdown file")
    title: Optional[str] = Field(default=None, description="Note title from frontmatter or filename")
    date: Optional[datetime] = Field(default=None, description="Date from frontmatter metadata")
    tags: Optional[List[str]] = Field(default=None, description="List of tags from frontmatter")
    content: str = Field(description="Raw markdown content body")
    frontmatter: Optional[Dict[str, Any]] = Field(default=None, description="Raw frontmatter metadata dict")
    modified_at: datetime = Field(description="Last file modification timestamp")
    created_at: datetime = Field(description="When note was first ingested")
    embedding_id: Optional[str] = Field(default=None, description="ChromaDB document ID for vector search")

    model_config = ConfigDict(
        extra="allow",
        json_encoders={datetime: lambda v: v.isoformat()},
    )

    @field_validator("file_path")
    @classmethod
    def validate_file_path(cls, v: str) -> str:
        """Ensure file path is a valid string."""
        if not v or not isinstance(v, str):
            raise ValueError("file_path must be a non-empty string")
        return v

    @field_validator("content")
    @classmethod
    def validate_content(cls, v: str) -> str:
        """Ensure content is not empty."""
        if not v or not v.strip():
            raise ValueError("content cannot be empty")
        return v

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        """Ensure tags is a list of strings if present."""
        if v is not None and not isinstance(v, list):
            raise ValueError("tags must be a list of strings")
        if v is not None and not all(isinstance(tag, str) for tag in v):
            raise ValueError("all tags must be strings")
        return v

    @classmethod
    def from_file(cls, file_path: str, content: str, frontmatter: Optional[Dict[str, Any]] = None) -> "Note":
        """Create a Note from a file."""
        path = Path(file_path)
        modified_at = datetime.fromtimestamp(path.stat().st_mtime)
        created_at = datetime.now()

        # Extract title from frontmatter or filename
        title = None
        date = None
        tags = None

        if frontmatter:
            title = frontmatter.get("title")
            date_str = frontmatter.get("date")
            if date_str:
                try:
                    date = datetime.fromisoformat(str(date_str).replace("Z", "+00:00"))
                except (ValueError, TypeError):
                    pass
            tags = frontmatter.get("tags")

        if not title:
            title = path.stem

        return cls(
            file_path=file_path,
            title=title,
            date=date,
            tags=tags,
            content=content,
            frontmatter=frontmatter,
            modified_at=modified_at,
            created_at=created_at,
        )


class NoteChunk(BaseModel):
    """Segmented piece of a note for semantic retrieval."""

    chunk_id: UUID = Field(default_factory=uuid4, description="Unique identifier")
    note_id: str = Field(description="Reference to parent Note (file_path)")
    content: str = Field(description="Text content of chunk")
    word_count: int = Field(description="Number of words in chunk")
    chunk_index: int = Field(description="Position within original note (0-based)")
    overlap_content: Optional[str] = Field(default=None, description="Context from adjacent chunks")
    embedding: Optional[List[float]] = Field(default=None, description="Vector embedding for semantic search")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional chunk metadata")

    model_config = ConfigDict(
        extra="allow",
        json_encoders={UUID: lambda v: str(v)},
    )

    @field_validator("content")
    @classmethod
    def validate_content(cls, v: str) -> str:
        """Ensure content is not empty."""
        if not v or not v.strip():
            raise ValueError("content cannot be empty")
        return v

    @field_validator("word_count")
    @classmethod
    def validate_word_count(cls, v: int) -> int:
        """Ensure word count is positive."""
        if v <= 0:
            raise ValueError("word_count must be positive")
        return v

    @field_validator("chunk_index")
    @classmethod
    def validate_chunk_index(cls, v: int) -> int:
        """Ensure chunk index is non-negative."""
        if v < 0:
            raise ValueError("chunk_index must be non-negative")
        return v

    @field_validator("embedding")
    @classmethod
    def validate_embedding(cls, v: Optional[List[float]]) -> Optional[List[float]]:
        """Ensure embedding is a list of floats if present."""
        if v is not None:
            if not isinstance(v, list):
                raise ValueError("embedding must be a list of floats")
            if not all(isinstance(x, (float, int)) for x in v):
                raise ValueError("embedding must contain only numbers")
        return v

    @classmethod
    def create(
        cls,
        note_id: str,
        content: str,
        chunk_index: int,
        chunk_size: int = 1000,
        overlap: int = 200,
    ) -> "NoteChunk":
        """Create a chunk from note content."""
        words = content.split()
        word_count = len(words)

        return cls(
            note_id=note_id,
            content=content,
            word_count=word_count,
            chunk_index=chunk_index,
            metadata={"chunk_size": chunk_size, "overlap": overlap},
        )
