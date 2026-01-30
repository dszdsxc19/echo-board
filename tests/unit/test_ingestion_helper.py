import os
import unittest
from unittest.mock import MagicMock, patch
from src.utils.ingestion_helper import process_single_file

class TestIngestionHelper(unittest.TestCase):

    def setUp(self):
        self.mock_engine = MagicMock()
        self.folder_path = "/tmp/test_folder"
        self.file_name = "test_file.md"
        self.file_path = os.path.join(self.folder_path, self.file_name)
        self.file_content = "This is a test content."

    def test_process_single_file_success(self):
        # Setup
        with patch("builtins.open", unittest.mock.mock_open(read_data=self.file_content)):
            with patch("os.path.relpath", return_value=self.file_name):
                # Execute
                result = process_single_file(self.mock_engine, self.file_path, self.folder_path)

        # Verify
        self.mock_engine.process_file.assert_called_once_with(self.file_content, source_name=self.file_name)
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["file"], self.file_name)
        self.assertEqual(result["chars"], len(self.file_content))
        self.assertEqual(result["file_size"], len(self.file_content.encode('utf-8')))

    def test_process_single_file_exception(self):
        # Setup
        error_message = "Test Error"
        self.mock_engine.process_file.side_effect = Exception(error_message)

        with patch("builtins.open", unittest.mock.mock_open(read_data=self.file_content)):
             with patch("os.path.relpath", return_value=self.file_name):
                # Execute
                result = process_single_file(self.mock_engine, self.file_path, self.folder_path)

        # Verify
        self.mock_engine.process_file.assert_called_once()
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["file"], self.file_name)
        self.assertEqual(result["error"], error_message)

if __name__ == '__main__':
    unittest.main()
