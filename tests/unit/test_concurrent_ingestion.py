import time
import unittest
from concurrent.futures import ThreadPoolExecutor, as_completed
from unittest.mock import MagicMock, patch

from src.utils.ingestion_helper import process_single_file


class TestConcurrentIngestion(unittest.TestCase):
    def setUp(self):
        self.mock_engine = MagicMock()
        # Mock process_file to simulate slow IO/Processing
        self.mock_engine.process_file.side_effect = lambda content, source_name: time.sleep(0.1)
        self.folder_path = "/tmp/test_vault"
        self.files = [f"/tmp/test_vault/note_{i}.md" for i in range(10)]

    def test_performance_gain(self):
        # Sequential Execution
        start_time_seq = time.time()
        # Note: We patch open and relpath globally for the block
        with patch("builtins.open", unittest.mock.mock_open(read_data="content")):
            with patch("os.path.relpath", side_effect=lambda p, f: p):
                 for file_path in self.files:
                    process_single_file(file_path, self.folder_path, self.mock_engine)
        duration_seq = time.time() - start_time_seq

        # Parallel Execution
        start_time_par = time.time()
        with patch("builtins.open", unittest.mock.mock_open(read_data="content")):
            with patch("os.path.relpath", side_effect=lambda p, f: p):
                with ThreadPoolExecutor(max_workers=4) as executor:
                    futures = [
                        executor.submit(process_single_file, file_path, self.folder_path, self.mock_engine)
                        for file_path in self.files
                    ]
                    for future in as_completed(futures):
                        future.result()
        duration_par = time.time() - start_time_par

        print(f"\nSequential Duration: {duration_seq:.4f}s")
        print(f"Parallel Duration: {duration_par:.4f}s")

        # Expect parallel to be significantly faster (approx 4x ideal, but overhead exists)
        # 10 files * 0.1s = 1.0s sequential
        # 10 files / 4 workers * 0.1s = 0.3s parallel
        # We set a conservative threshold
        self.assertLess(duration_par, duration_seq * 0.6) # Check if at least 40% faster
