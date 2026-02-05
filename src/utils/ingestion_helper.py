import os
from typing import TYPE_CHECKING, Any, Dict

if TYPE_CHECKING:
    from src.infrastructure.obsidian_loader import MemoryIngestionEngine

def process_single_file(
    file_path: str,
    folder_path: str,
    ingestion_engine: "MemoryIngestionEngine"
) -> Dict[str, Any]:
    """
    Process a single file for ingestion.
    Designed to be run in a separate thread.

    Returns a dictionary with keys:
    - status: "✅" or "❌"
    - file: relative file path
    - chars: character count
    - content_len_bytes: byte size of content
    - error: error message string or None
    """
    try:
        # Calculate relative path first as it's needed for reporting
        relative_path = os.path.relpath(file_path, folder_path)

        # Read file content
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        file_size = len(content.encode('utf-8'))

        # Process file
        # process_file returns List[LifeEvent], but we don't need to return that to the UI
        ingestion_engine.process_file(content, source_name=relative_path)

        return {
            "status": "✅",
            "file": relative_path,
            "chars": len(content),
            "content_len_bytes": file_size,
            "error": None
        }

    except Exception as e:
        # Attempt to get relative path if not already calculated
        try:
            rel_path = os.path.relpath(file_path, folder_path)
        except Exception:
            rel_path = os.path.basename(file_path)

        return {
            "status": "❌",
            "file": rel_path,
            "chars": 0,
            "content_len_bytes": 0,
            "error": str(e)
        }
