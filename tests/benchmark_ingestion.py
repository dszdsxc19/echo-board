import concurrent.futures
import random
import time


# Mock class to simulate the work
class MockIngestionEngine:
    def process_file(self, content, source_name):
        # Simulate processing time (e.g. embedding generation + DB write)
        # Random sleep between 0.1 and 0.3 seconds
        time.sleep(random.uniform(0.1, 0.3))
        return True

def process_file_wrapper(engine, content, name):
    return engine.process_file(content, name)

def run_sequential(files, engine):
    start = time.time()
    for f in files:
        engine.process_file(f['content'], f['name'])
    return time.time() - start

def run_parallel(files, engine, workers=4):
    start = time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        futures = [executor.submit(process_file_wrapper, engine, f['content'], f['name']) for f in files]
        for future in concurrent.futures.as_completed(futures):
            future.result()
    return time.time() - start

def main():
    print("⚡ Bolt Benchmark: Sequential vs Parallel Ingestion")

    # Setup
    num_files = 20
    files = [{'content': f"content {i}", 'name': f"file_{i}.md"} for i in range(num_files)]
    engine = MockIngestionEngine()

    print(f"Dataset: {num_files} files")
    print("Simulating ~0.2s latency per file...")

    # Sequential
    print("\nRunning Sequential...")
    seq_time = run_sequential(files, engine)
    print(f"Sequential Time: {seq_time:.2f}s")

    # Parallel
    workers = 4
    print(f"\nRunning Parallel ({workers} workers)...")
    par_time = run_parallel(files, engine, workers)
    print(f"Parallel Time: {par_time:.2f}s")

    # Results
    improvement = seq_time / par_time
    print(f"\nResult: Parallel is {improvement:.1f}x faster")

    if par_time < seq_time:
        print("✅ Optimization Verified!")
    else:
        print("❌ No improvement found.")

if __name__ == "__main__":
    main()
