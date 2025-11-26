"""LangGraph workflow orchestration for three-agent system."""

from typing import TypedDict, List, Dict, Any, Optional
from langgraph.graph import StateGraph, END
import time
import sys
from pathlib import Path

# Add parent directory to path to allow imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.core.state import AgentState
from src.core.models.context import ContextDocument
from src.agents.nodes import create_agent_nodes


class AgentWorkflow:
    """LangGraph orchestration for three-agent workflow."""

    def __init__(self):
        """Initialize agent workflow."""
        self.agents = create_agent_nodes()
        self.workflow = self._build_workflow()

    def _build_workflow(self) -> StateGraph:
        """Construct LangGraph StateGraph.

        Workflow:
        User Query → Retrieve Context → Archivist → Strategist → Coach → Response

        Returns:
            Compiled StateGraph
        """
        # Define the state schema
        workflow = StateGraph(AgentState)

        # Add nodes
        workflow.add_node("retrieve_context", self._retrieve_context)
        workflow.add_node("archivist", self._archivist_node)
        workflow.add_node("strategist", self._strategist_node)
        workflow.add_node("coach", self._coach_node)
        workflow.add_node("finalize", self._finalize_response)

        # Define edges
        workflow.set_entry_point("retrieve_context")
        workflow.add_edge("retrieve_context", "archivist")
        workflow.add_edge("archivist", "strategist")
        workflow.add_edge("strategist", "coach")
        workflow.add_edge("coach", "finalize")
        workflow.add_edge("finalize", END)

        return workflow.compile()

    async def invoke(
        self,
        user_query: str,
        context_docs: List[ContextDocument],
        conversation_history: Optional[List[str]] = None,
        session_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Execute complete advisory workflow.

        Args:
            user_query: User's question
            context_docs: Retrieved relevant documents
            conversation_history: Previous conversation context
            session_id: Optional session ID for continuing conversations

        Returns:
            Dictionary with session_id, agent responses, and metadata
        """
        start_time = time.time()

        # Initialize state
        initial_state = AgentState(
            user_query=user_query,
            query_type="initial" if not session_id else "follow_up",
            context_documents=[doc.model_dump() for doc in context_docs],
            retrieved_count=len(context_docs),
            archivist_response=None,
            strategist_response=None,
            coach_response=None,
            processing_times={},
            tokens_used={},
            errors=[],
            final_advice=None,
            session_id=session_id,
            conversation_history=conversation_history,
            workflow_complete=False,
            timeout_occurred=False,
        )

        # Execute workflow
        try:
            result = await self.workflow.ainvoke(initial_state)

            total_time = time.time() - start_time

            return {
                "session_id": result["session_id"],
                "user_query": user_query,
                "archivist_response": result["archivist_response"],
                "strategist_response": result["strategist_response"],
                "coach_response": result["coach_response"],
                "final_advice": result["final_advice"],
                "context_documents": context_docs,
                "processing_time": total_time,
                "errors": result["errors"],
                "timeout_occurred": result["timeout_occurred"],
            }

        except Exception as e:
            total_time = time.time() - start_time
            error_msg = f"Workflow execution failed: {str(e)}"
            print(f"❌ {error_msg}")

            return {
                "session_id": initial_state.get("session_id"),
                "user_query": user_query,
                "archivist_response": None,
                "strategist_response": None,
                "coach_response": None,
                "final_advice": f"抱歉，处理您的请求时出现错误：{str(e)}",
                "context_documents": context_docs,
                "processing_time": total_time,
                "errors": [error_msg],
                "timeout_occurred": False,
            }

    def _retrieve_context(self, state: AgentState) -> AgentState:
        """Retrieve and format context documents."""
        print(f"🔍 Retrieved {state['retrieved_count']} relevant documents")

        return state

    def _archivist_node(self, state: AgentState) -> AgentState:
        """Process through Archivist agent."""
        print("📚 Archivist analyzing facts...")

        try:
            from ..core.state import AgentContext

            agent_context = AgentContext(
                user_query=state["user_query"],
                context_documents=state["context_documents"],
                agent_type="archivist",
                conversation_history=state.get("conversation_history"),
            )

            start_time = time.time()
            response = self.agents["archivist"].process(agent_context)
            processing_time = time.time() - start_time

            state["archivist_response"] = response
            state["processing_times"]["archivist"] = processing_time

            print(f"✅ Archivist completed in {processing_time:.2f}s")

        except Exception as e:
            error_msg = f"Archivist error: {str(e)}"
            state["errors"].append(error_msg)
            state["archivist_response"] = f"抱歉，档案管理员处理时遇到问题：{str(e)}"
            print(f"❌ {error_msg}")

        return state

    def _strategist_node(self, state: AgentState) -> AgentState:
        """Process through Strategist agent."""
        print("💡 Strategist analyzing options...")

        try:
            from ..core.state import AgentContext

            agent_context = AgentContext(
                user_query=state["user_query"],
                context_documents=state["context_documents"],
                agent_type="strategist",
                conversation_history=state.get("conversation_history"),
            )

            start_time = time.time()
            response = self.agents["strategist"].process(agent_context)
            processing_time = time.time() - start_time

            state["strategist_response"] = response
            state["processing_times"]["strategist"] = processing_time

            print(f"✅ Strategist completed in {processing_time:.2f}s")

        except Exception as e:
            error_msg = f"Strategist error: {str(e)}"
            state["errors"].append(error_msg)
            state["strategist_response"] = f"抱歉，战略顾问处理时遇到问题：{str(e)}"
            print(f"❌ {error_msg}")

        return state

    def _coach_node(self, state: AgentState) -> AgentState:
        """Process through Coach agent."""
        print("🎯 Coach providing guidance...")

        try:
            from ..core.state import AgentContext

            agent_context = AgentContext(
                user_query=state["user_query"],
                context_documents=state["context_documents"],
                agent_type="coach",
                conversation_history=state.get("conversation_history"),
            )

            start_time = time.time()
            response = self.agents["coach"].process(agent_context)
            processing_time = time.time() - start_time

            state["coach_response"] = response
            state["processing_times"]["coach"] = processing_time

            print(f"✅ Coach completed in {processing_time:.2f}s")

        except Exception as e:
            error_msg = f"Coach error: {str(e)}"
            state["errors"].append(error_msg)
            state["coach_response"] = f"抱歉，人生教练处理时遇到问题：{str(e)}"
            print(f"❌ {error_msg}")

        return state

    def _finalize_response(self, state: AgentState) -> AgentState:
        """Finalize and prepare response."""
        # Combine all responses into final advice
        final_parts = []

        if state["archivist_response"]:
            final_parts.append(state["archivist_response"])

        if state["strategist_response"]:
            final_parts.append(state["strategist_response"])

        if state["coach_response"]:
            final_parts.append(state["coach_response"])

        state["final_advice"] = "\n\n---\n\n".join(final_parts)
        state["workflow_complete"] = True

        print("✨ Workflow complete")

        return state

    def get_state_schema(self) -> Dict[str, Any]:
        """Define LangGraph state structure.

        Returns:
            State schema with type hints
        """
        return {
            "user_query": str,
            "query_type": str,
            "context_documents": List[Dict[str, Any]],
            "retrieved_count": int,
            "archivist_response": Optional[str],
            "strategist_response": Optional[str],
            "coach_response": Optional[str],
            "processing_times": Dict[str, float],
            "tokens_used": Dict[str, int],
            "errors": List[str],
            "final_advice": Optional[str],
            "session_id": Optional[str],
            "conversation_history": Optional[List[str]],
            "workflow_complete": bool,
            "timeout_occurred": bool,
        }
