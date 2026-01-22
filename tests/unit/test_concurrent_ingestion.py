import unittest
from unittest.mock import MagicMock, patch
from concurrent.futures import ThreadPoolExecutor
from src.infrastructure.obsidian_loader import MemoryIngestionEngine

class TestConcurrentIngestion(unittest.TestCase):
    @patch('src.infrastructure.obsidian_loader.UserProfileService')
    def test_concurrent_processing(self, MockUserProfileService):
        # Setup mocks
        self.mock_kb = MagicMock()
        mock_mem0_instance = MockUserProfileService.return_value

        # Initialize engine with mocked KB
        # MockUserProfileService will be instantiated inside __init__
        self.engine = MemoryIngestionEngine(knowledge_base=self.mock_kb)

        # Verify the engine uses the mock (it should, because UserProfileService was patched)
        # Note: In the code, self.mem0 = UserProfileService() is called in __init__.
        # Since we patched UserProfileService class, self.mem0 should be the mock instance.

        files = [f"content {i}" for i in range(10)]

        # Run in parallel
        with ThreadPoolExecutor(max_workers=4) as executor:
            # We are calling process_file
            # process_file calls kb.add_events and mem0.remember
            futures = [executor.submit(self.engine.process_file, content, f"file_{i}.md")
                       for i, content in enumerate(files)]

            for future in futures:
                result = future.result()
                self.assertIsInstance(result, list)

        # Verify calls
        # Since we had 10 files, we expect 10 calls to remember
        self.assertEqual(mock_mem0_instance.remember.call_count, 10)
        # And 10 calls to add_events (assuming all files produced events)
        # But wait, our dummy content "content i" might be split differently or produce events.
        # Let's check process_file logic. It splits by headers then by chars.
        # "content i" has no headers, so it will be one chunk.
        self.assertEqual(self.mock_kb.add_events.call_count, 10)
