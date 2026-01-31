import logging
import os

# Configure logger just in case, though usually configured by app
logger = logging.getLogger(__name__)

def process_single_file(file_path: str, root_folder: str, engine):
    """
    Process a single file using the provided ingestion engine.

    Args:
        file_path: Absolute path to the file.
        root_folder: Root folder path to calculate relative path.
        engine: The MemoryIngestionEngine instance.

    Returns:
        dict: A dictionary containing status and stats.
    """
    try:
        # Calculate relative path for source name
        relative_path = os.path.relpath(file_path, root_folder)

        # Read file content
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Process the file content
        engine.process_file(content, source_name=relative_path)

        return {
            "status": "success",
            "file": relative_path,
            "chars": len(content),
            # We don't return bytes here to avoid the expensive encode(),
            # the UI should use os.path.getsize() for progress tracking.
        }

    except Exception as e:
        # In case something goes wrong with path calculation
        try:
            relative_path = os.path.relpath(file_path, root_folder)
        except Exception:
            relative_path = os.path.basename(file_path)

        return {
            "status": "error",
            "file": relative_path,
            "error": str(e)
        }
