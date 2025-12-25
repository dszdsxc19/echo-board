# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Echo-Board is a multi-agent AI advisory system that provides personalized life advice based on personal Obsidian notes. The system uses LangGraph for orchestration, ChromaDB for semantic search, and Streamlit for the UI.

### Core Architecture

```
User Query → Streamlit UI → LangGraph Workflow → Multi-Agent Response
                                  ↓
                          ChromaDB Vector Search
                                  ↓
                          Markdown Notes (Obsidian)
```

**Agent Workflow** (sequential execution via LangGraph):
1. **Archivist** - Extracts objective facts with citations
2. **Strategist** - Provides rational analysis and ROI evaluation
3. **Coach** - Offers empathetic guidance with reflective questions
4. **CFO** (new) - Financial analysis and reporting

The workflow is defined in `src/agents/graph.py:25-52` using StateGraph with a sequential chain.

## Development Commands

```bash
# Run the Streamlit app
streamlit run src/app.py

# Testing
pytest                           # Run all tests
pytest tests/unit/              # Unit tests only
pytest tests/integration/       # Integration tests only
pytest -k "test_name"           # Run specific test

# Linting and formatting
ruff check .                    # Lint (line-length: 88)
black .                         # Format (line-length: 88, target-version: py310)
mypy src/                       # Type check (strict mode)

# Dependency management (uv is used)
uv pip install -e .             # Install in editable mode
uv pip sync                     # Sync dependencies from lockfile
```

## Important Architecture Patterns

### LangGraph State Management

The entire workflow uses `AgentState` (TypedDict) defined in `src/core/state.py:9-38`:

```python
class AgentState(TypedDict):
    user_query: str
    query_type: str
    context_documents: List[Dict[str, Any]]
    archivist_response: Optional[str]
    strategist_response: Optional[str]
    coach_response: Optional[str]
    processing_times: Dict[str, float]
    tokens_used: Dict[str, int]
    errors: List[str]
    final_advice: Optional[str]
    session_id: Optional[str]
    conversation_history: Optional[List[str]]
    workflow_complete: bool
    timeout_occurred: bool
```

**Key pattern**: Each agent node receives the full state, updates its specific fields, and returns the modified state. The workflow is compiled and invoked asynchronously via `ainvoke()`.

### Agent Implementation Pattern

Agents are created via `create_agent_nodes()` in `src/agents/nodes.py`. Each agent:
1. Receives an `AgentContext` (Pydantic model with user_query, context_documents, agent_type)
2. Uses a prompt template from `src/agents/prompts/`
3. Returns a structured response string

When adding a new agent, you must:
1. Create the agent class in `src/agents/`
2. Add it to `create_agent_nodes()` in `src/agents/nodes.py`
3. Add a node in `_build_workflow()` in `src/agents/graph.py`
4. Add a corresponding state field in `AgentState`
5. Add a node handler method (e.g., `_cfo_node()`) in `AgentWorkflow`

### Multi-LLM Support

The LLM factory pattern in `src/infrastructure/llm_factory.py` supports multiple providers (OpenAI, Anthropic, Ollama). The provider is selected via the `LLM_PROVIDER` environment variable.

### Context Retrieval Flow

1. Notes are loaded from `NOTES_DIRECTORY` via `ObsidianLoader` (`src/infrastructure/obsidian_loader.py`)
2. Documents are chunked (configurable `CHUNK_SIZE`, `CHUNK_OVERLAP`)
3. Embeddings stored in ChromaDB at `VECTOR_STORE_PATH`
4. Query triggers semantic search returning `RETRIEVAL_TOP_K` documents
5. Results passed to all agents as `context_documents`

### Mem0 Long-Term Memory

User profiles and long-term memories are managed via `src/infrastructure/mem0_service.py`. This persists across sessions and is integrated into agent orchestration for personalized responses.

## Configuration

All configuration is centralized in `src/core/config.py` using Pydantic `BaseSettings`. Environment variables are loaded from `.env`:

```bash
# Required
OPEN_AI_API_KEY=xxx          # For OpenAI-compatible LLM
OPEN_AI_API_BASE=xxx         # API base URL
CHAT_MODEL=xxx               # Model name

# Optional
NOTES_DIRECTORY=./data/obsidian_vault
VECTOR_STORE_PATH=./data/chroma_db
RETRIEVAL_TOP_K=10
LLM_PROVIDER=openai          # or anthropic, ollama
LLM_TIMEOUT=60
```

## Code Style Requirements

- **Python**: 3.10+ required (use `python3` command, not `python`)
- **Type Checking**: Strict mypy mode enabled - all functions must have type hints
- **Line Length**: 88 characters (Black default)
- **Language**: Simplified Chinese for all UI strings and agent prompts
- **Validation**: Pydantic v2 for all data models

## Key File Locations

```
src/
├── app.py                    # Streamlit UI entry point
├── core/
│   ├── config.py            # Centralized configuration (Pydantic)
│   ├── state.py             # AgentState TypedDict + AgentContext model
│   └── models/              # Pydantic models (Note, Context, Conversation)
├── agents/
│   ├── archivist.py         # Fact extraction agent
│   ├── strategist.py        # Analysis/ROI agent
│   ├── coach.py             # Empathetic guidance agent
│   ├── cfo.py               # Financial analysis agent
│   ├── orchestrator.py      # Main workflow orchestration
│   ├── graph.py             # LangGraph workflow definition
│   ├── nodes.py             # Agent node factory
│   └── prompts/             # Agent prompt templates (Chinese)
├── infrastructure/
│   ├── vector_store.py      # ChromaDB wrapper
│   ├── llm_factory.py       # LLM provider factory
│   ├── obsidian_loader.py   # Markdown note processing
│   └── mem0_service.py      # Mem0 long-term memory service
└── main_test*.py            # Development test scripts
```

## Testing Approach

- **Contract tests** (`tests/contract/`) - Verify agent outputs match expected structure
- **Integration tests** (`tests/integration/`) - Test full agent workflows with real LLM calls
- **Unit tests** (`tests/unit/`) - Isolated component tests

Tests use `pytest-asyncio` for async workflow testing.

## Common Tasks

### Adding a New Agent

1. Create agent class in `src/agents/agent_name.py`
2. Add prompt template in `src/agents/prompts/agent_name.txt`
3. Register in `create_agent_nodes()` (`src/agents/nodes.py`)
4. Add node and edge in `_build_workflow()` (`src/agents/graph.py`)
5. Add state field in `AgentState` (`src/core/state.py`)
6. Add node handler method in `AgentWorkflow` class

### Debugging Agent Output

Agent outputs include emoji prefixes for easy identification in console logs:
- 📚 Archivist
- 💡 Strategist
- 🎯 Coach
- 💰 CFO

Check `processing_times` in state for performance profiling.

### Vector Store Issues

If retrieval fails: delete `data/chroma_db` and reload notes. The vector store is automatically recreated on startup.
