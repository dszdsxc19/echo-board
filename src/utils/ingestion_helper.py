import os
from typing import Any, Dict

def process_single_file(file_path: str, folder_path: str, ingestion_engine: Any) -> Dict[str, Any]:
    """
    Process a single file: read content, calculate relative path, and ingest.

    Args:
        file_path: Absolute path to the file.
        folder_path: Root folder path for calculating relative path.
        ingestion_engine: The ingestion engine instance.

    Returns:
        A dictionary with keys: 'status', 'file', 'chars', 'error', 'content_len_bytes'.
    """
    result = {
        "status": "pending",
        "file": "",
        "chars": 0,
        "error": None,
        "content_len_bytes": 0
    }

    try:
        relative_path = os.path.relpath(file_path, folder_path)
        result["file"] = relative_path

        # Read file content
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        result["chars"] = len(content)
        result["content_len_bytes"] = len(content.encode('utf-8'))

        # Process using engine
        ingestion_engine.process_file(content, source_name=relative_path)

        result["status"] = "success"

    except Exception as e:
        result["status"] = "error"
        result["error"] = str(e)
        # If relative path calculation failed, use file_path if available
        if not result["file"]:
            result["file"] = os.path.basename(file_path)

    return result
