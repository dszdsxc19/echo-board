import os
import tempfile
import unittest
from unittest.mock import MagicMock

from src.utils.ingestion_helper import process_single_file


class TestIngestionHelper(unittest.TestCase):
    def test_process_single_file_success(self):
        # Create a temp file
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = os.path.join(temp_dir, "test_note.md")
            content = "This is a test note."
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)

            # Mock engine
            mock_engine = MagicMock()

            # Run helper
            result = process_single_file(file_path, temp_dir, mock_engine)

            # Verify result
            self.assertEqual(result["status"], "success")
            self.assertEqual(result["file"], "test_note.md")
            self.assertEqual(result["chars"], len(content))

            # Verify engine call
            mock_engine.process_file.assert_called_once_with(content, source_name="test_note.md")

    def test_process_single_file_error(self):
        # Mock engine to raise exception
        mock_engine = MagicMock()
        mock_engine.process_file.side_effect = Exception("Processing failed")

        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = os.path.join(temp_dir, "bad_note.md")
            with open(file_path, "w", encoding="utf-8") as f:
                f.write("content")

            result = process_single_file(file_path, temp_dir, mock_engine)

            self.assertEqual(result["status"], "error")
            self.assertEqual(result["file"], "bad_note.md")
            self.assertIn("Processing failed", result["error"])

if __name__ == "__main__":
    unittest.main()
