"""Agent function nodes for the three-agent workflow."""

import time
import signal
from typing import List, Dict, Any, Optional
from pathlib import Path
import sys

# Add parent directory to path to allow imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage

from src.core.config import settings
from src.core.models.context import ContextDocument
from src.core.state import AgentContext


class BaseAgentNode:
    """Base class for all agent nodes."""

    def __init__(self, agent_type: str, prompt_file: str):
        """Initialize agent node.

        Args:
            agent_type: Type of agent (archivist, strategist, coach)
            prompt_file: Path to prompt template file
        """
        self.agent_type = agent_type
        self.prompt_file = prompt_file
        self.system_prompt = self._load_prompt()
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash-latest",
            google_api_key=settings.llm.api_key,
            timeout=settings.llm.timeout,
        )

    def _load_prompt(self) -> str:
        """Load agent prompt from file."""
        path = Path(self.prompt_file)
        if not path.exists():
            raise FileNotFoundError(f"Prompt file not found: {self.prompt_file}")
        return path.read_text(encoding="utf-8")

    def process(
        self,
        agent_context: AgentContext,
    ) -> str:
        """Process query through agent.

        Args:
            agent_context: Context including query and retrieved documents

        Returns:
            Agent response text

        Raises:
            LLMError: LLM inference failed
            TimeoutError: Processing exceeded timeout
        """
        start_time = time.time()

        try:
            # Format context documents for the prompt
            context_str = self._format_context_documents(agent_context.context_documents)

            # Prepare messages
            messages = [
                SystemMessage(content=self.system_prompt),
                HumanMessage(
                    content=f"""
用户问题：{agent_context.user_query}

相关文档内容：
{context_str}

请基于这些信息回答用户的问题。
"""
                ),
            ]

            # Call LLM with timeout
            try:
                # Set up timeout handler
                def timeout_handler(signum, frame):
                    raise TimeoutError(f"{self.agent_type} processing timed out after {settings.llm.timeout}s")

                signal.signal(signal.SIGALRM, timeout_handler)
                signal.alarm(settings.llm.timeout)

                # Call LLM
                response = self.llm.invoke(messages)
                response_text = response.content

                # Cancel timeout
                signal.alarm(0)

            except TimeoutError:
                # Graceful degradation on timeout
                print(f"⚠️ {self.agent_type} timed out, using fallback")
                return self._get_fallback_response(agent_context, timeout_occurred=True)

            processing_time = time.time() - start_time

            # Check if processing took too long
            if processing_time > settings.llm.timeout:
                print(f"⚠️ {self.agent_type} took {processing_time:.2f}s (long processing time)")

            # Log successful processing
            print(f"✅ {self.agent_type} processed in {processing_time:.2f}s")

            return response_text

        except Exception as e:
            processing_time = time.time() - start_time
            error_msg = f"Error processing {self.agent_type}: {str(e)}"
            print(f"❌ {error_msg} (took {processing_time:.2f}s)")

            # Determine error type and provide appropriate fallback
            if isinstance(e, (TimeoutError,)):
                return self._get_fallback_response(agent_context, timeout_occurred=True)
            elif isinstance(e, (ConnectionError, OSError)):
                return self._get_fallback_response(agent_context, connection_error=True)
            else:
                # Generic error
                return self._get_fallback_response(agent_context, generic_error=True)

    def _get_fallback_response(
        self,
        agent_context: AgentContext,
        timeout_occurred: bool = False,
        connection_error: bool = False,
        generic_error: bool = False,
    ) -> str:
        """Generate fallback response when LLM fails.

        Args:
            agent_context: Context including query and retrieved documents
            timeout_occurred: Whether timeout occurred
            connection_error: Whether connection error occurred
            generic_error: Whether generic error occurred

        Returns:
            Fallback response text
        """
        base_response = f"**【{self.agent_type.capitalize()}】**\n\n"

        if timeout_occurred:
            base_response += (
                f"抱歉，我需要更多时间来深入思考您的问题。\n\n"
                f"基于您的问题「{agent_context.user_query}」，我的初步建议是：\n\n"
                f"1. 仔细考虑问题的各个方面\n"
                f"2. 权衡短期和长期影响\n"
                f"3. 寻求他人的意见\n"
            )
        elif connection_error:
            base_response += (
                f"抱歉，我目前无法连接到语言模型。\n\n"
                f"您的问题「{agent_context.user_query}」需要深入思考，"
                f"建议您稍后重试。\n"
            )
        else:
            base_response += (
                f"抱歉，我在处理您的问题时遇到了技术问题。\n\n"
                f"关于「{agent_context.user_query}」，建议您：\n"
                f"- 重新表述您的问题\n"
                f"- 确保相关笔记已正确加载\n"
                f"- 检查网络连接\n"
            )

        return base_response

    def _format_context_documents(self, documents: List[Dict[str, Any]]) -> str:
        """Format context documents for prompt."""
        if not documents:
            return "没有找到相关文档。"

        formatted = []
        for i, doc in enumerate(documents, 1):
            note_path = doc.get("note_path", "未知文件")
            excerpt = doc.get("excerpt", "无内容")
            similarity = doc.get("similarity_score", 0)

            formatted.append(f"""
文档 {i}（相似度: {similarity:.2f}，来源: {note_path}）：
{excerpt}
""")

        return "\n".join(formatted)


class ArchivistAgent(BaseAgentNode):
    """Agent 1: Extracts facts with mandatory citations."""

    def __init__(self):
        """Initialize archivist agent."""
        prompt_file = Path(__file__).parent / "prompts" / "archivist.txt"
        super().__init__("archivist", str(prompt_file))

    def process(self, agent_context: AgentContext) -> str:
        """Process query through archivist agent.

        Extracts objective facts from retrieved documents.
        """
        response = super().process(agent_context)

        # Add citation information if not present
        if "来自笔记" not in response and agent_context.context_documents:
            response += "\n\n*基于提供的文档内容进行分析*"

        return response


class StrategistAgent(BaseAgentNode):
    """Agent 2: ROI-focused analysis."""

    def __init__(self):
        """Initialize strategist agent."""
        prompt_file = Path(__file__).parent / "prompts" / "strategist.txt"
        super().__init__("strategist", str(prompt_file))

    def process(self, agent_context: AgentContext) -> str:
        """Process query through strategist agent.

        Analyzes options and alternatives with ROI lens.
        """
        return super().process(agent_context)


class CoachAgent(BaseAgentNode):
    """Agent 3: Empathetic reflection and synthesis."""

    def __init__(self):
        """Initialize coach agent."""
        prompt_file = Path(__file__).parent / "prompts" / "coach.txt"
        super().__init__("coach", str(prompt_file))

    def process(self, agent_context: AgentContext) -> str:
        """Process query through coach agent.

        Synthesizes insights and provides reflective guidance.
        """
        return super().process(agent_context)


def create_agent_nodes() -> Dict[str, BaseAgentNode]:
    """Create all three agent nodes.

    Returns:
        Dictionary of agent type to agent node
    """
    return {
        "archivist": ArchivistAgent(),
        "strategist": StrategistAgent(),
        "coach": CoachAgent(),
    }
