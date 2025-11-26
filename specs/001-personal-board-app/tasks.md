# Tasks: Personal Board of Directors

**Input**: Design documents from `/specs/001-personal-board-app/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/
**Tests**: Tests are OPTIONAL - only included where explicitly requested or for critical workflows

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- All paths assume project structure from plan.md

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create project structure per implementation plan
- [ ] T002 Initialize Python project with uv and pyproject.toml
- [ ] T003 [P] Create .env.example with all configuration variables
- [ ] T004 [P] Setup core directories (src/, data/, tests/)
- [ ] T005 [P] Configure development dependencies and tooling (pytest, black, mypy)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T006 Create Pydantic models for data entities in src/core/models/
- [ ] T007 [P] Implement configuration management in src/core/config.py
- [ ] T008 [P] Define LangGraph state schema in src/core/state.py
- [ ] T009 Create data directory structure (chroma_db, conversations.db)
- [ ] T010 Initialize ChromaDB vector store and SQLite database
- [ ] T011 Create .gitignore to exclude data/, .env, and __pycache__

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Seek Life Decision Guidance (Priority: P1) 🎯 MVP

**Goal**: Complete advisory session where user asks a question, system retrieves notes, runs through three agents, and returns balanced advice with expandable evidence

**Independent Test**: Can be fully tested by providing test note directory and asking a single question. User receives advice from all three agents (Archivist, Strategist, Coach) and can expand to see evidence.

### Implementation for User Story 1

- [ ] T012 [P] [US1] Implement Note model and parser in src/data/loader.py
- [ ] T013 [P] [US1] Create NoteChunk model with chunking logic (1000 words, 200 overlap)
- [ ] T014 [P] [US1] Implement VectorStore with ChromaDB integration in src/data/vector_store.py
- [ ] T015 [US1] Create agent prompt templates in src/agents/prompts/ (archivist.txt, strategist.txt, coach.txt)
- [ ] T016 [US1] Implement three agent nodes in src/agents/nodes.py
- [ ] T017 [US1] Build LangGraph workflow orchestration in src/agents/graph.py
- [ ] T018 [US1] Create main Streamlit UI in src/app.py with chat interface
- [ ] T019 [US1] Implement evidence display component (hidden by default per FR-005)
- [ ] T020 [US1] Add loading states and progress indicators per agent
- [ ] T021 [US1] Integrate note loading, vector search, and agent workflow
- [ ] T022 [US1] Implement error handling for no relevant notes found (per FR-010)

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Continue Prior Advisory Session (Priority: P2)

**Goal**: Maintain conversation history across sessions and enable meaningful follow-up questions

**Independent Test**: Can be tested by asking a follow-up question to a previous advisory session. System should reference prior conversation and maintain coherent context.

### Implementation for User Story 2

- [ ] T023 [P] [US2] Create SQLite models for ConversationSession and AgentResponse
- [ ] T024 [US2] Implement ConversationStore class for session persistence
- [ ] T025 [US2] Add conversation history tracking to LangGraph state
- [ ] T026 [US2] Update UI to display conversation history sidebar
- [ ] T027 [US2] Implement session retrieval and context injection
- [ ] T028 [US2] Add conversation history pagination (20 sessions per page)
- [ ] T029 [US2] Update agent workflow to include conversation context
- [ ] T030 [US2] Test follow-up question context maintenance

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Configure Personal Data Source (Priority: P3)

**Goal**: Allow users to configure or change their notes directory with validation and re-indexing

**Independent Test**: Can be tested by configuring a directory path and verifying the system successfully ingests notes from that location.

### Implementation for User Story 3

- [ ] T031 [P] [US3] Create directory configuration UI in settings panel
- [ ] T032 [US3] Implement directory validation (exists, readable, has .md files)
- [ ] T033 [US3] Add incremental re-indexing logic (track file modification times)
- [ ] T034 [US3] Create "Force Re-index All Notes" functionality
- [ ] T035 [US3] Implement file change detection and selective update
- [ ] T036 [US3] Add progress tracking for note indexing
- [ ] T037 [US3] Handle edge cases (malformed frontmatter, non-md files)
- [ ] T038 [US3] Test directory switching and re-indexing

**Checkpoint**: All user stories should now be independently functional

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T039 [P] Add comprehensive error handling for all LLM operations
- [ ] T040 [P] Implement graceful degradation with 60-second timeout (per FR-011)
- [ ] T041 [P] Create logging infrastructure for debugging
- [ ] T042 Add integration tests for three-agent workflow
- [ ] T043 Add performance monitoring (advisory session time, search time)
- [ ] T044 Create comprehensive README.md with setup instructions
- [ ] T045 Add data validation checkpoints throughout workflow
- [ ] T046 Implement agent response formatting and UI improvements
- [ ] T047 Add API key validation and user feedback
- [ ] T048 Final testing and bug fixes

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phases 3-5)**: All depend on Foundational phase completion
  - User stories can proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - May integrate with US1 but should be independently testable
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - May integrate with US1/US2 but should be independently testable

### Within Each User Story

- Models before services
- Services before endpoints
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Models within a story marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: User Story 1

```bash
# Launch all models for User Story 1 together:
Task: "Implement Note model and parser in src/data/loader.py"
Task: "Create NoteChunk model with chunking logic"
Task: "Implement VectorStore with ChromaDB integration"

# Launch all agent implementation together:
Task: "Create agent prompt templates"
Task: "Implement three agent nodes"
Task: "Build LangGraph workflow orchestration"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 3 → Test independently → Deploy/Demo
5. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1
   - Developer B: User Story 2
   - Developer C: User Story 3
3. Stories complete and integrate independently

---

## Key Technologies and Implementation Notes

### Core Components

- **Streamlit UI**: src/app.py (single-page application)
- **LangGraph State**: src/core/state.py (Define agent state schema)
- **Note Loader**: src/data/loader.py (Parse Obsidian markdown)
- **Vector Store**: src/data/vector_store.py (ChromaDB integration)
- **Agent Nodes**: src/agents/nodes.py (Three agent implementations)
- **Agent Workflow**: src/agents/graph.py (LangGraph orchestration)

### Critical Requirements

- **top-k=10** for retrieval (FR-014)
- **1000-word chunks** with 200-word overlap (FR-014)
- **SQLite** for conversation persistence (FR-012)
- **60-second timeout** with graceful degradation (FR-011)
- **Evidence hidden by default** (FR-005)
- **Gemini Flash** as default LLM (FR-015)
- **Local data processing** (FR-007)

### Testing Strategy

- **Unit tests**: For individual components (NoteLoader, VectorStore, Agent nodes)
- **Integration tests**: For complete three-agent workflow
- **Contract tests**: For API interfaces between components
- **Mock external APIs**: LLM calls mocked in unit tests
- **Performance tests**: Verify <2 min session time, <3 sec search

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
