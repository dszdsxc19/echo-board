import os
import sys
from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture
def mock_env():
    with patch.dict(os.environ, {
        "OPEN_AI_API_KEY": "sk-dummy",
        "OPEN_AI_API_BASE": "https://dummy.com",
        "CHAT_MODEL": "gpt-3.5-turbo"
    }):
        yield

@pytest.fixture
def mock_dependencies():
    # Create mocks
    mock_kb_module = MagicMock()
    mock_kb_class = MagicMock()
    mock_kb_module.KnowledgeBase = mock_kb_class

    mock_mem0_module = MagicMock()
    mock_mem0_class = MagicMock()
    mock_mem0_module.UserProfileService = mock_mem0_class

    # Mock external libs to avoid side effects during import
    modules_to_patch = {
        "src.infrastructure.vector_store": mock_kb_module,
        "src.infrastructure.mem0_service": mock_mem0_module,
        "langchain_openai": MagicMock(),
        "mem0": MagicMock(),
    }

    with patch.dict(sys.modules, modules_to_patch):
        # We need to ensure obsidian_loader is reloaded or imported fresh
        if "src.infrastructure.obsidian_loader" in sys.modules:
            del sys.modules["src.infrastructure.obsidian_loader"]

        import src.infrastructure.obsidian_loader
        yield src.infrastructure.obsidian_loader, mock_kb_class, mock_mem0_class

        # Cleanup: remove the poisoned module so other tests load the real one
        if "src.infrastructure.obsidian_loader" in sys.modules:
            del sys.modules["src.infrastructure.obsidian_loader"]

def test_process_file_calls_services(mock_env, mock_dependencies):
    obsidian_loader, mock_kb_class, mock_user_prof_class = mock_dependencies

    # Setup instances
    kb_instance = mock_kb_class.return_value
    mem0_instance = mock_user_prof_class.return_value

    # We need to ensure MemoryIngestionEngine uses our mocks.
    # It instantiates UserProfileService() in __init__.

    engine = obsidian_loader.MemoryIngestionEngine(knowledge_base=kb_instance)

    content = """
    # Title
    ## Section
    Some content here.
    """

    # Run
    engine.process_file(content, source_name="test.md")

    # Verify
    assert kb_instance.add_events.called
    assert mem0_instance.remember.called

    # Check arguments
    mem0_instance.remember.assert_called_with(content)
