import unittest
import sys
import os
from unittest.mock import patch, MagicMock

# Ensure the project root is on PYTHONPATH for imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

class TestHindiTranslation(unittest.TestCase):
    @patch('google.generativeai.configure')
    @patch('google.generativeai.GenerativeModel')
    def test_hindi_translation(self, mock_model_class, mock_configure):
        mock_model = MagicMock()
        mock_model.generate_content.return_value.text = "यह एक परीक्षण उत्तर है"
        mock_model_class.return_value = mock_model

        from src.advisory import FarmerAdvisoryEngine
        engine = FarmerAdvisoryEngine()
        result = engine.ask_farming_expert("How to control aphids?", language="Hindi")
        self.assertIn("यह एक परीक्षण उत्तर है", result)
        args, _ = mock_model.generate_content.call_args
        self.assertIn("Translate the following agricultural advice", args[0])

if __name__ == '__main__':
    unittest.main()
