## 2024-05-22 - [Optimizing File Scanning in UI]
**Learning:** In Streamlit apps, long-running processes like file scanning can block the UI or cause bad UX if done synchronously. Reading files twice (once for stats, once for processing) is a common anti-pattern.
**Action:** Use `os.stat` or similar lightweight metadata calls for the first pass to estimate work, instead of full content reads.

## 2024-10-26 - [Parallelizing File Ingestion in Streamlit]
**Learning:** Streamlit UI updates are not thread-safe and must run in the main thread. To parallelize work without freezing the UI or crashing, use `ThreadPoolExecutor` and iterate over `as_completed(futures)` in the main thread to perform UI updates.
**Action:** Extract worker logic to a pure function, submit to executor, and collect results in the main loop to update `st.progress` or `st.text`.
