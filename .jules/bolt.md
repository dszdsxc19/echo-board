## 2024-05-22 - [Optimizing File Scanning in UI]
**Learning:** In Streamlit apps, long-running processes like file scanning can block the UI or cause bad UX if done synchronously. Reading files twice (once for stats, once for processing) is a common anti-pattern.
**Action:** Use `os.stat` or similar lightweight metadata calls for the first pass to estimate work, instead of full content reads.

## 2026-01-12 - [Parallelizing Independent I/O Operations]
**Learning:** Sequential execution of independent I/O-bound tasks (like vector DB writes and profile service updates) unnecessarily increases latency. Python's `ThreadPoolExecutor` is effective for these cases even with the GIL, as I/O releases the lock.
**Action:** When multiple independent storage/API calls are made in a single workflow, wrap them in `concurrent.futures.ThreadPoolExecutor` to run them in parallel. Always ensure exceptions are propagated by checking `future.result()`.
