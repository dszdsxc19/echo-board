# Echo-Board: Personal Board of Directors

> 💭 AI-powered life advice from your personal Obsidian notes

## Overview

Echo-Board is a Streamlit application that provides balanced, data-driven advice through a multi-agent system (Archivist, Strategist, Coach) based on your personal notes. The system ingests markdown files, retrieves relevant context via semantic search, and orchestrates a sequential agent workflow.

## Features

- **📚 Archivist Agent**: Extracts objective facts with citations from your notes
- **💡 Strategist Agent**: Provides rational analysis and ROI evaluation
- **🎯 Coach Agent**: Offers empathetic guidance with reflective questions
- **🔍 Semantic Search**: Finds relevant notes using ChromaDB vector storage
- **📊 Evidence Display**: View source citations (hidden by default)
- **💬 Conversation History**: Maintain context across sessions
- **🇨🇳 Simplified Chinese UI**: Full Chinese language support

## Architecture

```
┌─────────────────────────────────────────┐
│         Streamlit UI                    │
│  (Chat Interface, Evidence Display)     │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│         LangGraph Orchestration         │
│  (Three-Agent Workflow Management)      │
└──────────────┬──────────────────────────┘
               │
       ┌───────┴───────┐
       │               │
┌──────▼──────┐  ┌────▼─────────────┐
│   Archivist │  │  Strategist      │
│   Agent     │  │  Agent           │
└──────┬──────┘  └────┬─────────────┘
       │              │
       └──────┬───────┘
              │
       ┌──────▼──────┐
       │   Coach     │
       │   Agent     │
       └──────┬──────┘
              │
┌─────────────▼──────────────────────────┐
│         ChromaDB                        │
│    (Vector Similarity Search)           │
└─────────────┬──────────────────────────┘
              │
┌─────────────▼──────────────────────────┐
│      Markdown Notes                     │
│    (Frontmatter + Content)              │
└─────────────────────────────────────────┘
```

## Quick Start

### Prerequisites

- Python 3.10+ (use `python3` command, not `python`)
- Gemini API Key ([Get from Google AI Studio](https://makersuite.google.com/app/apikey))

### Installation

1. **Clone the repository**

   ```bash
   cd /path/to/echo-board
   ```

2. **Verify Python version**

   ```bash
   python3 --version  # Should be 3.10+
   ```

3. **Create virtual environment**

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

4. **Install dependencies**

   ```bash
   python3 -m pip install -e .
   ```

5. **Configure environment**

   ```bash
   cp .env.example .env
   # Edit .env with your API key and notes directory
   ```

6. **Initialize databases**

   ```bash
   python3 -m src.data.init_db
   ```

7. **Run the application**
   ```bash
   python3 -m streamlit run src/app.py
   ```

## Configuration

Edit `.env` file:

```env
# LLM Configuration
GEMINI_API_KEY=your_api_key_here
LLM_PROVIDER=gemini-flash
LLM_TIMEOUT=60

# Notes Configuration
NOTES_DIRECTORY=./data/obsidian_vault

# Vector Store Configuration
VECTOR_STORE_PATH=./data/chroma_db
RETRIEVAL_TOP_K=10
CHUNK_SIZE=1000
CHUNK_OVERLAP=200

# Conversation Storage
CONVERSATION_DB_PATH=./data/conversations.db
```

## Project Structure

```
echo-board/
├── src/
│   ├── app.py                  # Streamlit UI
│   ├── core/
│   │   ├── config.py           # Configuration management
│   │   ├── state.py            # LangGraph state definitions
│   │   └── models/             # Pydantic data models
│   ├── data/
│   │   ├── loader.py           # Note loading and parsing
│   │   ├── vector_store.py     # ChromaDB integration
│   │   └── database.py         # SQLite database
│   └── agents/
│       ├── nodes.py            # Agent implementations
│       ├── graph.py            # LangGraph workflow
│       └── prompts/            # Agent prompt templates
├── data/
│   └── obsidian_vault/         # Your notes directory
├── tests/                      # Test suite
├── .env.example                # Configuration template
├── pyproject.toml              # Dependencies
└── README.md                   # This file
```

## Usage

1. **Launch the app**: `streamlit run src/app.py`

2. **Configure notes directory** in the sidebar

3. **Load your notes** by clicking "📂 加载笔记"

4. **Ask a question** in the chat interface

5. **View responses** from all three agents

6. **Expand evidence** to see source citations

## Implementation Status

### ✅ Completed (Phase 1-3)

- [x] Project setup and configuration
- [x] Pydantic models for all entities
- [x] Configuration management
- [x] LangGraph state schema
- [x] Database initialization (SQLite + ChromaDB)
- [x] Note loading and parsing
- [x] Vector storage integration
- [x] Three-agent workflow (Archivist, Strategist, Coach)
- [x] Simplified Chinese prompts and UI
- [x] Streamlit chat interface
- [x] Evidence display component
- [x] Loading states and error handling

### 🚧 In Progress

- [ ] Embedding generation and retrieval
- [ ] Full workflow integration
- [ ] Conversation persistence

### 📋 To Do

- [ ] User Story 2: Continue Prior Advisory Session
- [ ] User Story 3: Configure Personal Data Source
- [ ] Polish and testing

## Constitution Compliance

This project follows the Echo-Board Constitution:

✅ **Engineering Standards**: Python 3.10+ (`python3` command), Pydantic V2, type hints
✅ **Modern Tech Stack**: Streamlit, LangGraph, ChromaDB, Gemini
✅ **Monolithic Modular**: Repository pattern, state machine, components
✅ **Local Data Processing**: Notes never leave your device
✅ **Testing**: Integration tests for agent workflows
✅ **Language**: Simplified Chinese for UI and agent outputs

## Tech Stack

- **Frontend**: Streamlit
- **Orchestration**: LangGraph
- **LLM**: Google Gemini Flash
- **Vector Store**: ChromaDB
- **Database**: SQLite
- **Validation**: Pydantic v2
- **Language**: Python 3.10+

## Contributing

This is an MVP implementation. Contributions welcome!

## License

MIT License

## Support

For issues and questions, please open an issue on GitHub.

---

**Built with ❤️ using Streamlit, LangGraph, and ChromaDB**
