import time
import concurrent.futures
import logging

# Mock logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MockIngestionEngine:
    def process_file(self, content, source_name):
        # Simulate I/O or LLM latency
        time.sleep(0.1)
        return True

def benchmark():
    engine = MockIngestionEngine()
    files = [f"file_{i}.md" for i in range(50)] # 50 files

    print(f"Starting benchmark with {len(files)} files...")

    # Sequential
    start_seq = time.time()
    for f in files:
        engine.process_file("content", f)
    duration_seq = time.time() - start_seq
    print(f"Sequential Execution: {duration_seq:.2f}s")

    # Concurrent
    start_conc = time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(engine.process_file, "content", f) for f in files]
        for future in concurrent.futures.as_completed(futures):
            future.result()
    duration_conc = time.time() - start_conc
    print(f"Concurrent Execution (4 workers): {duration_conc:.2f}s")

    improvement = (duration_seq - duration_conc) / duration_seq * 100
    print(f"Improvement: {improvement:.2f}%")

if __name__ == "__main__":
    benchmark()
