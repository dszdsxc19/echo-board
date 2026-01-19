import unittest
from unittest.mock import MagicMock, patch

from src.core.models.domain_models import LifeEvent
from src.infrastructure.obsidian_loader import MemoryIngestionEngine


class TestMemoryIngestionEngine(unittest.TestCase):
    def setUp(self):
        self.mock_kb = MagicMock()
        self.mock_mem0 = MagicMock()

        # Patch UserProfileService to return our mock
        self.patcher = patch('src.infrastructure.obsidian_loader.UserProfileService', return_value=self.mock_mem0)
        self.MockUserProfileService = self.patcher.start()

        self.engine = MemoryIngestionEngine(knowledge_base=self.mock_kb)

    def tearDown(self):
        self.patcher.stop()

    def test_process_file_calls_kb_and_mem0(self):
        # Arrange
        content = "# 2023-10-01 Test\n## Section\nSome content."
        source = "test.md"

        # Act
        self.engine.process_file(content, source_name=source)

        # Assert
        # Check if mem0.remember was called
        self.mock_mem0.remember.assert_called_once_with(content)

        # Check if kb.add_events was called
        # process_file parses the content, so life_events will be non-empty
        self.mock_kb.add_events.assert_called_once()

        args, _ = self.mock_kb.add_events.call_args
        self.assertTrue(len(args[0]) > 0)
        self.assertIsInstance(args[0][0], LifeEvent)

    def test_process_file_handles_empty_content(self):
        # Arrange
        content = "" # Empty content might result in no events

        # Act
        self.engine.process_file(content, source_name="empty.md")

        # Assert
        self.mock_mem0.remember.assert_called_once_with(content)
        self.mock_kb.add_events.assert_not_called()

if __name__ == '__main__':
    unittest.main()
