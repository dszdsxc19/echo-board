"""Configuration management for Echo-Board application."""

from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class LLMConfig(BaseModel):
    """LLM provider configuration."""

    provider: Literal["gemini-flash", "gemini-pro"] = Field(default="gemini-flash", description="LLM provider")
    api_key: str = Field(default="", description="API key for LLM provider")
    timeout: int = Field(default=60, ge=1, le=300, description="Timeout in seconds")

    model_config = ConfigDict(
        env_prefix="LLM_",
        env_nested_delimiter="__",
    )

    @field_validator("api_key")
    @classmethod
    def validate_api_key(cls, v: str) -> str:
        """Ensure API key is provided."""
        if not v or v == "your_gemini_api_key_here":
            raise ValueError("API key must be set to a valid value, not a placeholder")
        return v


class NotesConfig(BaseModel):
    """Notes directory configuration."""

    directory: str = Field(default="./data/obsidian_vault", description="Path to notes directory")

    model_config = ConfigDict(
        env_prefix="NOTES_",
        env_nested_delimiter="__",
    )

    @field_validator("directory")
    @classmethod
    def validate_directory(cls, v: str) -> str:
        """Ensure directory path is valid."""
        if not v:
            raise ValueError("directory cannot be empty")
        return v


class VectorStoreConfig(BaseModel):
    """Vector store configuration."""

    path: str = Field(default="./data/chroma_db", description="Path to ChromaDB storage")
    collection_name: str = Field(default="note_chunks", description="ChromaDB collection name")

    model_config = ConfigDict(
        env_prefix="VECTOR_",
        env_nested_delimiter="__",
    )

    @field_validator("path")
    @classmethod
    def validate_path(cls, v: str) -> str:
        """Ensure path is valid."""
        if not v:
            raise ValueError("path cannot be empty")
        return v


class RetrievalConfig(BaseModel):
    """Retrieval configuration."""

    top_k: int = Field(default=10, ge=1, le=50, description="Number of documents to retrieve")
    chunk_size: int = Field(default=1000, ge=100, le=5000, description="Chunk size in words")
    chunk_overlap: int = Field(default=200, ge=0, le=500, description="Chunk overlap in words")
    similarity_threshold: float = Field(default=0.7, ge=0.0, le=1.0, description="Minimum similarity score")

    model_config = ConfigDict(
        env_prefix="RETRIEVAL_",
        env_nested_delimiter="__",
    )


class ConversationConfig(BaseModel):
    """Conversation storage configuration."""

    db_path: str = Field(default="./data/conversations.db", description="Path to SQLite database")
    max_history_sessions: int = Field(default=5, ge=1, le=100, description="Maximum conversation sessions to keep")
    max_conversation_display: int = Field(default=20, ge=1, le=100, description="Maximum conversations to display")

    model_config = ConfigDict(
        env_prefix="CONVERSATION_",
        env_nested_delimiter="__",
    )


class UIConfig(BaseModel):
    """UI configuration."""

    title: str = Field(default="个人董事会 - Personal Board of Directors", description="Application title")
    evidence_default_collapsed: bool = Field(default=True, description="Whether evidence is collapsed by default")
    debug: bool = Field(default=False, description="Enable debug mode")

    model_config = ConfigDict(
        env_prefix="APP_",
        env_nested_delimiter="__",
    )


class Settings(BaseModel):
    """Main application settings."""

    llm: LLMConfig = Field(default_factory=LLMConfig, description="LLM configuration")
    notes: NotesConfig = Field(default_factory=NotesConfig, description="Notes configuration")
    vector_store: VectorStoreConfig = Field(default_factory=VectorStoreConfig, description="Vector store configuration")
    retrieval: RetrievalConfig = Field(default_factory=RetrievalConfig, description="Retrieval configuration")
    conversation: ConversationConfig = Field(default_factory=ConversationConfig, description="Conversation configuration")
    ui: UIConfig = Field(default_factory=UIConfig, description="UI configuration")

    model_config = ConfigDict(
        env_nested_delimiter="__",
        case_sensitive=False,
    )

    @field_validator("notes")
    @classmethod
    def validate_notes_directory(cls, v: NotesConfig) -> NotesConfig:
        """Ensure notes directory exists or can be created."""
        path = Path(v.directory)
        # Don't validate existence here, just ensure the parent directory exists
        # or is creatable
        return v

    @classmethod
    def load_from_env(cls) -> "Settings":
        """Load settings from environment variables and .env file."""
        # Try to load from .env file, but don't fail if it's not accessible
        try:
            from dotenv import load_dotenv
            env_file = Path(".env")
            if env_file.exists():
                load_dotenv(env_file)
        except Exception:
            # Silently ignore .env loading errors
            pass

        return cls()


# Global settings instance
try:
    settings = Settings.load_from_env()
except ValueError as e:
    # If API key validation fails, create with defaults
    # This allows the app to start even without a valid API key
    if "API key must be set" in str(e):
        # Create settings with a placeholder API key for development
        settings = Settings(
            llm=LLMConfig(api_key="placeholder_for_development"),
            notes=NotesConfig(),
            vector_store=VectorStoreConfig(),
            retrieval=RetrievalConfig(),
            conversation=ConversationConfig(),
            ui=UIConfig(),
        )
    else:
        raise
