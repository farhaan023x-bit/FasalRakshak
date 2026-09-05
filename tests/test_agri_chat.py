import os
import unittest
from unittest.mock import patch, MagicMock

from fastapi.testclient import TestClient

# Import the FastAPI app after environment vars are set (dotenv will load .env)
from api import app

client = TestClient(app)

class TestAgriChatEndpoint(unittest.TestCase):
    @patch('api.genai.GenerativeModel.generate_content')
    def test_agri_chat_returns_answer(self, mock_generate):
        # Mock Gemini response
        mock_response = MagicMock()
        mock_response.text = "Mocked answer from Gemini."
        mock_generate.return_value = mock_response
        payload = {
            "message": "What is the best fertilizer for wheat?",
            "disease_class": "Wheat",
            "language": "English",
        }
        response = client.post('/api/agri-chat', json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data.get('success'))
        self.assertIn('answer', data)
        self.assertEqual(data['answer'], "Mocked answer from Gemini.")
        self.assertIn('retrieved', data)


if __name__ == '__main__':
    unittest.main()
