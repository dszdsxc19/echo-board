import os

def process_single_file(file_path: str, folder_path: str, engine):
    """
    Process a single file: read content and ingest using the engine.
    Designed to be used with ThreadPoolExecutor.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        relative_path = os.path.relpath(file_path, folder_path)
        file_size = len(content.encode('utf-8'))

        # This is where the heavy lifting happens (embedding, vector store)
        engine.process_file(content, source_name=relative_path)

        return {
            "file": relative_path,
            "chars": len(content),
            "bytes": file_size,
            "status": "✅"
        }
    except Exception as e:
        relative_path = os.path.relpath(file_path, folder_path)
        return {
            "file": relative_path,
            "error": str(e),
            "status": "❌"
        }
