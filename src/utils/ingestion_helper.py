import logging
import os
from typing import TYPE_CHECKING, Any, Dict

if TYPE_CHECKING:
    from src.infrastructure.obsidian_loader import MemoryIngestionEngine

# Use a logger
logger = logging.getLogger(__name__)

def process_single_file(file_path: str, folder_path: str, engine: 'MemoryIngestionEngine') -> Dict[str, Any]:
    """
    Process a single file using the ingestion engine.
    Designed to be used in a thread-safe manner (no global state modification here).

    Args:
        file_path: Absolute path to the file.
        folder_path: Root folder path (for relative path calculation).
        engine: The MemoryIngestionEngine instance.

    Returns:
        A dictionary with status and metadata.
    """
    try:
        relative_path = os.path.relpath(file_path, folder_path)

        # Read content
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        file_size = len(content.encode('utf-8'))
        char_count = len(content)

        # Process
        engine.process_file(content, source_name=relative_path)

        return {
            "status": "success",
            "file": relative_path,
            "chars": char_count,
            "content_len_bytes": file_size,
            "error": None
        }

    except Exception as e:
        # Capture error safely
        # Ensure relative_path is defined even if os.path.relpath fails (unlikely but safe)
        try:
            relative_path = os.path.relpath(file_path, folder_path)
        except Exception:
            relative_path = os.path.basename(file_path)

        return {
            "status": "error",
            "file": relative_path,
            "chars": 0,
            "content_len_bytes": 0,
            "error": str(e)
        }
