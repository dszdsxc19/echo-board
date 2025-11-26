# Feature Specification: Personal Board of Directors

**Feature Branch**: `001-personal-board-app`
**Created**: 2025-11-26
**Status**: Draft
**Input**: User description: "Build a 'Personal Board of Directors' MVP application where a user interacts with a multi-agent system to review past personal data (Obsidian notes) and receive balanced advice for future decisions."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Seek Life Decision Guidance (Priority: P1) 🎯 MVP

The user asks a personal question about career, relationships, or life goals. The system retrieves relevant notes from their personal data, runs them through three specialized agents (Archivist for facts, Strategist for analysis, Coach for reflection), and provides balanced, data-driven advice. The user can expand to see source evidence.

**Why this priority**: This is the core value proposition - the complete advisory session from question to answer. Without this, the system provides no value. This delivers immediate benefit to users seeking guidance.

**Independent Test**: Can be fully tested by providing a test note directory and asking a single question. User receives advice from all three agents and can verify the response is relevant to their question.

**Acceptance Scenarios**:

1. **Given** user has notes in their directory, **When** user asks "Should I accept the job offer in Tokyo?", **Then** system retrieves relevant notes about career goals, location preferences, and family considerations; Archivist provides facts; Strategist provides analysis; Coach provides reflection; User receives balanced advice.
2. **Given** user asks a vague question, **When** system processes the query through the three-agent workflow, **Then** each agent contributes appropriately to shape a useful response with relevant context from personal notes.
3. **Given** user wants to see evidence, **When** they expand the evidence section, **Then** they can see specific note excerpts that informed each agent's response.
4. **Given** user asks a question with no relevant notes, **When** the system processes the query, **Then** it returns a clear message that insufficient personal data exists to provide informed advice and suggests adding more relevant notes.

---

### User Story 2 - Continue Prior Advisory Session (Priority: P2)

The user returns to review their previous conversation or ask a follow-up question. The system retrieves the prior conversation history and maintains context, allowing for iterative exploration of a topic or reviewing previous advice.

**Why this priority**: Real decision-making is iterative. Users need to ask follow-up questions, explore alternatives, and reflect on advice. This significantly improves user experience and makes the system truly useful for ongoing life decisions.

**Independent Test**: Can be tested by asking a follow-up question to a previous advisory session. System should reference the prior conversation and maintain coherent context.

**Acceptance Scenarios**:

1. **Given** user had an advisory session yesterday, **When** they return and ask a follow-up question, **Then** system retrieves the previous conversation and maintains context across sessions.
2. **Given** user wants to revisit advice, **When** they request to see past sessions, **Then** they can view their complete conversation history.
3. **Given** user asks an ambiguous follow-up, **When** system interprets the question, **Then** it uses the prior conversation context to provide relevant, coherent responses.

---

### User Story 3 - Configure Personal Data Source (Priority: P3)

The user sets up or changes the directory location where their personal notes are stored. System validates the directory, ingests available notes, and prepares the knowledge base for advisory sessions.

**Why this priority**: While the system can ship with a default directory, users need the ability to point it to their actual Obsidian vault. This enables real usage but can be deferred until after the core advisory workflow is proven.

**Independent Test**: Can be tested by configuring a directory path and verifying the system successfully ingests notes from that location.

**Acceptance Scenarios**:

1. **Given** user is setting up the system for the first time, **When** they provide a directory path to their notes, **Then** system validates the directory and ingests all markdown files.
2. **Given** user provides an invalid directory, **When** system attempts to process it, **Then** it displays a clear error message explaining the issue.
3. **Given** user has no notes in their directory, **When** system attempts to ingest, **Then** it provides helpful guidance on how to add notes for better advice.

---

### Edge Cases

- What happens when the directory contains non-markdown files?
- How does the system handle markdown files with malformed frontmatter?
- What occurs when an LLM inference call fails during the agent workflow?
- How does the system behave when all three agents disagree significantly?
- What happens if the user asks a question in the middle of an active agent workflow?

## Clarifications

### Session 2025-11-26

- Q: When an LLM inference call fails during multi-agent workflow, how should the system handle it? → A: Specify maximum processing time (e.g., 60 seconds), provide fast degraded response based on partial responses if timeout occurs
- Q: How should conversation history persist between sessions? → A: Store conversation history as SQLite database locally on user device
- Q: When users add or modify notes, how should the knowledge base update? → A: Intelligent incremental re-indexing (track file modification times, only re-index changed files)
- Q: How should the semantic retrieval top-k parameter and chunking strategy be configured? → A: Dynamic adjustment: top-k=10 (relevance-based), chunk size=1000 words, 200-word overlap
- Q: For external LLM service choice, what approach should the system take? → A: Pluggable architecture, default to Gemini Flash, simplified configuration

### Added Requirements

- **FR-011**: System MUST implement graceful degradation for agent failures with a maximum processing time of 60 seconds per query, providing responses based on available partial agent outputs when timeouts occur
- **FR-012**: System MUST persist conversation history across sessions using SQLite database stored locally on the user's device
- **FR-013**: System MUST implement intelligent incremental re-indexing to update the knowledge base when notes are added or modified, tracking file modification timestamps to re-index only changed files
- **FR-014**: System MUST implement dynamic retrieval configuration with top-k=10 for relevance-based filtering, chunk size=1000 words, and 200-word overlap for contextual continuity
- **FR-015**: System MUST support pluggable LLM architecture with Gemini Flash as default provider, allowing simplified configuration and future extensibility
- **FR-016**: System MUST display all user-facing UI elements and Agent outputs in Simplified Chinese, as per project constitution requirements

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST parse all Markdown files (.md) from the configured local directory, extracting frontmatter metadata (including date) and content body
- **FR-002**: System MUST retrieve top-k relevant content chunks based on semantic similarity between user query and note content
- **FR-003**: System MUST process user queries through a sequential agent workflow: User → Archivist (extracts facts with citations) → Strategist (analyzes ROI/alternatives) → Coach (reflects/synthesizes) → User
- **FR-004**: System MUST display agent responses in the UI with clear attribution to each agent role (Archivist, Strategist, Coach)
- **FR-005**: System MUST hide evidence (source note excerpts) by default in expandable/collapsible UI components, showing only when explicitly requested by the user
- **FR-006**: System MUST preserve conversation context within active runtime sessions, allowing users to ask follow-up questions with full context maintained
- **FR-007**: System MUST operate with local data processing, ensuring user personal notes remain on their device (LLM inference calls may be external)
- **FR-008**: System MUST optimize agent turn-around time through parallel processing where feasible (sequential processing acceptable for MVP)
- **FR-009**: System MUST provide clear user feedback during processing (loading states, progress indicators) for each agent in the workflow
- **FR-010**: System MUST handle cases where insufficient relevant notes exist and provide actionable guidance to users

### Key Entities

- **User**: The individual seeking advice; owns the personal notes and asks questions
- **Note**: Individual markdown files containing personal data; includes frontmatter (date, tags, metadata) and content; serves as the knowledge base
- **Conversation Session**: A discrete advisory interaction including user query, all agent responses, and evidence; maintains state for follow-up questions
- **Agent Response**: The output from each of the three agents (Archivist, Strategist, Coach); includes response text and associated evidence/citations
- **Query**: User's question or prompt that initiates the advisory workflow

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can complete an advisory session from question to answer in under 2 minutes for typical queries
- **SC-002**: System retrieves relevant context with 80% accuracy (users report the retrieved notes are relevant to their question)
- **SC-003**: 90% of advisory sessions produce balanced advice incorporating all three agent perspectives (Archivist facts, Strategist analysis, Coach reflection)
- **SC-004**: Users can ask meaningful follow-up questions and receive contextually relevant responses in 95% of cases
- **SC-005**: Privacy requirement met: 100% of personal notes remain local (never transmitted); only user query and agent prompts sent to external LLM services
- **SC-006**: 85% of users report the advice is personally relevant and actionable based on their specific situation and notes
- **SC-007**: System handles note directories with 100+ files without performance degradation (search and retrieval completes in under 3 seconds)
