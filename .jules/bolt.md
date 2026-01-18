## 2024-05-22 - [Optimizing File Scanning in UI]
**Learning:** In Streamlit apps, long-running processes like file scanning can block the UI or cause bad UX if done synchronously. Reading files twice (once for stats, once for processing) is a common anti-pattern.
**Action:** Use `os.stat` or similar lightweight metadata calls for the first pass to estimate work, instead of full content reads.

## 2024-05-23 - [Parallelizing Independent Storage Backends]
**Learning:** The ingestion pipeline writes to two independent systems: a vector store (local/Chroma) and a user profile service (Mem0/API). Doing this sequentially doubles the latency, especially when LLM calls are involved.
**Action:** Use `concurrent.futures.ThreadPoolExecutor` to parallelize independent I/O or network-bound tasks within a single unit of work (e.g., `process_file`), ensuring thread safety is respected for each backend.
