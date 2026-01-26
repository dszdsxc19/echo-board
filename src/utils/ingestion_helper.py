import os
from typing import Any, Dict


def process_single_file(file_path: str, folder_path: str, ingestion_engine: Any) -> Dict[str, Any]:
    """
    Process a single file for ingestion.
    Designed to be used with ThreadPoolExecutor.

    Args:
        file_path: Absolute path to the file.
        folder_path: Root folder path (to calculate relative path).
        ingestion_engine: The MemoryIngestionEngine instance.

    Returns:
        Dict containing processing status and metadata.
    """
    relative_path = "unknown"
    try:
        # Get relative path for source name
        if folder_path and os.path.exists(folder_path):
            relative_path = os.path.relpath(file_path, folder_path)
        else:
            relative_path = os.path.basename(file_path)

        # Read file content
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        file_size = len(content.encode('utf-8'))
        chars = len(content)

        # Process the file
        ingestion_engine.process_file(content, source_name=relative_path)

        return {
            "file": relative_path,
            "chars": chars,
            "status": "✅",
            "bytes": file_size,
            "error": None
        }
    except Exception as e:
        return {
            "file": relative_path,
            "chars": 0,
            "status": "❌",
            "bytes": 0,
            "error": str(e)
        }
