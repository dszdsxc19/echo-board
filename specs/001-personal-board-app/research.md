# Research: Personal Board of Directors Implementation

**Date**: 2025-11-26
**Feature**: Personal Board of Directors
**Phase**: 0 - Research & Unknown Resolution

## Research Tasks

### 1. LangGraph Multi-Agent Orchestration Best Practices

**Decision**: Use LangGraph's StateGraph pattern with typed state definitions for sequential agent workflow

**Rationale**: LangGraph provides native state management for multi-agent systems. StateGraph allows defining nodes (agents) and edges (workflow) with type-safe state passing between agents. This is ideal for our sequential User → Archivist → Strategist → Coach → User workflow.

**Alternatives Considered**:
- Direct LangChain chains: Less state management, harder to maintain conversation context
- Custom state machine: More code to maintain, less robust than proven framework
- Sequential agent library: Less mature ecosystem compared to LangGraph

**Implementation Approach**:
- Define state schema with: user_query, context_docs, archivist_response, strategist_response, coach_response, conversation_history
- Create three agent nodes: archivist_node, strategist_node, coach_node
- Connect with sequential edges: user_query → archivist → strategist → coach → output
- Use state persistence for conversation history across sessions

---

### 2. ChromaDB + langchain-google-genai Integration

**Decision**: Use ChromaDB as vector store with langchain-google-genai embeddings via Chroma client wrapper

**Rationale**: ChromaDB offers persistent local storage compatible with LangChain. langchain-google-genai provides unified interface for both embeddings and chat completions. This combination meets the constitution's library-level integration requirement.

**Alternatives Considered**:
- FAISS for vector storage: Requires more boilerplate, less persistence features
- Qdrant: Overkill for single-user MVP, adds complexity
- Pinecone/Weaviate: External services violate local data requirement

**Implementation Approach**:
- Initialize ChromaDB client in local persistent mode
- Create Chroma collection per note ingestion
- Use Gemini Flash for both embeddings and chat completions
- Implement top-k=10 retrieval with similarity threshold
- Store document metadata (file path, date, tags) for citations

---

### 3. Streamlit + LangGraph State Management

**Decision**: Store LangGraph state in Streamlit session state with conversation history in SQLite

**Rationale**: Streamlit provides session_state for runtime persistence. SQLite offers reliable cross-session storage. This separates runtime state (current workflow) from persistent storage (conversation history).

**Alternatives Considered**:
- In-memory only: Loses context on app restart
- File-based JSON: Less structured, harder to query
- Dedicated database server: Overkill for MVP

**Implementation Approach**:
- Initialize LangGraph state in st.session_state on first run
- Serialize state to SQLite on workflow completion
- Load conversation history from SQLite on app start
- Maintain conversation_summary in session_state for follow-up context
- Use Pydantic models for type-safe state serialization

---

### 4. Obsidian Markdown Frontmatter Parsing

**Decision**: Use python-frontmatter library for parsing, implement custom validation

**Rationale**: python-frontmatter is a mature library specifically designed for Jekyll/Obsidian frontmatter. It's well-tested and handles edge cases (malformed YAML, missing frontmatter, etc.).

**Alternatives Considered**:
- Manual regex parsing: Fragile, error-prone
- PyYAML direct parsing: Doesn't handle delimiter stripping
- markdown-it plugins: Adds unnecessary processing overhead

**Implementation Approach**:
- Use python-frontmatter.load() to parse markdown files
- Extract frontmatter dict: date, tags, title, other metadata
- Validate required fields (date) with Pydantic models
- Handle malformed frontmatter gracefully with warnings
- Preserve raw content for embedding generation

---

### 5. Incremental Re-indexing Strategy

**Decision**: Track file modification times, maintain change log, re-index only modified files

**Rationale**: Efficient updates are critical for usability. File modification timestamps provide reliable change detection without expensive full re-indexing. This aligns with the clarified requirement for intelligent incremental indexing.

**Alternatives Considered**:
- Hash-based change detection: More accurate but slower
- Watchdog polling: Real-time but complex, overkill for MVP
- Manual trigger only: Poor UX, requires user action

**Implementation Approach**:
- Store file path + modification timestamp in metadata DB
- On note load, check if modification time > stored time
- Only re-embed changed files
- Update timestamp after successful re-indexing
- Batch operations for efficiency (re-index up to N files per query)

---

### 6. Agent Prompt Engineering Strategy

**Decision**: Store prompts in text files, implement role-specific templates with evidence requirements

**Rationale**: Separating prompts from code enables iteration without deployment. Role-specific prompts ensure consistent agent behavior. Evidence requirement baked into prompts for citation compliance.

**Alternatives Considered**:
- Inline prompts: Harder to iterate, mixes logic and content
- Database storage: Overkill for MVP
- Hardcoded templates: Less flexible for tuning

**Implementation Approach**:
- Create separate .txt files for each agent: archivist.txt, strategist.txt, coach.txt
- Include context retrieval instructions and evidence citation requirements
- Pass retrieved documents as context to each agent
- Format responses with clear role attribution for UI display

---

## Technology Stack Validation

All selected technologies align with Echo-Board Constitution:

✅ **Engineering Standards**: Python 3.10+, Pydantic V2 for validation
✅ **Modern Tech Stack**: Streamlit, LangGraph, langchain-google-genai, ChromaDB
✅ **Monolithic Modular**: Clear separation: core/data/agents/utils
✅ **Local Processing**: ChromaDB local mode, SQLite for persistence
✅ **Library-level integrations**: No custom RAG server

## Unknowns Resolved

All technical decisions made. No NEEDS CLARIFICATION markers remain in technical context.

## Integration Patterns

1. **Data Flow**: Notes → Loader → Vector Store → Retriever → Agents → UI
2. **State Flow**: User Query → LangGraph State → Sequential Agents → Response
3. **Persistence**: Runtime State (session_state) + History (SQLite)
4. **Configuration**: Pydantic models + .env file

## Next Steps

Ready for Phase 1: Design & Contracts
- Generate data model (entities from spec)
- Create API contracts for data flow
- Document setup process in quickstart.md
