## 2024-05-22 - [Optimizing File Scanning in UI]
**Learning:** In Streamlit apps, long-running processes like file scanning can block the UI or cause bad UX if done synchronously. Reading files twice (once for stats, once for processing) is a common anti-pattern.
**Action:** Use `os.stat` or similar lightweight metadata calls for the first pass to estimate work, instead of full content reads.

## 2024-05-23 - [Parallelizing Streamlit Ingestion]
**Learning:** Streamlit is not thread-safe for UI updates. When parallelizing tasks with `ThreadPoolExecutor`, you cannot call `st.*` functions inside the worker threads.
**Action:** Use `as_completed` in the main thread to collect results and update the UI incrementally based on the returned data.
