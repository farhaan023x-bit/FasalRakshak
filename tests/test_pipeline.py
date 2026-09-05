"""
Unit tests for FasalRakshak EfficientNet-B4 pipeline, dataset loading, and inference.
"""

import unittest
from pathlib import Path
import torch
import numpy as np

# Project imports
import sys
ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT))

import config
from src.model import build_model, FasalRakshakNet
from src.dataset import CropLeafDataset, normalize_class_name, get_train_val_datasets
from src.utils import load_image, detect_blur, tta_transforms, apply_clahe
from src.inference import predict_image, load_checkpoint


class TestFasalRakshakPipeline(unittest.TestCase):

    def test_01_config_classes(self):
        """Verify configuration has exactly 38 disease classes."""
        self.assertEqual(len(config.DISEASE_CLASSES), 38)
        self.assertEqual(config.IMAGE_SIZE, (380, 380))

    def test_02_model_architecture(self):
        """Verify EfficientNet-B4 builds with correct input/output dimensions."""
        model = build_model(pretrained=False)
        self.assertIsInstance(model, FasalRakshakNet)

        dummy_input = torch.randn(2, 3, 380, 380)
        output = model(dummy_input)
        self.assertEqual(output.shape, (2, 38))

    def test_03_class_normalization(self):
        """Verify PlantVillage naming variations normalize correctly."""
        self.assertEqual(normalize_class_name("Corn_(maize)___Common_rust_"), "Corn___Common_rust")
        self.assertEqual(normalize_class_name("Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot"), "Corn___Cercospora_leaf_spot")
        self.assertEqual(normalize_class_name("Tomato___Early_blight"), "Tomato___Early_blight")

    def test_04_dataset_loader(self):
        """Verify CropLeafDataset loads existing samples properly."""
        sample_path = config.DATA_DIR / "sample_leaves"
        ds = CropLeafDataset(root_dir=sample_path)
        self.assertGreater(len(ds), 0)

        img, label = ds[0]
        self.assertIsInstance(label, int)
        self.assertTrue(0 <= label < 15)

    def test_05_utils_image_processing(self):
        """Verify image loading, blur detection, CLAHE, and TTA functions."""
        sample_img_path = next((config.DATA_DIR / "sample_leaves").rglob("*.jpg"))
        img_np = load_image(sample_img_path)

        self.assertIsInstance(img_np, np.ndarray)
        self.assertEqual(len(img_np.shape), 3)
        self.assertEqual(img_np.shape[2], 3)

        # Blur check
        is_sharp = detect_blur(img_np, threshold=50.0)
        self.assertIsInstance(is_sharp, bool)

        # CLAHE
        clahe_img = apply_clahe(img_np)
        self.assertEqual(clahe_img.shape, img_np.shape)

        # TTA
        ttas = tta_transforms(img_np, n=3)
        self.assertEqual(len(ttas), 3)

    def test_06_model_checkpoint(self):
        """Verify trained model checkpoint exists and can be loaded."""
        self.assertTrue(config.MODEL_SAVE_PATH.exists(), f"Model checkpoint missing at {config.MODEL_SAVE_PATH}")
        self.assertGreater(config.MODEL_SAVE_PATH.stat().st_size, 10_000_000)

        model = build_model(pretrained=False)
        loaded_model = load_checkpoint(model, config.MODEL_SAVE_PATH)
        self.assertIsNotNone(loaded_model)

    def test_07_inference_end_to_end(self):
        """Verify end-to-end inference produces expected diagnosis structure."""
        test_img = config.DATA_DIR / "sample_leaves" / "Corn___Common_rust" / "botanical_01.jpg"
        if not test_img.exists():
            test_img = next((config.DATA_DIR / "sample_leaves").rglob("*.jpg"))

        result = predict_image(test_img, use_tta=True, top_k=3)
        self.assertIn("class", result)
        self.assertIn("crop", result)
        self.assertIn("disease", result)
        self.assertIn("confidence", result)
        self.assertIn("is_sharp", result)
        self.assertIn("top_k", result)

        self.assertTrue(0.0 <= result["confidence"] <= 1.0)
        self.assertEqual(len(result["top_k"]), 3)


if __name__ == "__main__":
    unittest.main()
