# Implementation Plan: Personal Board of Directors

**Branch**: `001-personal-board-app` | **Date**: 2025-11-26 | **Spec**: [Link to spec.md](spec.md)
**Input**: Feature specification from `/specs/001-personal-board-app/spec.md`

## Summary

Build a Personal Board of Directors MVP that enables users to receive balanced advice from a multi-agent system (Archivist, Strategist, Coach) based on their personal Obsidian notes. The system ingests markdown files, retrieves relevant context via semantic search, and orchestrates a sequential agent workflow to provide data-driven guidance with evidence citations.

## Technical Context

**Language/Version**: Python 3.10+ (use `python3` command, not `python`)
**Primary Dependencies**: Streamlit (UI), LangGraph (multi-agent orchestration), langchain-google-genai (LLM integration), ChromaDB (vector storage), Pydantic V2 (validation), uv (dependency management)
**Storage**: ChromaDB (local persistent mode) for vector storage, SQLite for conversation history (per clarified requirements)
**Testing**: pytest (unit), Integration tests for agent workflows (mandatory per constitution)
**Target Platform**: Desktop/Server (local deployment with local data processing)
**Project Type**: Single project (Monolithic Modular architecture per constitution)
**Performance Goals**: Advisory sessions complete in <2 minutes, search/retreival <3 seconds for 100+ files (from spec SC-001, SC-007)
**Constraints**: Local data processing (notes never transmitted), 60-second timeout per query, Gemini Flash as default LLM
**Scale/Scope**: MVP for single user with 100+ personal notes, no multi-tenant support

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Gate 1: Engineering Standards ✅ PASS
- Python 3.10+ enforced (use `python3` command)
- Type hints mandatory (Pydantic V2)
- Configuration via .env (12-Factor principles)

### Gate 2: Modern Tech Stack ✅ PASS
- Streamlit for frontend
- LangGraph for orchestration
- langchain-google-genai for LLM
- ChromaDB for vector storage
- Pydantic V2 for validation
- Library-level integrations (no custom RAG server)

### Gate 3: Monolithic Modular Architecture ✅ PASS
- Repository Pattern: data layer separate
- State Machine: LangGraph manages agent state
- Component-based UI: Streamlit components

### Gate 4: Stateless Data Operations ✅ PASS
- ChromaDB local persistent mode
- SQLite for conversation persistence (clarified)
- Vector embeddings reproducible with metadata

### Gate 5: Testing and Documentation ✅ PASS
- TDD encouraged
- Integration tests mandatory for agent workflows
- Mock external API calls
- Docstrings for public APIs

## Project Structure

### Documentation (this feature)

```text
specs/001-personal-board-app/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
│   └── api.yaml         # API contracts for data flow
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
# Single project structure per constitution Monolithic Modular pattern
.env.example                # Config template
pyproject.toml              # Dependencies (Poetry/Pip via uv)
uv.lock                     # Lock file for uv dependency management

src/
├── app.py                  # Streamlit Entrypoint
├── core/
│   ├── config.py           # Settings management (Pydantic)
│   └── state.py            # LangGraph State Definitions
├── data/
│   ├── loader.py           # Obsidian Markdown Parser
│   └── vector_store.py     # ChromaDB Client Wrapper
├── agents/
│   ├── prompts/            # Text files for System Prompts
│   │   ├── archivist.txt   # Archivist agent prompt
│   │   ├── strategist.txt  # Strategist agent prompt
│   │   └── coach.txt       # Coach agent prompt
│   ├── nodes.py            # Agent Function Nodes
│   └── graph.py            # LangGraph Graph Construction
└── utils/
    └── formatting.py       # UI Helpers

data/
└── obsidian_vault/         # (Gitignored) User data directory

tests/
├── contract/               # API contract tests
├── integration/            # Agent workflow tests
└── unit/                   # Unit tests
```

**Structure Decision**: Single project using Monolithic Modular architecture with clear separation of concerns: core (config/state), data (loader/vector), agents (prompts/nodes/graph), utils (helpers). This aligns with constitution requirements while enabling independent testing and maintainability.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations identified. All components align with constitution principles.
