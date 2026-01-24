import os
from typing import Any, Dict


def process_single_file(file_path: str, folder_path: str, ingestion_engine: Any) -> Dict[str, Any]:
    """
    Helper function to process a single file.
    Designed to be used with ThreadPoolExecutor.

    Args:
        file_path: Absolute path to the file
        folder_path: Root folder path (to calculate relative path)
        ingestion_engine: The engine instance to process the file

    Returns:
        Dict containing status, file info, and optional error message
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        file_size = len(content.encode('utf-8'))
        relative_path = os.path.relpath(file_path, folder_path)

        # Process the file using the engine
        ingestion_engine.process_file(content, source_name=relative_path)

        return {
            "status": "success",
            "file": relative_path,
            "chars": len(content),
            "bytes": file_size,
            "error": None
        }
    except Exception as e:
        # Calculate relative path even in error case if possible
        try:
            relative_path = os.path.relpath(file_path, folder_path)
        except Exception:
            relative_path = file_path

        return {
            "status": "error",
            "file": relative_path,
            "chars": 0,
            "bytes": 0,
            "error": str(e)
        }
