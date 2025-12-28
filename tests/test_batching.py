
import sys
import os
import unittest
from unittest.mock import MagicMock, patch

# Adjust path to import from src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock dependencies before importing modules that use them
sys.modules['src.infrastructure.mem0_service'] = MagicMock()
sys.modules['src.infrastructure.vector_store'] = MagicMock()

# Mock specific classes
mock_kb_class = MagicMock()
sys.modules['src.infrastructure.vector_store'].KnowledgeBase = mock_kb_class

mock_ups_class = MagicMock()
sys.modules['src.infrastructure.mem0_service'].UserProfileService = mock_ups_class

# Now import the class to test
from src.infrastructure.obsidian_loader import MemoryIngestionEngine
from src.core.models.domain_models import LifeEvent

class TestBatchIngestion(unittest.TestCase):
    def setUp(self):
        self.mock_kb = MagicMock()
        self.mock_mem0 = MagicMock()

        # Patch UserProfileService inside MemoryIngestionEngine
        with patch('src.infrastructure.obsidian_loader.UserProfileService', return_value=self.mock_mem0):
            self.engine = MemoryIngestionEngine(knowledge_base=self.mock_kb)

    def test_process_file_no_persist(self):
        content = "# Title\nSome content."
        # Call with persist=False
        events = self.engine.process_file(content, source_name="test.md", persist=False)

        # Verify events returned
        self.assertTrue(len(events) > 0)

        # Verify add_events NOT called
        self.mock_kb.add_events.assert_not_called()

        # Verify mem0.remember called (as it is not batched yet)
        self.mock_mem0.remember.assert_called_once()

    def test_save_events(self):
        events = [MagicMock(spec=LifeEvent), MagicMock(spec=LifeEvent)]
        self.engine.save_events(events)
        self.mock_kb.add_events.assert_called_once_with(events)

    def test_ui_batch_logic_simulation(self):
        # Simulate the loop in app_ui.py
        batched_events = []
        BATCH_THRESHOLD = 5

        # Mock process_file to return 2 events each time
        with patch.object(self.engine, 'process_file') as mock_process:
            mock_events = [MagicMock(spec=LifeEvent), MagicMock(spec=LifeEvent)]
            mock_process.return_value = mock_events

            # Reset kb mock
            self.mock_kb.add_events.reset_mock()

            # Simulate processing 10 files
            for i in range(10):
                events = self.engine.process_file("content", source_name=f"file{i}.md", persist=False)
                if events:
                    batched_events.extend(events)

                if len(batched_events) >= BATCH_THRESHOLD:
                    self.engine.save_events(batched_events)
                    batched_events = []

            # Process remaining
            if batched_events:
                self.engine.save_events(batched_events)

            # Verification:
            # 10 files * 2 events = 20 events total.
            # Batch size 5.
            # Should flush 4 times (5, 5, 5, 5).

            self.assertEqual(self.mock_kb.add_events.call_count, 4)
            # Ensure total events saved is correct?
            # We can check arguments if needed, but call count is enough to prove batching works vs 10 calls.

if __name__ == '__main__':
    unittest.main()
