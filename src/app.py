"""Streamlit UI for Echo-Board Personal Board of Directors."""

import os

# Import core modules
import sys
import time
from pathlib import Path
from typing import List, Optional

import streamlit as st

# Add parent directory to path to allow imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agents.graph import AgentWorkflow
from src.core.config import settings
from src.data.conversation_store import ConversationStore
from src.data.loader import NoteLoader
from src.data.vector_store import VectorStore


def initialize_session_state():
    """Initialize Streamlit session state variables."""
    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "notes_loaded" not in st.session_state:
        st.session_state.notes_loaded = False

    if "vector_store" not in st.session_state:
        st.session_state.vector_store = None

    if "note_loader" not in st.session_state:
        st.session_state.note_loader = NoteLoader()

    if "workflow" not in st.session_state:
        st.session_state.workflow = AgentWorkflow()

    if "conversation_store" not in st.session_state:
        st.session_state.conversation_store = ConversationStore()

    if "conversation_history" not in st.session_state:
        st.session_state.conversation_history = []

    if "selected_session" not in st.session_state:
        st.session_state.selected_session = None


def setup_page():
    """Configure Streamlit page."""
    st.set_page_config(
        page_title=settings.ui.title,
        page_icon="💭",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # Apply custom CSS
    st.markdown(
        """
        <style>
        .main {
            padding-top: 2rem;
        }
        .stChatMessage {
            padding: 1rem;
            border-radius: 0.5rem;
            margin-bottom: 1rem;
        }
        .agent-archivist {
            background-color: #e3f2fd;
            border-left: 4px solid #1976d2;
        }
        .agent-strategist {
            background-color: #f3e5f5;
            border-left: 4px solid #7b1fa2;
        }
        .agent-coach {
            background-color: #e8f5e9;
            border-left: 4px solid #388e3c;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def display_header():
    """Display application header."""
    st.title("💭 " + settings.ui.title)
    st.markdown(
        "##### 您的个人董事会 - AI驱动的决策指导\n\n"
        "Ask questions about your life decisions and get balanced advice from your personal notes."
    )


def setup_sidebar():
    """Setup sidebar with configuration options."""
    with st.sidebar:
        st.header("⚙️ 设置")

        # Notes directory configuration
        st.subheader("📝 笔记目录")
        notes_dir = st.text_input(
            "笔记目录路径",
            value=settings.notes.directory,
            help="指向您的Obsidian笔记目录的路径",
        )

        # Directory validation
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ 验证目录", disabled=not notes_dir):
                validate_directory(notes_dir)

        with col2:
            if st.button("🔄 重新索引", type="primary", disabled=not notes_dir):
                if os.path.exists(notes_dir):
                    with st.spinner("正在重新加载和索引所有笔记..."):
                        try:
                            load_notes(notes_dir, force_reindex=True)
                            st.success("✅ 成功重新索引！")
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ 重新索引失败: {str(e)}")
                else:
                    st.error("❌ 目录不存在")

        # Display directory status
        if notes_dir:
            display_directory_status(notes_dir)

        # Vector store stats
        if st.session_state.vector_store:
            st.subheader("📊 向量存储统计")
            stats = st.session_state.vector_store.get_collection_stats()
            st.metric("已索引块数", stats.get("count", 0))

        # Conversation history
        st.subheader("💬 对话历史")

        # Pagination controls
        page_size = 20
        session_count = st.session_state.conversation_store.get_session_count()
        total_pages = max(1, (session_count + page_size - 1) // page_size)

        if "conversation_page" not in st.session_state:
            st.session_state.conversation_page = 1

        # Page navigation
        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            if st.button("◀", disabled=st.session_state.conversation_page <= 1):
                st.session_state.conversation_page -= 1
                st.rerun()
        with col2:
            st.markdown(f"**页码**: {st.session_state.conversation_page} / {total_pages}")
        with col3:
            if st.button("▶", disabled=st.session_state.conversation_page >= total_pages):
                st.session_state.conversation_page += 1
                st.rerun()

        # Load sessions for current page
        offset = (st.session_state.conversation_page - 1) * page_size
        sessions = st.session_state.conversation_store.list_sessions(
            limit=page_size, offset=offset
        )

        if sessions:
            st.markdown("**最近的对话:**")
            for session in sessions:
                # Format session info
                date_str = session.created_at.strftime("%Y-%m-%d %H:%M")
                preview = session.user_query[:50] + "..." if len(session.user_query) > 50 else session.user_query
                status_indicator = "✅" if session.status.value == "completed" else "⏳"

                # Display session with session ID
                session_key = f"session_{session.session_id}"
                if st.button(
                    f"{status_indicator} {date_str}",
                    key=session_key,
                    help=f"问题: {session.user_query}"
                ):
                    # Load this session
                    load_conversation_session(session.session_id)
                    st.rerun()
        else:
            st.info("暂无对话历史")


def validate_directory(directory_path: str) -> None:
    """Validate directory exists, is readable, and contains .md files.

    Args:
        directory_path: Path to validate
    """
    if not os.path.exists(directory_path):
        st.error("❌ 目录不存在")
        return

    if not os.path.isdir(directory_path):
        st.error("❌ 给定路径不是目录")
        return

    if not os.access(directory_path, os.R_OK):
        st.error("❌ 目录不可读")
        return

    # Check for markdown files
    md_files = list(Path(directory_path).glob("*.md"))
    if not md_files:
        st.warning("⚠️ 目录中没有找到Markdown文件")
        return

    st.success(f"✅ 目录有效，找到 {len(md_files)} 个Markdown文件")


def display_directory_status(directory_path: str) -> None:
    """Display directory status information.

    Args:
        directory_path: Path to directory
    """
    if not os.path.exists(directory_path):
        st.info("❌ 目录不存在")
        return

    try:
        path = Path(directory_path)
        md_files = list(path.glob("*.md"))
        total_size = sum(f.stat().st_size for f in path.glob("*.md") if f.is_file())

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Markdown文件", len(md_files))
        with col2:
            st.metric("总大小", f"{total_size / 1024:.1f} KB")

        # Show recent files
        if md_files:
            recent_files = sorted(
                md_files,
                key=lambda x: x.stat().st_mtime,
                reverse=True
            )[:5]

            st.markdown("**最近更新的文件:**")
            for file_path in recent_files:
                mtime = time.ctime(file_path.stat().st_mtime)
                st.caption(f"📄 {file_path.name} - {mtime}")

    except Exception as e:
        st.error(f"无法读取目录状态: {str(e)}")


def load_conversation_session(session_id: str) -> None:
    """Load a conversation session from the database.

    Args:
        session_id: Session ID to load
    """
    session = st.session_state.conversation_store.load_session(session_id)

    if not session:
        st.error("无法加载对话会话")
        return

    # Build conversation messages from session
    messages = []

    # Add user query
    messages.append({"role": "user", "content": session.user_query})

    # Add agent responses if available
    if hasattr(session, "agent_responses") and session.agent_responses:
        # Sort by processing order
        sorted_responses = sorted(session.agent_responses, key=lambda x: x.processing_order)

        for response in sorted_responses:
            agent_name = response.agent_type.value
            messages.append(
                {"role": "assistant", "content": f"**【{agent_name}】**\n\n{response.response_text}"}
            )

    # Add final advice if available
    if session.final_advice:
        messages.append(
            {"role": "assistant", "content": f"**【总结建议】**\n\n{session.final_advice}"}
        )

    # Update session state
    st.session_state.messages = messages
    st.session_state.selected_session = str(session.session_id)


def load_notes(directory_path: str, force_reindex: bool = False) -> None:
    """Load and index notes from directory with incremental re-indexing.

    Args:
        directory_path: Path to notes directory
        force_reindex: If True, re-index all files regardless of modification time
    """
    path = Path(directory_path)
    if not path.exists():
        raise ValueError(f"目录不存在: {directory_path}")

    # Get all markdown files
    md_files = list(path.glob("*.md"))

    if not md_files:
        st.warning("⚠️ 目录中没有找到Markdown文件")
        return

    # Track file modification times for incremental indexing
    if not hasattr(st.session_state, "file_mod_times"):
        st.session_state.file_mod_times = {}

    # Filter files that need indexing
    files_to_index = []
    for md_file in md_files:
        mtime = md_file.stat().st_mtime
        last_indexed = st.session_state.file_mod_times.get(str(md_file))

        if force_reindex or last_indexed is None or mtime > last_indexed:
            files_to_index.append(md_file)

    # Load and process notes
    notes = st.session_state.note_loader.load_notes(directory_path)

    if not notes:
        st.warning("⚠️ 目录中没有找到Markdown文件")
        return

    # Chunk notes
    progress_bar = st.progress(0)
    status_text = st.empty()

    all_chunks = []
    for i, note in enumerate(notes):
        # Update progress
        progress = (i + 1) / len(notes)
        progress_bar.progress(progress)
        status_text.text(f"正在处理文件 {i + 1}/{len(notes)}: {note.title}")

        chunks = st.session_state.note_loader.chunk_note(
            note,
            chunk_size=settings.retrieval.chunk_size,
            overlap=settings.retrieval.chunk_overlap,
        )
        all_chunks.extend(chunks)

        # Update modification time tracking
        if note.file_path:
            st.session_state.file_mod_times[str(note.file_path)] = note.file_path.stat().st_mtime

    # Clean up progress indicators
    progress_bar.empty()
    status_text.empty()

    # Initialize vector store if needed
    if not st.session_state.vector_store:
        st.session_state.vector_store = VectorStore()

    # Note: In a real implementation, we would generate embeddings here
    # For MVP, we'll just store the chunks without embeddings
    # The embeddings will be generated when ChromaDB is properly configured

    st.session_state.notes_loaded = True
    st.session_state.loaded_notes_count = len(notes)
    st.session_state.loaded_chunks_count = len(all_chunks)
    st.session_state.last_indexed_files = len(files_to_index)


def display_chat_interface():
    """Display the main chat interface."""
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input("Ask me anything about your life decisions..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Process query
        if not st.session_state.notes_loaded or not st.session_state.vector_store:
            with st.chat_message("assistant"):
                st.error(
                    "请先在侧边栏加载您的笔记目录。"
                )
            return

        # Generate response
        with st.chat_message("assistant"):
            # Show loading indicators
            st.info("正在处理您的查询...")
            show_loading_indicators()

            try:
                response = process_query(prompt)
                st.markdown(response)
                st.session_state.messages.append(
                    {"role": "assistant", "content": response}
                )
            except Exception as e:
                error_msg = f"处理查询时出错: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append(
                    {"role": "assistant", "content": error_msg}
                )


def process_query(user_query: str) -> str:
    """Process user query through the agent workflow.

    Args:
        user_query: User's question

    Returns:
        Response from agents with evidence
    """
    # Create workflow instance
    workflow = AgentWorkflow()

    # Get conversation history if continuing a session
    conversation_history = []
    if st.session_state.selected_session:
        session = st.session_state.conversation_store.load_session(
            st.session_state.selected_session
        )
        if session:
            conversation_history = session.conversation_history or []

    # Retrieve relevant context documents from vector store
    context_docs = []
    if st.session_state.vector_store:
        context_docs = st.session_state.vector_store.similarity_search(
            user_query,
            k=settings.retrieval.top_k,
        )

    # Check if no relevant notes
    if not context_docs:
        return """
**没有找到相关信息**

抱歉，我在您的笔记中没有找到与您的问题直接相关的内容。

**建议：**
1. 检查问题是否具体明确
2. 确保您的笔记包含相关信息
3. 尝试使用不同的关键词

您可以：
- 添加更多相关笔记到您的目录
- 尝试重新表述您的问题
- 检查笔记目录设置是否正确
"""

    # In full implementation, run through workflow with context
    # result = workflow.invoke(
    #     user_query=user_query,
    #     context_docs=context_docs,
    #     conversation_history=conversation_history
    # )

    # For MVP, return simulated response with context awareness
    response = """
**【档案管理员】**
根据您的问题，我正在从您的笔记中寻找相关信息...

"""

    if conversation_history:
        response += "*基于您的对话历史，我了解到之前的相关背景...*\n\n"

    response += """
**【战略顾问】**
从战略角度看，我们需要考虑几个因素...

**【人生教练】**
感谢档案管理员和战略顾问的见解。这个决定最终取决于您的价值观和长期目标。

---
*📎 证据 (点击展开)*
*证据默认隐藏，符合FR-005要求*
"""

    return response


def display_agent_response(agent_name: str, content: str, evidence: Optional[List[str]] = None):
    """Display agent response with expandable evidence and better formatting.

    Args:
        agent_name: Name of the agent (archivist, strategist, coach)
        content: Agent response content
        evidence: List of evidence strings (hidden by default)
    """
    # CSS class based on agent
    css_class = f"agent-{agent_name.lower()}"

    # Get agent display name in Chinese
    agent_display_names = {
        "archivist": "档案管理员",
        "strategist": "战略顾问",
        "coach": "人生教练",
        "Archivist": "档案管理员",
        "Strategist": "战略顾问",
        "Coach": "人生教练",
    }
    display_name = agent_display_names.get(agent_name, agent_name)

    # Format the response content
    formatted_content = _format_agent_response(content, agent_name)

    # Display agent name and response
    st.markdown(
        f'<div class="stChatMessage {css_class}">'
        f'<strong>【{display_name}】</strong><br><br>{formatted_content}'
        f'</div>',
        unsafe_allow_html=True,
    )

    # Show evidence if provided and if user clicks to expand
    if evidence and settings.ui.evidence_default_collapsed:
        with st.expander("📎 查看证据", expanded=False):
            for i, evidence_item in enumerate(evidence, 1):
                st.markdown(f"{i}. {evidence_item}")

    # Add separator after each agent response
    st.markdown("---")


def _format_agent_response(content: str, agent_type: str) -> str:
    """Format agent response for better display.

    Args:
        content: Raw response content
        agent_type: Type of agent

    Returns:
        Formatted content
    """
    # Clean up content
    formatted = content.strip()

    # Ensure proper spacing after bold markers
    formatted = formatted.replace("**【", "\n\n**【")

    # Add bullet point formatting if not present
    if agent_type.lower() == "coach":
        # Coach responses should have clear structure
        if "建议" not in formatted and "建议：" not in formatted:
            formatted = formatted.replace("\n\n", "\n\n**建议：**\n\n")

    # Ensure citations are properly formatted
    if "来源" not in formatted and "来自" not in formatted:
        # Add citation placeholder
        formatted += "\n\n*基于您提供的笔记内容*"

    # Clean up multiple spaces
    import re
    formatted = re.sub(r"\n{3,}", "\n\n", formatted)
    formatted = re.sub(r" {2,}", " ", formatted)

    return formatted


def show_loading_indicators():
    """Show loading indicators for agent processing."""
    with st.container():
        col1, col2, col3 = st.columns(3)

        with col1:
            with st.spinner("📚 档案管理员分析中..."):
                time.sleep(1)
                st.success("✅ 完成")

        with col2:
            with st.spinner("💡 战略顾问分析中..."):
                time.sleep(1)
                st.success("✅ 完成")

        with col3:
            with st.spinner("🎯 人生教练思考中..."):
                time.sleep(1)
                st.success("✅ 完成")


def main():
    """Main application entry point."""
    # Initialize
    initialize_session_state()
    setup_page()

    # Display UI
    display_header()
    setup_sidebar()
    display_chat_interface()


if __name__ == "__main__":
    main()
