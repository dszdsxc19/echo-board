"""Data models for conversations and agent responses."""

from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator, ConfigDict


class SessionStatus(str, Enum):
    """Status of a conversation session."""

    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"


class AgentType(str, Enum):
    """Type of agent in the workflow."""

    ARCHIVIST = "archivist"
    STRATEGIST = "strategist"
    COACH = "coach"


class QueryType(str, Enum):
    """Type of user query."""

    INITIAL = "initial"
    FOLLOW_UP = "follow_up"
    CLARIFICATION = "clarification"


class ConversationSession(BaseModel):
    """Discrete advisory interaction including query and all agent responses."""

    session_id: UUID = Field(default_factory=uuid4, description="Unique identifier")
    user_query: str = Field(description="User's question or prompt")
    created_at: datetime = Field(default_factory=datetime.now, description="When session started")
    completed_at: Optional[datetime] = Field(default=None, description="When session finished")
    status: SessionStatus = Field(default=SessionStatus.ACTIVE, description="Session status")
    processing_time: Optional[float] = Field(default=None, description="Seconds from start to completion")
    final_advice: Optional[str] = Field(default=None, description="Synthesized advice from coach")
    conversation_history: Optional[List[str]] = Field(default=None, description="Previous conversation context for follow-ups")

    model_config = ConfigDict(
        extra="allow",
        json_encoders={
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v),
            SessionStatus: lambda v: v.value,
        },
    )

    @field_validator("user_query")
    @classmethod
    def validate_user_query(cls, v: str) -> str:
        """Ensure user query is not empty."""
        if not v or not v.strip():
            raise ValueError("user_query cannot be empty")
        return v

    @field_validator("processing_time")
    @classmethod
    def validate_processing_time(cls, v: Optional[float]) -> Optional[float]:
        """Ensure processing time is positive if present."""
        if v is not None and v < 0:
            raise ValueError("processing_time must be non-negative")
        return v

    def mark_completed(self, processing_time: float) -> None:
        """Mark session as completed."""
        self.status = SessionStatus.COMPLETED
        self.completed_at = datetime.now()
        self.processing_time = processing_time

    def mark_failed(self) -> None:
        """Mark session as failed."""
        self.status = SessionStatus.FAILED
        self.completed_at = datetime.now()


class AgentResponse(BaseModel):
    """Output from one of the three specialized agents."""

    response_id: UUID = Field(default_factory=uuid4, description="Unique identifier")
    session_id: UUID = Field(description="Reference to parent ConversationSession")
    agent_type: AgentType = Field(description="Type of agent")
    response_text: str = Field(description="Agent's response content")
    processing_order: int = Field(description="Order in workflow (1=archivist, 2=strategist, 3=coach)")
    processing_time: float = Field(description="Time taken for this agent's response")
    tokens_used: Optional[int] = Field(default=None, description="LLM token count")
    cites_context: bool = Field(default=False, description="Whether response includes evidence citations")
    context_documents: Optional[List[str]] = Field(default=None, description="List of ContextDocument IDs referenced")

    model_config = ConfigDict(
        extra="allow",
        json_encoders={
            UUID: lambda v: str(v),
            AgentType: lambda v: v.value,
        },
    )

    @field_validator("agent_type")
    @classmethod
    def validate_agent_type(cls, v: AgentType) -> AgentType:
        """Validate agent type."""
        if not isinstance(v, AgentType):
            raise ValueError("agent_type must be a valid AgentType")
        return v

    @field_validator("processing_order")
    @classmethod
    def validate_processing_order(cls, v: int) -> int:
        """Ensure processing order is 1-3."""
        if v < 1 or v > 3:
            raise ValueError("processing_order must be between 1 and 3")
        return v

    @field_validator("response_text")
    @classmethod
    def validate_response_text(cls, v: str) -> str:
        """Ensure response text is not empty."""
        if not v or not v.strip():
            raise ValueError("response_text cannot be empty")
        return v

    @field_validator("processing_time")
    @classmethod
    def validate_processing_time(cls, v: float) -> float:
        """Ensure processing time is positive."""
        if v < 0:
            raise ValueError("processing_time must be non-negative")
        return v


class UserQuery(BaseModel):
    """User's question or prompt that initiates advisory workflow."""

    query_id: UUID = Field(default_factory=uuid4, description="Unique identifier")
    session_id: UUID = Field(description="Reference to parent ConversationSession")
    query_text: str = Field(description="The actual question text")
    query_type: QueryType = Field(default=QueryType.INITIAL, description="Type of query")
    previous_query_id: Optional[UUID] = Field(default=None, description="Reference to prior query for context")
    timestamp: datetime = Field(default_factory=datetime.now, description="When query was submitted")

    model_config = ConfigDict(
        extra="allow",
        json_encoders={
            UUID: lambda v: str(v),
            QueryType: lambda v: v.value,
            datetime: lambda v: v.isoformat(),
        },
    )

    @field_validator("query_text")
    @classmethod
    def validate_query_text(cls, v: str) -> str:
        """Ensure query text is not empty."""
        if not v or not v.strip():
            raise ValueError("query_text cannot be empty")
        return v

    @field_validator("query_type")
    @classmethod
    def validate_query_type(cls, v: QueryType) -> QueryType:
        """Validate query type."""
        if not isinstance(v, QueryType):
            raise ValueError("query_type must be a valid QueryType")
        return v

    @field_validator("previous_query_id")
    @classmethod
    def validate_previous_query_id(
        cls, v: Optional[UUID], info: Dict[str, Any]
    ) -> Optional[UUID]:
        """Ensure previous_query_id is provided for follow-up queries."""
        query_type = info.data.get("query_type")
        if query_type == QueryType.FOLLOW_UP and v is None:
            raise ValueError("previous_query_id must be provided for follow-up queries")
        return v
