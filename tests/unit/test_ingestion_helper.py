import os
import tempfile
import unittest
from unittest.mock import MagicMock

from src.utils.ingestion_helper import process_single_file


class TestIngestionHelper(unittest.TestCase):
    def test_process_single_file_success(self):
        # Setup
        engine = MagicMock()
        content = "Test content"

        with tempfile.NamedTemporaryFile(mode='w', suffix=".md", delete=False, encoding='utf-8') as tmp:
            tmp.write(content)
            tmp_path = tmp.name

        root_folder = os.path.dirname(tmp_path)
        expected_relative_path = os.path.basename(tmp_path)

        try:
            # Execute
            result = process_single_file(tmp_path, root_folder, engine)

            # Verify
            self.assertEqual(result['status'], 'success')
            self.assertEqual(result['file'], expected_relative_path)
            self.assertEqual(result['chars'], len(content))

            engine.process_file.assert_called_once()
            args, kwargs = engine.process_file.call_args
            self.assertEqual(args[0], content)
            self.assertEqual(kwargs['source_name'], expected_relative_path)

        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    def test_process_single_file_error(self):
        # Setup
        engine = MagicMock()
        engine.process_file.side_effect = Exception("Ingestion failed")

        with tempfile.NamedTemporaryFile(mode='w', suffix=".md", delete=False, encoding='utf-8') as tmp:
            tmp.write("content")
            tmp_path = tmp.name

        root_folder = os.path.dirname(tmp_path)

        try:
            # Execute
            result = process_single_file(tmp_path, root_folder, engine)

            # Verify
            self.assertEqual(result['status'], 'error')
            self.assertIn("Ingestion failed", result['error'])

        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
