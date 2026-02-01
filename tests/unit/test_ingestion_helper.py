import os
import unittest
from unittest.mock import MagicMock, mock_open, patch
from src.utils.ingestion_helper import process_single_file

class TestIngestionHelper(unittest.TestCase):

    def setUp(self):
        self.mock_engine = MagicMock()
        self.folder_path = "/tmp/obsidian"
        self.file_path = "/tmp/obsidian/note.md"
        self.relative_path = "note.md"
        self.file_content = "Test content"

    @patch("builtins.open", new_callable=mock_open, read_data="Test content")
    @patch("os.path.relpath")
    def test_process_single_file_success(self, mock_relpath, mock_file):
        # Setup
        mock_relpath.return_value = self.relative_path

        # Execute
        result = process_single_file(self.file_path, self.folder_path, self.mock_engine)

        # Verify
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["file"], self.relative_path)
        self.assertEqual(result["chars"], len(self.file_content))
        self.assertIsNone(result["error"])

        # Check calls
        mock_file.assert_called_with(self.file_path, "r", encoding="utf-8")
        self.mock_engine.process_file.assert_called_once_with(self.file_content, source_name=self.relative_path)

    @patch("builtins.open", side_effect=IOError("Read error"))
    @patch("os.path.relpath")
    def test_process_single_file_read_error(self, mock_relpath, mock_file):
        # Setup
        mock_relpath.return_value = self.relative_path

        # Execute
        result = process_single_file(self.file_path, self.folder_path, self.mock_engine)

        # Verify
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["file"], self.relative_path)
        self.assertIn("Read error", result["error"])
        self.mock_engine.process_file.assert_not_called()

    @patch("builtins.open", new_callable=mock_open, read_data="Test content")
    @patch("os.path.relpath")
    def test_process_single_file_engine_error(self, mock_relpath, mock_file):
        # Setup
        mock_relpath.return_value = self.relative_path
        self.mock_engine.process_file.side_effect = Exception("Engine failure")

        # Execute
        result = process_single_file(self.file_path, self.folder_path, self.mock_engine)

        # Verify
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["file"], self.relative_path)
        self.assertIn("Engine failure", result["error"])

if __name__ == '__main__':
    unittest.main()
