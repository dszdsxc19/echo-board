import concurrent.futures
import os
import tempfile
import time
from unittest.mock import MagicMock

from src.utils.ingestion_helper import process_single_file


def test_process_single_file_success():
    # Setup
    mock_engine = MagicMock()
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp:
        tmp.write("Hello World")
        tmp_path = tmp.name

    try:
        # Execute
        result = process_single_file(tmp_path, os.path.dirname(tmp_path), mock_engine)

        # Verify
        assert result["success"] is True
        assert result["chars"] == 11
        assert result["status"] == "✅"
        mock_engine.process_file.assert_called_once()
        args, kwargs = mock_engine.process_file.call_args
        assert args[0] == "Hello World"
        assert kwargs["source_name"] == os.path.basename(tmp_path)

    finally:
        os.remove(tmp_path)

def test_process_single_file_failure():
    # Setup
    mock_engine = MagicMock()
    mock_engine.process_file.side_effect = Exception("Processing failed")

    with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp:
        tmp.write("Bad File")
        tmp_path = tmp.name

    try:
        # Execute
        result = process_single_file(tmp_path, os.path.dirname(tmp_path), mock_engine)

        # Verify
        assert result["success"] is False
        assert "Processing failed" in result["error"]
        assert result["status"] == "❌"

    finally:
        os.remove(tmp_path)

def test_concurrent_processing_simulation():
    """Verify that multiple files can be processed via ThreadPoolExecutor"""
    files = []
    # Create temp files
    temp_dir = tempfile.mkdtemp()
    try:
        for i in range(5):
            path = os.path.join(temp_dir, f"file_{i}.md")
            with open(path, "w") as f:
                f.write(f"Content {i}")
            files.append(path)

        mock_engine = MagicMock()
        # Add a small delay to simulate work
        def side_effect(content, source_name):
            time.sleep(0.01)
            return []
        mock_engine.process_file.side_effect = side_effect

        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            future_to_file = {
                executor.submit(process_single_file, f, temp_dir, mock_engine): f
                for f in files
            }

            results = []
            for future in concurrent.futures.as_completed(future_to_file):
                results.append(future.result())

        assert len(results) == 5
        assert all(r["success"] for r in results)
        assert mock_engine.process_file.call_count == 5

    finally:
        for f in files:
            if os.path.exists(f):
                os.remove(f)
        os.rmdir(temp_dir)
