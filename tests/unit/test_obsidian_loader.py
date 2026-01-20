
import pytest
from unittest.mock import MagicMock
from src.infrastructure.obsidian_loader import MemoryIngestionEngine
from src.core.models.domain_models import LifeEvent

def test_process_file_concurrency():
    # Mock dependencies
    mock_kb = MagicMock()
    mock_mem0 = MagicMock()

    # Instantiate engine
    engine = MemoryIngestionEngine(knowledge_base=mock_kb)
    # Inject mock mem0
    engine.mem0 = mock_mem0

    # Test input
    file_content = "# Title\nSome content"
    source_name = "test_file.md"

    # Run
    result = engine.process_file(file_content, source_name=source_name)

    # Verify calls
    # Check that add_events was called
    assert mock_kb.add_events.called
    # Check that remember was called
    mock_mem0.remember.assert_called_with(file_content)

    # Check result type
    assert isinstance(result, list)
    assert len(result) > 0
    assert isinstance(result[0], LifeEvent)
