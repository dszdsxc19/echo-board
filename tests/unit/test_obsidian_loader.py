
import unittest
from unittest.mock import MagicMock
from src.infrastructure.obsidian_loader import MemoryIngestionEngine
from src.core.models.domain_models import LifeEvent

class TestMemoryIngestionEngine(unittest.TestCase):
    def setUp(self):
        self.mock_kb = MagicMock()
        self.engine = MemoryIngestionEngine(knowledge_base=self.mock_kb)
        self.engine.mem0 = MagicMock()

    def test_process_file(self):
        content = """
        # 2023-10-25 Journal
        ## Section 1
        This is some content for section 1.
        """

        events = self.engine.process_file(content, source_name="test.md")

        self.assertTrue(len(events) > 0)
        self.mock_kb.add_events.assert_called_once()
        self.engine.mem0.remember.assert_called_once_with(content)

    def test_initialization(self):
        self.assertIsNotNone(self.engine.markdown_splitter)
        self.assertIsNotNone(self.engine.text_splitter)
