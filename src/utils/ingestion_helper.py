import os


def process_single_file(file_path: str, folder_path: str, ingestion_engine):
    """
    Process a single file using the ingestion engine.
    Designed to be used with ThreadPoolExecutor.
    """
    try:
        # Read file content
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        file_size = len(content.encode('utf-8'))
        relative_path = os.path.relpath(file_path, folder_path)

        # Process file
        ingestion_engine.process_file(content, source_name=relative_path)

        return {
            "success": True,
            "file": relative_path,
            "chars": len(content),
            "bytes": file_size,
            "status": "✅"
        }
    except Exception as e:
        relative_path = os.path.relpath(file_path, folder_path)
        return {
            "success": False,
            "file": relative_path,
            "error": str(e),
            "status": "❌"
        }
