import os
from unittest.mock import MagicMock

# Set dummy environment variables to avoid import errors
os.environ["OPEN_AI_API_KEY"] = "dummy"
os.environ["OPEN_AI_API_BASE"] = "http://dummy"
os.environ["CHAT_MODEL"] = "gpt-4-dummy"

import concurrent.futures
import tempfile
import unittest

from src.utils.ingestion_helper import process_single_file


class TestConcurrentIngestion(unittest.TestCase):
    def test_concurrent_execution(self):
        # Create multiple temp files
        with tempfile.TemporaryDirectory() as temp_dir:
            file_paths = []
            for i in range(10):
                file_path = os.path.join(temp_dir, f"note_{i}.md")
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(f"Content {i}")
                file_paths.append(file_path)

            # Mock engine
            mock_engine = MagicMock()

            # Use ThreadPoolExecutor
            results = []
            with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
                futures = []
                for file_path in file_paths:
                    futures.append(
                        executor.submit(process_single_file, file_path, temp_dir, mock_engine)
                    )

                for future in concurrent.futures.as_completed(futures):
                    results.append(future.result())

            # Verify results
            self.assertEqual(len(results), 10)
            success_count = sum(1 for r in results if r["status"] == "success")
            self.assertEqual(success_count, 10)

            # Verify engine calls
            self.assertEqual(mock_engine.process_file.call_count, 10)

if __name__ == "__main__":
    unittest.main()
