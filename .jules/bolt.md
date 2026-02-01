## 2024-05-22 - [Optimizing File Scanning in UI]
**Learning:** In Streamlit apps, long-running processes like file scanning can block the UI or cause bad UX if done synchronously. Reading files twice (once for stats, once for processing) is a common anti-pattern.
**Action:** Use `os.stat` or similar lightweight metadata calls for the first pass to estimate work, instead of full content reads.

## 2024-05-23 - [Parallel File Processing in Streamlit]
**Learning:** IO-bound operations (like reading files and sending them to an embedding engine) in a sequential loop significantly slow down data ingestion. Streamlit UI updates must stay on the main thread.
**Action:** Use `concurrent.futures.ThreadPoolExecutor` to offload processing. Iterate over `as_completed` futures in the main thread to update `st.progress` safely. Extracted logic to a helper function to ensure thread safety and testability.
