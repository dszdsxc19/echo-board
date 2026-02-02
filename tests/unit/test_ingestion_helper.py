import unittest
from unittest.mock import MagicMock, mock_open, patch

from src.utils.ingestion_helper import process_single_file


class TestIngestionHelper(unittest.TestCase):
    def test_process_single_file_success(self):
        # Mock engine
        mock_engine = MagicMock()
        mock_engine.process_file.return_value = []

        file_content = "Test content"
        file_path = "test.md"
        source_name = "test.md"

        # Test with content provided
        result = process_single_file(file_path, source_name, mock_engine, content=file_content)

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["file"], source_name)
        self.assertEqual(result["chars"], len(file_content))
        mock_engine.process_file.assert_called_once_with(file_content, source_name=source_name)

    def test_process_single_file_read_success(self):
        # Mock engine
        mock_engine = MagicMock()
        mock_engine.process_file.return_value = []

        file_content = "Test content read from file"
        file_path = "test_read.md"
        source_name = "test_read.md"

        # Mock open
        m = mock_open(read_data=file_content)
        with patch("builtins.open", m):
            result = process_single_file(file_path, source_name, mock_engine)

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["chars"], len(file_content))
        mock_engine.process_file.assert_called_once_with(file_content, source_name=source_name)

    def test_process_single_file_error(self):
        # Mock engine to raise exception
        mock_engine = MagicMock()
        error_msg = "Processing failed"
        mock_engine.process_file.side_effect = Exception(error_msg)

        result = process_single_file("path", "source", mock_engine, content="content")

        self.assertEqual(result["status"], "error")
        self.assertEqual(result["file"], "source")
        self.assertEqual(result["error"], error_msg)

if __name__ == "__main__":
    unittest.main()
