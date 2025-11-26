<!--
SYNC IMPACT REPORT
==================
Version change: None → 1.0.0 (Initial constitution creation)
Modified principles: N/A (all new)
Added sections: Core Principles (5 sections: Engineering Standards, Modern Tech Stack, Monolithic Modular Architecture, Stateless Data Operations, Testing and Documentation), Tech Stack Requirements, Development Workflow, Governance
Removed sections: N/A
Templates verified: ✅ .specify/templates/plan-template.md (no updates needed - uses generic "Constitution Check"), ✅ .specify/templates/spec-template.md (no updates needed - technology-agnostic), ✅ .specify/templates/tasks-template.md (no updates needed - parameterized), ✅ .claude/commands/speckit.constitution.md (no updates needed - generic guidance)
Follow-up TODOs: TODO(RATIFICATION_DATE) - Original adoption date unknown, requires team confirmation
-->

# Echo-Board Constitution

## Core Principles

### I. Engineering Standards
Python 3.10+ is mandatory for all code (use `python3` command, not `python`). Strict PEP 8 compliance required with Google Python Style Guide for docstrings. Type Hinting is mandatory for all function signatures using `typing` and `pydantic`. All internal code comments, docstrings, and commit messages must be in English. User-facing UI and Agent outputs must be in Simplified Chinese. Configuration follows 12-Factor App principles with secrets loaded via `.env` or Environment Variables, never hardcoded.

### II. Modern Tech Stack
Project must use latest stable versions of: Streamlit for frontend UI (clean, reactive components), LangGraph for orchestration (stateful multi-agent), `langchain-google-genai` for LLM integration (Gemini Pro/Flash & embeddings), ChromaDB for vector storage (local persistent mode), and Pydantic V2 for data validation. Library-level integrations preferred over custom server deployments for MVP scope.

### III. Monolithic Modular Architecture
MVP follows Monolithic Modular architecture using Repository Pattern for data access, State Machine for logic, and Component-based UI architecture. Maintain clear separation of concerns within unified deployment unit. Architecture decisions must prioritize simplicity and maintainability over premature distributed complexity.

### IV. Stateless Data Operations
ChromaDB operates in local persistent mode for vector storage. All database operations must be transactional and reversible. Vector embeddings must be reproducible with consistent metadata tagging for audit trails. Regular data validation checkpoints required.

### V. Testing and Documentation
TDD encouraged: write tests first where practical. Integration tests mandatory for agent workflows and LLM interactions. Mock external API calls in unit tests. Comprehensive docstrings required for all public APIs. Inline comments required for complex business logic. Documentation must be kept current with code changes.

## Tech Stack Requirements

All development must adhere to specified technology versions and integration patterns using Python 3.10+ (`python3` command). Streamlit provides the frontend framework with emphasis on reactive components and clean user experience. LangGraph manages multi-agent orchestration with stateful workflows. `langchain-google-genai` handles all LLM operations including Gemini Pro, Flash, and embedding generation. ChromaDB stores vectors in persistent local mode. Pydantic V2 ensures strict data validation throughout the application.

## Development Workflow

Feature development follows iterative approach: design → implementation → testing → documentation. Code reviews required for all changes. Pull requests must include test coverage and updated documentation. Main branch protection enforced with required checks. Commit messages follow conventional commits format. Automated testing runs on every commit. Documentation updated concurrent with feature development.

## Governance

This constitution supersedes all other development practices within the project. Amendments require documentation of changes, rationale, and migration plan. All contributors must verify compliance with these principles. Complexity must be justified with performance, security, or maintainability benefits. Use project documentation for runtime development guidance.

**Version**: 1.0.0 | **Ratified**: TODO(RATIFICATION_DATE): Original adoption date unknown | **Last Amended**: 2025-11-26
