import os
import unittest
from unittest.mock import MagicMock, patch, mock_open
from src.utils.ingestion_helper import process_single_file

class TestIngestionHelper(unittest.TestCase):
    def test_process_single_file_success(self):
        # Mock file content
        file_path = "/path/to/file.md"
        root_path = "/path/to"
        content = "test content"

        # Mock engine
        mock_engine = MagicMock()

        # Mock open
        with patch("builtins.open", mock_open(read_data=content)):
            result = process_single_file(file_path, root_path, mock_engine)

        # Verify result
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["file"], "file.md")
        self.assertEqual(result["chars"], len(content))
        self.assertEqual(result["content_len_bytes"], len(content.encode('utf-8')))
        self.assertIsNone(result["error"])

        # Verify engine call
        mock_engine.process_file.assert_called_once_with(content, source_name="file.md")

    def test_process_single_file_error(self):
        # Mock file path
        file_path = "/path/to/file.md"
        root_path = "/path/to"

        # Mock engine to raise exception
        mock_engine = MagicMock()
        mock_engine.process_file.side_effect = Exception("Processing failed")

        # Mock open
        with patch("builtins.open", mock_open(read_data="content")):
            result = process_single_file(file_path, root_path, mock_engine)

        # Verify result
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["file"], "file.md")
        self.assertEqual(result["error"], "Processing failed")

    def test_process_single_file_io_error(self):
         # Mock file path
        file_path = "/path/to/file.md"
        root_path = "/path/to"
        mock_engine = MagicMock()

        # Mock open to raise exception
        with patch("builtins.open", side_effect=IOError("File read error")):
            result = process_single_file(file_path, root_path, mock_engine)

        # Verify result
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["error"], "File read error")
        mock_engine.process_file.assert_not_called()

if __name__ == "__main__":
    unittest.main()
