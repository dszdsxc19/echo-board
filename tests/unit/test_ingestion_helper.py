import pytest
from unittest.mock import Mock, patch, mock_open
import os
import sys

# Ensure we can import from src
sys.path.append(os.getcwd())

from src.utils.ingestion_helper import process_single_file

def test_process_single_file_success():
    """Test successful processing of a file."""
    mock_engine = Mock()
    file_content = "Test content"
    file_path = "/abs/path/to/file.md"
    folder_path = "/abs/path/to"

    with patch("builtins.open", mock_open(read_data=file_content)):
        # We don't mock os.path.relpath generally, but here we can to control output
        # or just rely on real os.path.relpath if we set up paths correctly.
        # Let's just mock it for simplicity.
        with patch("os.path.relpath", return_value="file.md"):
             result = process_single_file(file_path, folder_path, mock_engine)

    assert result["status"] == "✅"
    assert result["file"] == "file.md"
    assert result["chars"] == len(file_content)
    assert result["content_len_bytes"] == len(file_content.encode('utf-8'))
    assert result["error"] is None

    mock_engine.process_file.assert_called_once_with(file_content, source_name="file.md")

def test_process_single_file_read_error():
    """Test error during file reading."""
    mock_engine = Mock()
    file_path = "/abs/path/to/file.md"
    folder_path = "/abs/path/to"

    with patch("builtins.open", side_effect=IOError("File not found")):
        with patch("os.path.relpath", return_value="file.md"):
            result = process_single_file(file_path, folder_path, mock_engine)

    assert result["status"] == "❌"
    assert result["error"] == "File not found"
    assert result["file"] == "file.md"
    mock_engine.process_file.assert_not_called()

def test_process_single_file_ingestion_error():
    """Test error during ingestion engine processing."""
    mock_engine = Mock()
    mock_engine.process_file.side_effect = Exception("Ingestion failed")
    file_content = "Test content"
    file_path = "/abs/path/to/file.md"
    folder_path = "/abs/path/to"

    with patch("builtins.open", mock_open(read_data=file_content)):
        with patch("os.path.relpath", return_value="file.md"):
             result = process_single_file(file_path, folder_path, mock_engine)

    assert result["status"] == "❌"
    assert result["error"] == "Ingestion failed"
    assert result["file"] == "file.md"
