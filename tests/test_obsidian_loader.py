
import pytest
from unittest.mock import MagicMock, patch
from src.infrastructure.obsidian_loader import MemoryIngestionEngine
from src.core.models.domain_models import LifeEvent
from concurrent.futures import ThreadPoolExecutor

@pytest.fixture
def mock_kb():
    return MagicMock()

@pytest.fixture
def mock_mem0():
    return MagicMock()

@pytest.fixture
def engine(mock_kb, mock_mem0):
    with patch("src.infrastructure.obsidian_loader.UserProfileService", return_value=mock_mem0):
        engine = MemoryIngestionEngine(knowledge_base=mock_kb)
        return engine

def test_process_file_calls_kb_and_mem0(engine, mock_kb, mock_mem0):
    file_content = "# Title\nSome content"
    source_name = "test.md"

    # Mock splitters to return something valid
    # Since we can't easily mock the internal splitters without more patching,
    # we rely on the fact that the content is simple enough for default splitters.
    # However, to be safe and avoid "no splits" warning which might skip kb add,
    # let's ensure split_text returns something.

    # Actually, MarkdownHeaderTextSplitter with "# Title" should return 1 split.

    events = engine.process_file(file_content, source_name=source_name)

    assert len(events) > 0
    assert mock_kb.add_events.called
    assert mock_mem0.remember.called

    # Check arguments
    mock_mem0.remember.assert_called_with(file_content)

    # Check concurrent execution logic (indirectly)
    # It's hard to prove concurrency without delays, but we can verify both were called.

def test_process_file_handles_kb_error(engine, mock_kb, mock_mem0):
    mock_kb.add_events.side_effect = Exception("KB Error")

    file_content = "# Title\nSome content"

    # Should not raise exception
    engine.process_file(file_content)

    assert mock_mem0.remember.called

def test_process_file_handles_mem0_error(engine, mock_kb, mock_mem0):
    mock_mem0.remember.side_effect = Exception("Mem0 Error")

    file_content = "# Title\nSome content"

    # Should not raise exception
    engine.process_file(file_content)

    assert mock_kb.add_events.called

def test_ingest_folder(engine, mock_kb, mock_mem0, tmp_path):
    # Create dummy files
    d = tmp_path / "obsidian_vault"
    d.mkdir()
    p1 = d / "note1.md"
    p1.write_text("# Note 1\nContent 1", encoding="utf-8")
    p2 = d / "note2.md"
    p2.write_text("# Note 2\nContent 2", encoding="utf-8")

    engine.ingest_folder(str(d))

    assert mock_kb.add_events.call_count == 2
    assert mock_mem0.remember.call_count == 2
