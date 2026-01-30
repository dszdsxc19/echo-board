import os
from typing import Dict, Any

def process_single_file(engine, file_path: str, folder_path: str) -> Dict[str, Any]:
    """
    Helper function to process a single file.
    Returns a dictionary with result status to be consumed by the main thread.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        relative_path = os.path.relpath(file_path, folder_path)

        # This is the expensive blocking call
        engine.process_file(content, source_name=relative_path)

        return {
            "status": "success",
            "file": relative_path,
            "chars": len(content),
            "file_size": len(content.encode('utf-8'))
        }
    except Exception as e:
        relative_path = os.path.relpath(file_path, folder_path)
        return {
            "status": "error",
            "file": relative_path,
            "error": str(e)
        }
