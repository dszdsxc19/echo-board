
import pytest
import os
import shutil
from unittest.mock import MagicMock, patch
from src.infrastructure.obsidian_loader import MemoryIngestionEngine
from src.infrastructure.vector_store import KnowledgeBase
from src.core.models.domain_models import LifeEvent
from langchain_core.documents import Document

# Mock dependencies
@pytest.fixture
def mock_kb():
    kb = MagicMock(spec=KnowledgeBase)
    return kb

@pytest.fixture
def mock_mem0():
    return MagicMock()

@pytest.fixture
def engine(mock_kb, mock_mem0):
    # Patch UserProfileService to avoid real instantiation which requires API keys
    with patch('src.infrastructure.obsidian_loader.UserProfileService', return_value=mock_mem0):
        engine = MemoryIngestionEngine(knowledge_base=mock_kb)
        return engine

def test_process_file_generates_deterministic_ids(engine, mock_kb):
    """Test that processing the same content twice generates events with the same IDs."""

    content = """
    # Title
    Test content here.
    """
    source_name = "test_doc.md"

    # Process first time
    events1 = engine.process_file(content, source_name=source_name)
    ids1 = [e.id for e in events1]

    # Process second time
    events2 = engine.process_file(content, source_name=source_name)
    ids2 = [e.id for e in events2]

    assert len(ids1) > 0
    assert ids1 == ids2, "IDs should be identical for same content and source"

    # Verify mock calls
    assert mock_kb.add_events.call_count == 2

def test_process_file_different_content_different_ids(engine):
    """Test that different content generates different IDs."""

    events1 = engine.process_file("Content A", source_name="doc.md")
    events2 = engine.process_file("Content B", source_name="doc.md")

    assert events1[0].id != events2[0].id

def test_process_file_different_source_different_ids(engine):
    """Test that same content from different sources generates different IDs."""

    content = "Same content"
    events1 = engine.process_file(content, source_name="doc1.md")
    events2 = engine.process_file(content, source_name="doc2.md")

    assert events1[0].id != events2[0].id
