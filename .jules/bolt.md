## 2024-05-22 - [Optimizing File Scanning in UI]
**Learning:** In Streamlit apps, long-running processes like file scanning can block the UI or cause bad UX if done synchronously. Reading files twice (once for stats, once for processing) is a common anti-pattern.
**Action:** Use `os.stat` or similar lightweight metadata calls for the first pass to estimate work, instead of full content reads.

## 2024-05-22 - [Parallelizing Streamlit Ingestion]
**Learning:** Streamlit UI updates must happen in the main thread. When using `ThreadPoolExecutor` for heavy background tasks, submit tasks and then iterate over `as_completed` in the main thread to update progress bars/logs.
**Action:** Use `src/utils/ingestion_helper.py` pattern with `process_single_file` returning a dict result, and handle UI updates in the main loop.
