# Data Model: Personal Board of Directors

**Date**: 2025-11-26
**Feature**: Personal Board of Directors
**Phase**: 1 - Design & Contracts

## Entities

### 1. Note

Represents individual markdown files containing personal data.

**Attributes**:
- `file_path` (str): Absolute path to the markdown file
- `title` (str, optional): Note title from frontmatter or filename
- `date` (datetime, optional): Date from frontmatter metadata
- `tags` (List[str], optional): List of tags from frontmatter
- `content` (str): Raw markdown content body
- `frontmatter` (dict): Raw frontmatter metadata dict
- `chunks` (List[NoteChunk]): Segmented content for retrieval
- `modified_at` (datetime): Last file modification timestamp
- `created_at` (datetime): When note was first ingested
- `embedding_id` (str): ChromaDB document ID for vector search

**Relationships**:
- Has many NoteChunk (content segmentation)
- Linked to AgentResponse via citations

**State Transitions**:
- New → Indexed (when first ingested)
- Indexed → Modified (when file changes)
- Modified → Re-indexed (after incremental update)
- Re-indexed → Indexed

**Validation Rules**:
- file_path must exist and be readable
- content cannot be empty
- date must be valid datetime if present
- tags must be list of strings if present

---

### 2. NoteChunk

Segmented piece of a note for semantic retrieval.

**Attributes**:
- `chunk_id` (str): Unique identifier (UUID)
- `note_id` (str): Reference to parent Note (file_path)
- `content` (str): Text content of chunk
- `word_count` (int): Number of words in chunk
- `chunk_index` (int): Position within original note (0-based)
- `overlap_content` (str, optional): Context from adjacent chunks (200-word overlap per clarified FR-014)
- `embedding` (List[float]): Vector embedding for semantic search
- `metadata` (dict): Additional chunk metadata

**Relationships**:
- Belongs to one Note
- Referenced by ContextDocument in retrieval results

**Validation Rules**:
- content must be non-empty
- word_count must match actual content
- chunk_index must be sequential within note
- embedding must be valid float vector

---

### 3. ConversationSession

Discrete advisory interaction including query and all agent responses.

**Attributes**:
- `session_id` (str): Unique identifier (UUID)
- `user_query` (str): User's question or prompt
- `created_at` (datetime): When session started
- `completed_at` (datetime, optional): When session finished
- `status` (str): Enum - 'active', 'completed', 'failed'
- `processing_time` (float, optional): Seconds from start to completion
- `context_documents` (List[ContextDocument]): Retrieved documents
- `agent_responses` (List[AgentResponse]): All three agent outputs
- `final_advice` (str): Synthesized advice from coach
- `conversation_history` (List[str]): Previous conversation context for follow-ups

**Relationships**:
- Has many ContextDocument (retrieved for this query)
- Has many AgentResponse (three responses per session)
- May reference previous ConversationSession for context

**State Transitions**:
- Created → Active (query submitted)
- Active → Completed (all agents responded)
- Active → Failed (timeout or error)
- Failed → Active (retry if applicable)

**Validation Rules**:
- user_query cannot be empty
- Must have exactly 3 agent_responses when completed
- context_documents must be <= 10 (top-k limit)
- processing_time must be <= 60 seconds per clarified FR-011

---

### 4. ContextDocument

Relevant document chunk retrieved for a query.

**Attributes**:
- `doc_id` (str): Unique identifier (UUID)
- `session_id` (str): Reference to parent ConversationSession
- `chunk_id` (str): Reference to NoteChunk
- `similarity_score` (float): Cosine similarity to query (0-1)
- `retrieval_rank` (int): Position in retrieved results (1-10)
- `note_path` (str): Source note file path
- `excerpt` (str): Display excerpt for UI evidence
- `date_context` (str, optional): Date context from note for relevance

**Relationships**:
- Belongs to one ConversationSession
- References one NoteChunk

**Validation Rules**:
- similarity_score must be between 0 and 1
- retrieval_rank must be 1-10
- excerpt cannot be empty
- Must reference valid NoteChunk

---

### 5. AgentResponse

Output from one of the three specialized agents.

**Attributes**:
- `response_id` (str): Unique identifier (UUID)
- `session_id` (str): Reference to parent ConversationSession
- `agent_type` (str): Enum - 'archivist', 'strategist', 'coach'
- `response_text` (str): Agent's response content
- `processing_order` (int): Order in workflow (1=archivist, 2=strategist, 3=coach)
- `processing_time` (float): Time taken for this agent's response
- `tokens_used` (int, optional): LLM token count
- `cites_context` (bool): Whether response includes evidence citations
- `context_documents` (List[str]): List of ContextDocument IDs referenced

**Relationships**:
- Belongs to one ConversationSession
- May reference multiple ContextDocument for citations

**State Transitions**:
- Pending → Processing
- Processing → Completed
- Processing → Failed
- Failed → Retried

**Validation Rules**:
- agent_type must be valid enum value
- processing_order must be 1-3
- response_text cannot be empty
- Must have valid processing_time

---

### 6. UserQuery

User's question or prompt that initiates advisory workflow.

**Attributes**:
- `query_id` (str): Unique identifier (UUID)
- `session_id` (str): Reference to parent ConversationSession
- `query_text` (str): The actual question text
- `query_type` (str, optional): Enum - 'initial', 'follow_up', 'clarification'
- `previous_query_id` (str, optional): Reference to prior query for context
- `timestamp` (datetime): When query was submitted

**Relationships**:
- Belongs to one ConversationSession
- May reference previous UserQuery for follow-ups

**Validation Rules**:
- query_text cannot be empty
- If query_type is 'follow_up', must have previous_query_id
- timestamp must be valid datetime

---

### 7. VectorIndex

Metadata for ChromaDB vector storage.

**Attributes**:
- `index_id` (str): ChromaDB collection name or ID
- `note_path` (str): File path for the note
- `chunk_id` (str): NoteChunk ID
- `embedding` (List[float]): The vector embedding
- `metadata` (dict): ChromaDB metadata (title, date, tags, etc.)
- `last_updated` (datetime): When this embedding was created/updated

**Relationships**:
- Links NoteChunk to ChromaDB storage

**Validation Rules**:
- embedding must be valid float vector
- metadata must contain required fields
- note_path must match actual file

---

## Database Storage

### SQLite Tables (for application state)

1. **notes**: Persist note metadata (not content, to avoid duplication)
2. **conversation_sessions**: Store session history
3. **user_queries**: Log all user queries
4. **agent_responses**: Store agent outputs
5. **context_documents**: Track retrieved documents per session
6. **vector_index**: Track ChromaDB embeddings metadata

### ChromaDB Collections (for vector search)

1. **note_chunks**: Collection storing all NoteChunk embeddings
   - Documents: chunk content
   - Metadata: note_path, chunk_index, title, date, tags
   - IDs: chunk_id

## Data Validation

All entities use Pydantic models for:
- Type validation (str, int, datetime, etc.)
- Required field enforcement
- Custom validators (date format, path validation, etc.)
- Metadata serialization for storage

## Migration Strategy

1. **v1.0**: Initial schema with basic entities
2. **v1.1**: Add incremental re-indexing tracking (if needed)
3. **v2.0**: Multi-user support (future)

No schema migrations needed for MVP - all entities defined upfront.

## Performance Considerations

- **NoteChunking**: 1000-word chunks with 200-word overlap (per FR-014)
- **Indexing**: Batch insert to ChromaDB for efficiency
- **Retrieval**: top-k=10 with similarity threshold
- **Caching**: Cache recent embeddings, invalidate on file changes
- **Pagination**: For conversation history display (20 sessions per page)

## Security & Privacy

- **Local Only**: All SQLite data stored locally
- **No Encryption**: SQLite database not encrypted (user's responsibility)
- **Gitignore**: data/ directory excluded from version control
- **API Keys**: Stored in .env, never in database
- **Redaction**: Consider redacting sensitive patterns from embeddings (future)
