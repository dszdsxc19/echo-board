## 2024-05-22 - [Optimizing File Scanning in UI]
**Learning:** In Streamlit apps, long-running processes like file scanning can block the UI or cause bad UX if done synchronously. Reading files twice (once for stats, once for processing) is a common anti-pattern.
**Action:** Use `os.stat` or similar lightweight metadata calls for the first pass to estimate work, instead of full content reads.

## 2024-05-23 - [Parallel File Ingestion]
**Learning:** Sequential processing of files for RAG ingestion (embedding + vector DB) in Streamlit is a major bottleneck due to network/IO latency. However, Streamlit is not thread-safe for UI updates.
**Action:** Use `ThreadPoolExecutor` to parallelize processing. Ensure UI updates happen only in the main thread via `as_completed` futures to avoid Streamlit thread-safety issues.
