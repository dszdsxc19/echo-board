import os
from typing import Any, Dict


def process_single_file(file_path: str, folder_path: str, engine: Any) -> Dict[str, Any]:
    """
    Process a single file using the provided ingestion engine.
    Designed to be run in a thread pool.

    Args:
        file_path: Absolute path to the file.
        folder_path: Root folder path (to calculate relative path).
        engine: Instance of MemoryIngestionEngine.

    Returns:
        Dict with keys: status, file, chars, error (optional)
    """
    relative_path = os.path.relpath(file_path, folder_path)
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        file_size = len(content)

        # Call the engine to process content
        engine.process_file(content, source_name=relative_path)

        return {
            "status": "success",
            "file": relative_path,
            "chars": file_size
        }
    except Exception as e:
        return {
            "status": "error",
            "file": relative_path,
            "error": str(e)
        }
