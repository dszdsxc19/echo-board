# Quickstart Guide: Personal Board of Directors

**Date**: 2025-11-26
**Version**: 1.0.0
**Feature**: Personal Board of Directors

---

## Overview

The Personal Board of Directors is a Streamlit application that provides AI-powered life advice by analyzing your personal notes through a three-agent system (Archivist, Strategist, Coach). This guide will get you up and running in minutes.

**What it does**: Analyzes your Obsidian notes and provides balanced, data-driven advice for life decisions through a sequential multi-agent conversation.

**Who it's for**: Self-reflective individuals who maintain personal notes and seek data-driven guidance for important decisions.

---

## Prerequisites

### System Requirements

- **Python**: 3.10 or higher
- **Operating System**: macOS, Linux, or Windows
- **Memory**: 2GB RAM minimum (4GB recommended for 100+ notes)
- **Storage**: 500MB free space (for ChromaDB and SQLite)

### Required Files

- **Obsidian Notes**: Directory of markdown (.md) files with optional frontmatter
- **Gemini API Key**: Required for LLM inference (free tier available)

---

## Installation

### Step 1: Clone and Setup

```bash
# Navigate to project directory
cd /path/to/echo-board

# Create virtual environment with uv
uv venv

# Activate virtual environment
# On macOS/Linux:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate

# Install dependencies
uv pip install -e .
```

### Step 2: Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your settings
```

**Required .env Configuration**:

```env
# LLM Configuration
LLM_PROVIDER=gemini-flash
GEMINI_API_KEY=your_api_key_here

# Notes Configuration
NOTES_DIRECTORY=/path/to/your/obsidian/notes

# Vector Store Configuration
VECTOR_STORE_PATH=./data/chroma_db

# Conversation Storage
CONVERSATION_DB_PATH=./data/conversations.db
```

**Getting your Gemini API Key**:

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Copy to `.env` file

**Locating your Notes Directory**:

```bash
# macOS/Linux
NOTES_DIRECTORY=/Users/yourname/Documents/Obsidian/Vault

# Windows
NOTES_DIRECTORY=C:\Users\YourName\Documents\Obsidian\Vault
```

### Step 3: Initialize Database

```bash
# First run will initialize ChromaDB and SQLite
streamlit run src/app.py
```

The application will:
1. ✅ Create `./data/chroma_db` directory
2. ✅ Initialize SQLite database at `CONVERSATION_DB_PATH`
3. ✅ Prompt for notes directory if not set in .env
4. ✅ Start Streamlit development server

---

## First Run

### 1. Launch Application

```bash
streamlit run src/app.py
```

The app will open in your browser at `http://localhost:8501`

### 2. Configure Notes Directory

If not set in `.env`, the app will prompt:

```
Enter the path to your Obsidian notes directory:
> /path/to/your/notes
```

**What happens next**:

- ✅ Validates directory exists and is readable
- ✅ Scans for all `.md` files
- ✅ Parses frontmatter (date, tags, title)
- ✅ Chunks content (1000 words, 200-word overlap per FR-014)
- ✅ Generates embeddings with Gemini
- ✅ Stores in ChromaDB vector index

**Initial indexing time**:
- 10 notes: ~30 seconds
- 50 notes: ~2 minutes
- 100 notes: ~5 minutes

### 3. First Advisory Session

Once indexing is complete:

1. **Ask a question** in the chat input:
   ```
   Should I accept the job offer in Tokyo?
   ```

2. **Wait for processing** (30-60 seconds typical):
   - 🔄 Retrieving relevant notes...
   - 🔄 Archivist analyzing facts...
   - 🔄 Strategist evaluating options...
   - 🔄 Coach synthesizing advice...

3. **View response**:
   - Three agent responses (Archivist, Strategist, Coach)
   - Evidence hidden by default (expand to see citations)
   - Processing time displayed

---

## Usage Guide

### Asking Effective Questions

**Good questions** (specific, contextual):

```
"I'm considering transitioning from software engineering to product management.
Given my past experiences and goals, what factors should I weigh?"

"Should I move to a larger apartment or save for a house down payment?"
```

**Avoid**:
```
"What should I do?" (too vague)
"Tell me about myself" (too broad)
"Who am I?" (not actionable)
```

### Viewing Evidence

Evidence (source note excerpts) is **hidden by default** per FR-005.

**To view evidence**:
1. Click "Show Evidence" button below any agent response
2. See specific note excerpts with file paths
3. Click "Hide Evidence" to collapse

### Follow-up Questions

The system maintains conversation context across sessions.

**Examples**:
```
Follow-up to "job in Tokyo" question:
"What are the tax implications of working in Japan?"
```

### Checking History

**View past sessions**:
- Scroll up in chat interface
- Previous conversations listed chronologically
- Click any to review full session

---

## Configuration

### Adjusting Settings

Edit `.env` file and restart application:

```env
# More context (slower)
RETRIEVAL_TOP_K=15

# Less context (faster)
RETRIEVAL_TOP_K=5

# Adjust chunk size (words)
CHUNK_SIZE=500
CHUNK_OVERLAP=100

# Timeout (seconds)
LLM_TIMEOUT=60
```

### Changing Notes Directory

**Option 1**: Update `.env` and restart
```env
NOTES_DIRECTORY=/path/to/new/notes
```

**Option 2**: Use UI
- Settings panel (sidebar)
- Update "Notes Directory" field
- Click "Re-index Notes"

---

## Common Tasks

### Updating Notes

**Automatic** (Incremental Re-indexing per FR-013):
- Add/edit/delete notes in your Obsidian vault
- System detects changes on next query
- Only modified files re-indexed (fast!)

**Manual Re-index**:
- Settings panel → "Force Re-index All Notes"
- Useful after bulk note changes

### Exporting Conversations

**From SQLite database**:
```python
import sqlite3

conn = sqlite3.connect('./data/conversations.db')
cursor = conn.cursor()

# Export all sessions
cursor.execute("SELECT * FROM conversation_sessions")
sessions = cursor.fetchall()

# Export with responses
cursor.execute("""
    SELECT cs.session_id, cs.user_query, ar.agent_type, ar.response_text
    FROM conversation_sessions cs
    JOIN agent_responses ar ON cs.session_id = ar.session_id
    ORDER BY cs.created_at DESC
""")
data = cursor.fetchall()
```

### Clearing Data

**Reset everything**:
```bash
# Stop the application first!

# Remove vector database
rm -rf ./data/chroma_db

# Remove conversation history
rm ./data/conversations.db

# Restart application
streamlit run src/app.py
```

**Keep conversations, re-index notes only**:
```bash
rm -rf ./data/chroma_db
streamlit run src/app.py
```

---

## Troubleshooting

### Issue: "No relevant notes found"

**Cause**: Vector search returned no results above threshold

**Solution**:
1. Add more notes to your directory
2. Ensure notes have substantial content (>100 words each)
3. Lower similarity threshold (edit .env)
4. Try more specific query terms

### Issue: "LLM Error" or "API Key Invalid"

**Cause**: Invalid or missing API key

**Solution**:
1. Verify API key in `.env`
2. Check key hasn't expired
3. Ensure Gemini API is enabled
4. Test key: `curl -H 'Content-Type: application/json' -d '{"contents":[{"parts":[{"text":"test"}]}]}' -X POST "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key=YOUR_KEY"`

### Issue: "Directory Not Found"

**Cause**: Incorrect notes directory path

**Solution**:
1. Use absolute path in `.env`
2. Ensure directory exists
3. Check file permissions
4. Try different directory first

### Issue: Slow Performance

**Cause**: Too many notes or large chunk size

**Solutions**:
1. Reduce `RETRIEVAL_TOP_K` (default 10)
2. Decrease `CHUNK_SIZE` (default 1000)
3. Re-index with smaller chunks
4. Consider using a SSD for storage

### Issue: Application Won't Start

**Debug steps**:
```bash
# Check Python version
python --version  # Should be 3.10+

# Verify dependencies
pip list | grep -E "(streamlit|chromadb|pydantic)"

# Run with verbose logging
streamlit run src/app.py --logger.level=debug

# Check for errors in terminal
```

---

## Performance Tips

### For 100+ Notes

1. **Use SSD storage** for ChromaDB
2. **Keep chunk size moderate** (1000 words)
3. **Add notes gradually** to monitor performance
4. **Monitor vector store size**:
   ```bash
   du -sh ./data/chroma_db
   ```

### For Faster Queries

1. **Enable incremental re-indexing** (default on)
2. **Avoid full re-indexing** unless necessary
3. **Use specific queries** (narrow scope)
4. **Keep conversation history** reasonable (<100 sessions)

### Memory Usage

**Typical memory usage**:
- 10 notes: ~200MB
- 50 notes: ~800MB
- 100 notes: ~1.5GB

Monitor with: `Activity Monitor` (macOS) or `htop` (Linux)

---

## Data Privacy

### What's Local

✅ **Your Notes**: Stored only on your device
✅ **Conversation History**: SQLite database on your device
✅ **Vector Embeddings**: ChromaDB on your device

### What's External

⚠️ **Your Queries**: Sent to Gemini API
⚠️ **Agent Prompts**: Sent to Gemini API
⚠️ **Retrieved Content**: Sent to Gemini API for processing

**Your notes themselves never leave your device.**

### Privacy Best Practices

1. **Secure your API key**: Don't commit `.env` to git
2. **Use strong file permissions**: Protect your data directory
3. **Consider encryption**: Full-disk encryption recommended
4. **Regular backups**: Backup both notes and conversation database

---

## Architecture Overview

### Components

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

### Data Flow

1. **Query**: User asks question
2. **Search**: Vector similarity search in ChromaDB
3. **Workflow**: Three agents process sequentially
4. **Response**: Synthesized advice returned
5. **Persist**: Session saved to SQLite

---

## Support

### Getting Help

1. **Check this guide** for common issues
2. **Review logs** in terminal/console output
3. **Check ChromaDB status**: Settings panel
4. **Verify API key**: Gemini AI Studio

### Reporting Issues

When reporting issues, include:

- Python version (`python --version`)
- OS and version
- Number of notes
- Full error message
- Steps to reproduce

### Feature Requests

This is an MVP. Consider implementing:
- Multi-user support
- Custom agent prompts
- Note tagging system
- Advanced filtering
- Export functionality

---

## License

Echo-Board Personal Board of Directors
Copyright (c) 2025

This project is part of the Echo-Board application suite.

---

## What's Next

Ready to proceed? Run:

```bash
# Generate implementation tasks
/speckit.tasks

# Or continue development directly
streamlit run src/app.py
```

Happy decision-making! 🎯
