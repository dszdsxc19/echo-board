## 2024-05-22 - [Optimizing File Scanning in UI]
**Learning:** In Streamlit apps, long-running processes like file scanning can block the UI or cause bad UX if done synchronously. Reading files twice (once for stats, once for processing) is a common anti-pattern.
**Action:** Use `os.stat` or similar lightweight metadata calls for the first pass to estimate work, instead of full content reads.

## 2026-01-13 - [Parallelizing Independent Ingestion Tasks]
**Learning:** Independent IO-bound tasks like vector DB insertion and LLM memory extraction can be parallelized to significantly reduce ingestion latency. `ThreadPoolExecutor` is effective here.
**Action:** Identify independent `add` or `write` operations in data pipelines and wrap them in `ThreadPoolExecutor`.
