import pytest
from unittest.mock import MagicMock, patch
from concurrent.futures import ThreadPoolExecutor, as_completed
import os
from src.utils.ingestion_helper import process_single_file

class TestConcurrentIngestion:

    @patch("builtins.open", new_callable=MagicMock)
    @patch("os.path.relpath")
    def test_process_single_file_success(self, mock_relpath, mock_open):
        # Setup
        mock_file = MagicMock()
        mock_file.__enter__.return_value.read.return_value = "Test content"
        mock_open.return_value = mock_file

        mock_relpath.return_value = "test.md"

        mock_engine = MagicMock()

        # Execute
        result = process_single_file("/path/to/test.md", "/path/to", mock_engine)

        # Verify
        assert result["status"] == "✅"
        assert result["file"] == "test.md"
        assert result["chars"] == 12
        mock_engine.process_file.assert_called_once_with("Test content", source_name="test.md")

    @patch("builtins.open", new_callable=MagicMock)
    @patch("os.path.relpath")
    def test_process_single_file_failure(self, mock_relpath, mock_open):
        # Setup
        mock_open.side_effect = Exception("File read error")
        mock_relpath.return_value = "error.md"

        mock_engine = MagicMock()

        # Execute
        result = process_single_file("/path/to/error.md", "/path/to", mock_engine)

        # Verify
        assert result["status"] == "❌"
        assert result["file"] == "error.md"
        assert "File read error" in result["error"]
        mock_engine.process_file.assert_not_called()

    @patch("builtins.open", new_callable=MagicMock)
    @patch("os.path.relpath")
    def test_concurrent_execution(self, mock_relpath, mock_open):
        # This tests that we can use the helper in a ThreadPoolExecutor
        mock_engine = MagicMock()
        files = ["/path/to/file1.md", "/path/to/file2.md"]
        folder_path = "/path/to"

        # Setup mocks
        mock_file = MagicMock()
        mock_file.__enter__.return_value.read.return_value = "Content"
        mock_open.return_value = mock_file

        # Simple side effect for relpath to return filename
        mock_relpath.side_effect = lambda p, f: os.path.basename(p)

        results = []
        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = {executor.submit(process_single_file, f, folder_path, mock_engine): f for f in files}

            for future in as_completed(futures):
                results.append(future.result())

        assert len(results) == 2
        assert all(r["status"] == "✅" for r in results)
        assert mock_engine.process_file.call_count == 2
        # Verify both files were processed
        file_names = [r["file"] for r in results]
        assert "file1.md" in file_names
        assert "file2.md" in file_names
