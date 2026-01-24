import concurrent.futures
import os
import tempfile
from unittest.mock import MagicMock

from src.utils.ingestion_helper import process_single_file


def test_process_single_file_success():
    # Setup
    mock_engine = MagicMock()
    content = "Test content"

    with tempfile.TemporaryDirectory() as temp_dir:
        file_path = os.path.join(temp_dir, "test.md")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        # Execute
        result = process_single_file(file_path, temp_dir, mock_engine)

        # Verify
        assert result["status"] == "success"
        assert result["file"] == "test.md"
        assert result["chars"] == len(content)
        assert result["error"] is None

        # Verify engine call
        mock_engine.process_file.assert_called_once_with(content, source_name="test.md")

def test_process_single_file_error():
    # Setup
    mock_engine = MagicMock()
    mock_engine.process_file.side_effect = Exception("Processing failed")

    with tempfile.TemporaryDirectory() as temp_dir:
        file_path = os.path.join(temp_dir, "test.md")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("content")

        # Execute
        result = process_single_file(file_path, temp_dir, mock_engine)

        # Verify
        assert result["status"] == "error"
        assert result["file"] == "test.md"
        assert result["error"] == "Processing failed"

def test_concurrent_execution():
    # Setup
    mock_engine = MagicMock()

    with tempfile.TemporaryDirectory() as temp_dir:
        files = []
        for i in range(5):
            fname = f"doc_{i}.md"
            fpath = os.path.join(temp_dir, fname)
            with open(fpath, "w", encoding="utf-8") as f:
                f.write(f"Content {i}")
            files.append(fpath)

        # Execute with ThreadPoolExecutor
        results = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            future_to_file = {
                executor.submit(process_single_file, fp, temp_dir, mock_engine): fp
                for fp in files
            }

            for future in concurrent.futures.as_completed(future_to_file):
                results.append(future.result())

        # Verify
        assert len(results) == 5
        assert all(r["status"] == "success" for r in results)
        assert mock_engine.process_file.call_count == 5
