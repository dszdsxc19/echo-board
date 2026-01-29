"""Validation script for Echo-Board implementation."""

import sys
from pathlib import Path


def check_file_exists(file_path, description):
    """Check if a file exists and report status."""
    path = Path(file_path)
    if path.exists():
        print("[OK] {}: {}".format(description, file_path))
        return True
    else:
        print("[MISSING] {}: {}".format(description, file_path))
        return False


def validate_implementation():
    """Validate the implementation structure."""
    print("=" * 60)
    print("Echo-Board Implementation Validation")
    print("=" * 60)
    print()

    all_good = True

    # Check core files
    print("Core Implementation Files:")
    all_good &= check_file_exists("src/app.py", "Main Streamlit UI")
    all_good &= check_file_exists("src/core/config.py", "Configuration")
    all_good &= check_file_exists("src/core/state.py", "LangGraph State")
    all_good &= check_file_exists("src/data/loader.py", "Note Loader")
    all_good &= check_file_exists("src/data/vector_store.py", "Vector Store")
    all_good &= check_file_exists("src/agents/nodes.py", "Agent Nodes")
    all_good &= check_file_exists("src/agents/graph.py", "Agent Workflow")
    print()

    # Check models
    print("Data Models:")
    all_good &= check_file_exists("src/core/models/__init__.py", "Models Init")
    all_good &= check_file_exists("src/core/models/note.py", "Note Model")
    all_good &= check_file_exists("src/core/models/conversation.py", "Conversation Model")
    all_good &= check_file_exists("src/core/models/context.py", "Context Model")
    print()

    # Check agent prompts
    print("Agent Prompts (Simplified Chinese):")
    all_good &= check_file_exists("src/agents/prompts/archivist.txt", "Archivist Prompt")
    all_good &= check_file_exists("src/agents/prompts/strategist.txt", "Strategist Prompt")
    all_good &= check_file_exists("src/agents/prompts/coach.txt", "Coach Prompt")
    print()

    # Check configuration
    print("Configuration Files:")
    all_good &= check_file_exists(".env.example", "Environment Template")
    all_good &= check_file_exists("pyproject.toml", "Python Project Config")
    all_good &= check_file_exists(".gitignore", "Git Ignore")
    print()

    # Check documentation
    print("Documentation:")
    all_good &= check_file_exists("README.md", "README")
    all_good &= check_file_exists("specs/001-personal-board-app/spec.md", "Feature Spec")
    all_good &= check_file_exists("specs/001-personal-board-app/tasks.md", "Tasks")
    print()

    # Summary
    print("=" * 60)
    if all_good:
        print("[SUCCESS] All required files present!")
        print()
        print("IMPORTANT: Use python3 (not python) for this project!")
        print()
        print("Next steps:")
        print("1. Verify Python 3.10+: python3 --version")
        print("2. Copy .env.example to .env and add your API key")
        print("3. Install: python3 -m pip install -e .")
        print("4. Initialize: python3 -m src.data.init_db")
        print("5. Run: python3 -m streamlit run src/app.py")
        return 0
    else:
        print("[ERROR] Some files are missing!")
        print("Please complete all tasks before running the application.")
        return 1


if __name__ == "__main__":
    sys.exit(validate_implementation())
