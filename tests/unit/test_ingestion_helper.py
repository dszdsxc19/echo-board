import unittest
from unittest.mock import MagicMock, patch

from src.utils.ingestion_helper import process_single_file


class TestIngestionHelper(unittest.TestCase):
    def setUp(self):
        self.mock_engine = MagicMock()
        self.folder_path = "/tmp/test_vault"
        self.file_path = "/tmp/test_vault/note.md"

    def test_process_single_file_success(self):
        content = "Hello World"

        # We need to mock os.path.relpath because we are using fake paths
        with patch("builtins.open", unittest.mock.mock_open(read_data=content)):
            with patch("os.path.relpath", return_value="note.md"):
                result = process_single_file(self.file_path, self.folder_path, self.mock_engine)

        self.assertEqual(result["status"], "✅")
        self.assertEqual(result["file"], "note.md")
        self.assertEqual(result["chars"], len(content))
        self.mock_engine.process_file.assert_called_once_with(content, source_name="note.md")

    def test_process_single_file_failure(self):
        # Mock ingestion engine to raise exception
        self.mock_engine.process_file.side_effect = Exception("Processing failed")

        content = "Hello World"
        with patch("builtins.open", unittest.mock.mock_open(read_data=content)):
             with patch("os.path.relpath", return_value="note.md"):
                result = process_single_file(self.file_path, self.folder_path, self.mock_engine)

        self.assertEqual(result["status"], "❌")
        self.assertEqual(result["error"], "Processing failed")
