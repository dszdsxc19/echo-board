import pytest
from unittest.mock import MagicMock
from src.utils.ingestion_helper import process_single_file

def test_process_single_file_success(tmp_path):
    # Setup
    folder = tmp_path / "vault"
    folder.mkdir()
    file_path = folder / "test.md"
    file_path.write_text("content", encoding="utf-8")

    engine = MagicMock()

    # Execute
    result = process_single_file(str(file_path), str(folder), engine)

    # Verify
    assert result["status"] == "success"
    assert result["file"] == "test.md"
    assert result["chars"] == 7
    assert result["error"] is None
    engine.process_file.assert_called_once()

def test_process_single_file_error(tmp_path):
    # Setup
    folder = tmp_path / "vault"
    folder.mkdir()
    file_path = folder / "test.md"
    file_path.write_text("content", encoding="utf-8")

    engine = MagicMock()
    engine.process_file.side_effect = Exception("Boom")

    # Execute
    result = process_single_file(str(file_path), str(folder), engine)

    # Verify
    assert result["status"] == "error"
    assert result["error"] == "Boom"
