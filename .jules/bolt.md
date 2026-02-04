## 2024-05-22 - [Optimizing File Scanning in UI]
**Learning:** In Streamlit apps, long-running processes like file scanning can block the UI or cause bad UX if done synchronously. Reading files twice (once for stats, once for processing) is a common anti-pattern.
**Action:** Use `os.stat` or similar lightweight metadata calls for the first pass to estimate work, instead of full content reads.

## 2024-05-24 - [Parallelizing Streamlit Ingestion]
**Learning:** Sequential processing of files in Streamlit significantly slows down the UI update cycle. Using `ThreadPoolExecutor` with a helper function (to isolate logic) allows for parallel ingestion.
**Action:** When iterating over I/O bound tasks in Streamlit, always prefer `futures.as_completed` to process results and update the UI in the main thread while workers run in background.
