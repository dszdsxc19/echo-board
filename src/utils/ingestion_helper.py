import os
from typing import TYPE_CHECKING, Any, Dict

if TYPE_CHECKING:
    from src.infrastructure.obsidian_loader import MemoryIngestionEngine

def process_single_file(file_path: str, root_path: str, engine: "MemoryIngestionEngine") -> Dict[str, Any]:
    """
    Process a single file using the ingestion engine.
    Returns a dictionary with results.
    """
    relative_path = os.path.relpath(file_path, root_path)
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        file_size = len(content) # Characters
        file_bytes = len(content.encode('utf-8'))

        # Process the file
        engine.process_file(content, source_name=relative_path)

        return {
            "status": "success",
            "file": relative_path,
            "chars": file_size,
            "error": None,
            "content_len_bytes": file_bytes
        }
    except Exception as e:
        return {
            "status": "error",
            "file": relative_path,
            "chars": 0,
            "error": str(e),
            "content_len_bytes": 0
        }
