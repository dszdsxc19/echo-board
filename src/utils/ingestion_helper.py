from typing import TYPE_CHECKING, Any, Dict, Optional

if TYPE_CHECKING:
    from src.infrastructure.obsidian_loader import MemoryIngestionEngine

def process_single_file(
    file_path: str,
    source_name: str,
    engine: "MemoryIngestionEngine",
    content: Optional[str] = None
) -> Dict[str, Any]:
    """
    Process a single file using the ingestion engine.
    Designed to be run in a separate thread.

    Args:
        file_path: Path to the file (used for reading if content is None).
        source_name: Name of the source (e.g. relative path).
        engine: Instance of MemoryIngestionEngine.
        content: Optional content. If provided, file read is skipped.

    Returns:
        Dict with status, file, chars, error (if any).
    """
    try:
        # Read content if not provided
        if content is None:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

        # Calculate size for stats
        content_len_bytes = len(content.encode('utf-8'))
        chars_count = len(content)

        # Process the file
        engine.process_file(content, source_name=source_name)

        return {
            "status": "success",
            "file": source_name,
            "chars": chars_count,
            "content_len_bytes": content_len_bytes
        }
    except Exception as e:
        return {
            "status": "error",
            "file": source_name,
            "error": str(e)
        }
