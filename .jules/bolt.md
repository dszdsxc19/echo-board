## 2024-05-22 - [Optimizing File Scanning in UI]
**Learning:** In Streamlit apps, long-running processes like file scanning can block the UI or cause bad UX if done synchronously. Reading files twice (once for stats, once for processing) is a common anti-pattern.
**Action:** Use `os.stat` or similar lightweight metadata calls for the first pass to estimate work, instead of full content reads.

## 2024-05-22 - [Parallelizing Streamlit Data Ingestion]
**Learning:** Updating Streamlit UI elements (like progress bars) from background threads is unsafe. To parallelize work, use `concurrent.futures.ThreadPoolExecutor` to run tasks, but iterate over `futures.as_completed()` in the main thread to perform UI updates.
**Action:** Always decouple the heavy computation (worker thread) from the progress reporting (main thread) when working with Streamlit.
