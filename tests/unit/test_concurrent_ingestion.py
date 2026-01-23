import os
import unittest
from unittest.mock import MagicMock
import concurrent.futures

# The function to be tested (will be copied to app_ui.py)
def process_single_file(file_path: str, folder_path: str, ingestion_engine):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        file_size = len(content.encode('utf-8'))
        relative_path = os.path.relpath(file_path, folder_path)

        ingestion_engine.process_file(content, source_name=relative_path)

        return {
            "status": "success",
            "file": relative_path,
            "chars": len(content),
            "bytes": file_size
        }
    except Exception as e:
        # If relpath fails (e.g. file not in folder), use basename
        try:
            relative_path = os.path.relpath(file_path, folder_path)
        except ValueError:
            relative_path = os.path.basename(file_path)

        return {
            "status": "error",
            "file": relative_path,
            "error": str(e)
        }

class TestConcurrentIngestion(unittest.TestCase):
    def setUp(self):
        self.mock_engine = MagicMock()
        self.test_dir = "test_data_ingest"
        os.makedirs(self.test_dir, exist_ok=True)

        self.file_path = os.path.join(self.test_dir, "test.md")
        with open(self.file_path, "w", encoding="utf-8") as f:
            f.write("Hello World")

    def tearDown(self):
        if os.path.exists(self.file_path):
            os.remove(self.file_path)
        if os.path.exists(self.test_dir):
            os.rmdir(self.test_dir)

    def test_process_single_file_success(self):
        result = process_single_file(self.file_path, self.test_dir, self.mock_engine)
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["file"], "test.md")
        self.mock_engine.process_file.assert_called_once()

    def test_process_single_file_error(self):
        self.mock_engine.process_file.side_effect = Exception("Processing failed")
        result = process_single_file(self.file_path, self.test_dir, self.mock_engine)
        self.assertEqual(result["status"], "error")
        self.assertIn("Processing failed", result["error"])

    def test_parallel_execution(self):
        files = [self.file_path] * 5
        self.mock_engine.reset_mock()
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            futures = [executor.submit(process_single_file, f, self.test_dir, self.mock_engine) for f in files]
            results = [f.result() for f in futures]

        self.assertEqual(len(results), 5)
        self.assertEqual(self.mock_engine.process_file.call_count, 5)

if __name__ == "__main__":
    unittest.main()
