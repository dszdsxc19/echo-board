## 2024-05-22 - [Optimizing File Scanning in UI]
**Learning:** In Streamlit apps, long-running processes like file scanning can block the UI or cause bad UX if done synchronously. Reading files twice (once for stats, once for processing) is a common anti-pattern.
**Action:** Use `os.stat` or similar lightweight metadata calls for the first pass to estimate work, instead of full content reads.

## 2026-01-26 - [Parallelizing IO-Bound Ingestion]
**Learning:** Sequential processing of files involving LLM/DB calls drastically slows down the UI loop in Streamlit. `ThreadPoolExecutor` is effective for I/O bound tasks (like embedding generation via API), but requires careful handling of UI updates (must run in main thread via `as_completed` or similar).
**Action:** Use `ThreadPoolExecutor` for batch processing, collecting results in futures, and updating the UI iteratively as futures complete.
