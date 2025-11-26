"""LangGraph state definitions for agent workflow."""

from typing import List, Optional, Dict, Any
from typing_extensions import TypedDict

from pydantic import BaseModel, Field


class AgentState(TypedDict):
    """State maintained throughout the agent workflow."""

    # User input
    user_query: str
    query_type: str

    # Retrieved context
    context_documents: List[Dict[str, Any]]
    retrieved_count: int

    # Agent responses
    archivist_response: Optional[str]
    strategist_response: Optional[str]
    coach_response: Optional[str]

    # Processing metadata
    processing_times: Dict[str, float]
    tokens_used: Dict[str, int]
    errors: List[str]

    # Final output
    final_advice: Optional[str]
    session_id: Optional[str]
    conversation_history: Optional[List[str]]

    # Control flags
    workflow_complete: bool
    timeout_occurred: bool


class AgentContext(BaseModel):
    """Context passed to individual agents."""

    user_query: str = Field(description="The user's question")
    context_documents: List[Dict[str, Any]] = Field(
        default_factory=list, description="Retrieved relevant documents"
    )
    agent_type: str = Field(description="Type of agent (archivist, strategist, coach)")
    conversation_history: Optional[List[str]] = Field(
        default=None, description="Previous conversation context"
    )

    class Config:
        arbitrary_types_allowed = True


class WorkflowMetadata(BaseModel):
    """Metadata tracking for the workflow."""

    session_id: str
    start_time: float
    total_processing_time: Optional[float] = None
    agents_completed: List[str] = []
    agents_failed: List[str] = []
    timeout_occurred: bool = False

    class Config:
        arbitrary_types_allowed = True
