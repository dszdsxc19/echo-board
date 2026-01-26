import time
import os
import tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from unittest.mock import Mock, MagicMock
from src.utils.ingestion_helper import process_single_file

class MockIngestionEngine:
    def process_file(self, content, source_name="unknown"):
        # Simulate I/O delay
        time.sleep(0.1)
        return []

def test_parallel_vs_sequential_ingestion():
    """
    Performance test to verify that parallel ingestion is faster than sequential.
    """
    engine = MockIngestionEngine()

    # Create temporary files
    with tempfile.TemporaryDirectory() as temp_dir:
        files = []
        for i in range(10):
            file_path = os.path.join(temp_dir, f"test_{i}.md")
            with open(file_path, "w") as f:
                f.write(f"Content for file {i}")
            files.append(file_path)

        # 1. Measure Sequential Time
        start_seq = time.time()
        for file_path in files:
            process_single_file(file_path, temp_dir, engine)
        seq_duration = time.time() - start_seq

        print(f"\nSequential Duration: {seq_duration:.4f}s")

        # 2. Measure Parallel Time
        start_par = time.time()
        with ThreadPoolExecutor(max_workers=4) as executor:
            future_to_file = {
                executor.submit(process_single_file, f, temp_dir, engine): f
                for f in files
            }
            results = []
            for future in as_completed(future_to_file):
                results.append(future.result())
        par_duration = time.time() - start_par

        print(f"Parallel Duration: {par_duration:.4f}s")

        # Verify correctness
        assert len(results) == 10
        assert all(r["status"] == "✅" for r in results)

        # Verify speedup
        # 10 files * 0.1s = 1.0s sequential.
        # 4 workers -> ~0.3s ideally (0.1 * 3 rounds).
        # We allow some overhead, so check if parallel is at least 30% faster than sequential.
        assert par_duration < seq_duration * 0.7, \
            f"Parallel ({par_duration}s) should be significantly faster than Sequential ({seq_duration}s)"
