import time
import concurrent.futures
from dataclasses import dataclass

# Mock Engine
class MockIngestionEngine:
    def process_file(self, content, source_name="unknown"):
        # Simulate I/O bound work (e.g. embedding API call + DB write)
        time.sleep(0.1)

# Mock Data
md_files = [f"file_{i}.md" for i in range(20)]
ingestion_engine = MockIngestionEngine()

def run_sequential():
    start_time = time.time()
    for file_path in md_files:
        content = "dummy content"
        ingestion_engine.process_file(content, source_name=file_path)
    return time.time() - start_time

def process_file_wrapper(file_path):
    content = "dummy content"
    ingestion_engine.process_file(content, source_name=file_path)
    return file_path

def run_parallel():
    start_time = time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        futures = {executor.submit(process_file_wrapper, fp): fp for fp in md_files}
        for future in concurrent.futures.as_completed(futures):
            future.result()
    return time.time() - start_time

if __name__ == "__main__":
    print("Running benchmarks...")
    seq_time = run_sequential()
    print(f"Sequential time: {seq_time:.4f}s")

    par_time = run_parallel()
    print(f"Parallel time: {par_time:.4f}s")

    speedup = seq_time / par_time
    print(f"Speedup: {speedup:.2f}x")

    if speedup > 1.5:
        print("✅ Performance improvement confirmed.")
    else:
        print("❌ Performance improvement negligible.")
