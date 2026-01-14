## 2024-05-22 - [Optimizing File Scanning in UI]
**Learning:** In Streamlit apps, long-running processes like file scanning can block the UI or cause bad UX if done synchronously. Reading files twice (once for stats, once for processing) is a common anti-pattern.
**Action:** Use `os.stat` or similar lightweight metadata calls for the first pass to estimate work, instead of full content reads.

## 2026-01-14 - [Parallelizing IO-Bound Ingestion]
**Learning:** Ingestion pipelines often involve multiple independent IO/Network-bound steps (e.g., vector DB write + LLM extraction). Running them sequentially doubles the latency.
**Action:** Use `concurrent.futures.ThreadPoolExecutor` to parallelize independent steps like `kb.add_events` and `mem0.remember`. Verified 50% speedup.
