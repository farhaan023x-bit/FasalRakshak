"""
End-to-end integration tests for FasalRakshak backend endpoints.
"""

import unittest
from pathlib import Path
from fastapi.testclient import TestClient

from api import app
from src.advisory import advisory_db

class TestE2EApi(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_healthy_voice_reassurance_no_treatment(self):
        """Verify that healthy crop voice gives reassurance only and suppresses treatment."""
        script = advisory_db.get_voice_script_by_language("Tomato___healthy", "English")
        self.assertIn("healthy", script.lower())
        self.assertIn("no pesticide or treatment is needed", script.lower())
        self.assertNotIn("spray", script.lower())
        self.assertNotIn("fungicide", script.lower())

        # Test audio synthesis with this script
        res = self.client.post("/api/inworld-voice", json={
            "text": script,
            "disease_class": "Tomato___healthy",
            "language": "English"
        })
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("audio_url", data)
        self.assertTrue(data["audio_url"].endswith(".mp3"))

    def test_diseased_voice_audio(self):
        """Verify that diseased crop voice generates third-party audio URL."""
        script = advisory_db.get_voice_script_by_language("Tomato___Early_blight", "English")
        self.assertIn("treatment", script.lower())

        res = self.client.post("/api/inworld-voice", json={
            "text": script,
            "disease_class": "Tomato___Early_blight",
            "language": "English"
        })
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("audio_url", data)
        self.assertTrue(data["audio_url"].endswith(".mp3"))

    def test_agri_chat_response(self):
        """Verify that Agri-Chat generates a rich grounded answer without crashing."""
        res = self.client.post("/api/agri-chat", json={
            "message": "How to control early blight organically?",
            "disease_class": "Tomato___Early_blight",
            "language": "English"
        })
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data.get("success"))
        self.assertIn("answer", data)
        self.assertGreater(len(data["answer"]), 20)

    def test_image_prediction_real_leaf(self):
        """Verify that image prediction functions with a real leaf sample."""
        sample_img = next(Path("data/sample_leaves").rglob("*.jpg"))
        with open(sample_img, "rb") as f:
            res = self.client.post("/api/predict", files={"file": ("leaf.jpg", f, "image/jpeg")})
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data.get("success"))
        self.assertIn("prediction", data)
        self.assertIn("disease", data["prediction"])
        self.assertIn("confidence", data["prediction"])
        self.assertTrue(0.0 <= data["prediction"]["confidence"] <= 100.0)
        self.assertIn("selected_language_voice", data)


if __name__ == "__main__":
    unittest.main()
