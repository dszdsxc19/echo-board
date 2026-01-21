## 2024-05-22 - [Optimizing File Scanning in UI]
**Learning:** In Streamlit apps, long-running processes like file scanning can block the UI or cause bad UX if done synchronously. Reading files twice (once for stats, once for processing) is a common anti-pattern.
**Action:** Use `os.stat` or similar lightweight metadata calls for the first pass to estimate work, instead of full content reads.

## 2024-05-23 - [Parallelizing UI-Blocking Ingestion]
**Learning:** Streamlit runs on a main thread loop. CPU/IO bound tasks in loops block the UI. ThreadPoolExecutor allows parallelization, but UI updates (`st.write`, `st.progress`) MUST happen on the main thread (e.g., iterating `as_completed`), or they will fail or cause race conditions.
**Action:** Use `ThreadPoolExecutor` for the heavy lifting and a main-thread loop over `futures.as_completed()` to consume results and update the UI safe-ly.
