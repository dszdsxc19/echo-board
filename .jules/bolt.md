## 2024-05-22 - [Optimizing File Scanning in UI]
**Learning:** In Streamlit apps, long-running processes like file scanning can block the UI or cause bad UX if done synchronously. Reading files twice (once for stats, once for processing) is a common anti-pattern.
**Action:** Use `os.stat` or similar lightweight metadata calls for the first pass to estimate work, instead of full content reads.
## 2024-05-23 - [Streamlit Concurrent UI Updates]
**Learning:** Streamlit is not thread-safe for UI updates. To parallelize heavy tasks (like file ingestion), run computation in `ThreadPoolExecutor` but iterate over `as_completed(futures)` in the main thread to update `st.progress` and `st.empty` components safely.
**Action:** Always decouple computation (worker threads) from UI updates (main thread) when optimizing Streamlit apps.
