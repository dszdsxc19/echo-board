import logging
import os
from typing import Any, Dict

# Configure logger
logger = logging.getLogger(__name__)

def process_single_file(file_path: str, folder_path: str, ingestion_engine: Any) -> Dict[str, Any]:
    """
    Processes a single markdown file using the ingestion engine.

    Args:
        file_path: Absolute path to the file.
        folder_path: Root folder path (to calculate relative path).
        ingestion_engine: The engine instance to process the content.

    Returns:
        Dict containing status, file path, chars count, and error if any.
    """
    try:
        # Calculate relative path
        relative_path = os.path.relpath(file_path, folder_path)

        # Read file content
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        file_size = len(content.encode('utf-8')) # Approximate byte size for progress

        # Process file
        ingestion_engine.process_file(content, source_name=relative_path)

        return {
            "file": relative_path,
            "chars": len(content),
            "bytes": file_size,
            "status": "✅"
        }
    except Exception as e:
        # If relative path calculation fails (e.g. file not in folder), use basename
        try:
            relative_path = os.path.relpath(file_path, folder_path)
        except Exception:
            relative_path = os.path.basename(file_path)

        return {
            "file": relative_path,
            "error": str(e),
            "status": "❌"
        }
