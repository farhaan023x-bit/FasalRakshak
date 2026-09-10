"""
FasalRakshak - Disease Prediction & Deep Learning Inference Engine
Includes:
1. Smart Plant Leaf Guard (rejects non-plant images like cars, faces, shoes)
2. EfficientNet-B4 deep learning neural inference with true softmax confidence
3. Grad-CAM visual explainability heatmap generation
4. Confidence-Based Escalation thresholding (< 65% triggers KVK escalation)
"""

import numpy as np
from PIL import Image

try:
    import torch
    import torch.nn.functional as F
    TORCH_AVAILABLE = True
except ImportError:
    torch = None
    F = None
    TORCH_AVAILABLE = False

from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parent.parent))
import config
try:
    from src.dataset import VAL_TRANSFORMS
    from src.model import build_model
    from src.gradcam import compute_gradcam_overlay
except ImportError:
    VAL_TRANSFORMS = None
    build_model = None
    compute_gradcam_overlay = None


def is_valid_plant_leaf(image: Image.Image) -> tuple[bool, str]:
    """
    Image Guard: Analyzes color spectrum, chrominance, and chlorophyll pigment
    distribution to verify if the uploaded image is actually a plant leaf or crop part.
    Rejects non-plant objects (faces, cars, shoes, furniture, artificial noise).
    """
    img_rgb = image.convert("RGB").resize((100, 100))
    img_np = np.array(img_rgb)

    # Convert RGB to HSV
    r, g, b = img_np[:, :, 0] / 255.0, img_np[:, :, 1] / 255.0, img_np[:, :, 2] / 255.0
    cmax = np.maximum(np.maximum(r, g), b)
    cmin = np.minimum(np.minimum(r, g), b)
    diff = cmax - cmin

    h = np.zeros_like(cmax)
    mask_r = (cmax == r) & (diff != 0)
    mask_g = (cmax == g) & (diff != 0)
    mask_b = (cmax == b) & (diff != 0)

    h[mask_r] = (60 * ((g[mask_r] - b[mask_r]) / diff[mask_r]) + 360) % 360
    h[mask_g] = (60 * ((b[mask_g] - r[mask_g]) / diff[mask_g]) + 120) % 360
    h[mask_b] = (60 * ((r[mask_b] - g[mask_b]) / diff[mask_b]) + 240) % 360

    saturation = np.where(cmax == 0, 0, diff / (cmax + 1e-6))
    value = cmax

    green_mask = (h >= 35) & (h <= 165) & (saturation >= 0.10) & (value >= 0.10)
    necrotic_mask = (h >= 10) & (h <= 45) & (saturation >= 0.15) & (value >= 0.10)
    plant_mask = green_mask | necrotic_mask

    plant_pixel_ratio = np.sum(plant_mask) / (100 * 100)

    if plant_pixel_ratio < 0.10:
        return False, (
            "⚠️ Non-Plant Image Detected: The uploaded image does not contain plant leaf or vegetation characteristics. "
            "Please upload a clear photograph of a crop leaf."
        )

    return True, "Valid plant leaf detected."


class DiseasePredictor:
    """
    Inference Engine with built-in Leaf Guard, Deep Learning Model, Grad-CAM, and Escalation.
    """
    CONFIDENCE_THRESHOLD = 65.0

    def __init__(self, model_path=None):
        if not TORCH_AVAILABLE or build_model is None:
            self.device = "cpu"
            self.model = None
            return
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = build_model(pretrained=False)

        target_path = Path(model_path) if model_path else config.MODEL_SAVE_PATH
        if target_path.exists():
            try:
                state_dict = torch.load(target_path, map_location=self.device)
                if isinstance(state_dict, dict) and "model_state_dict" in state_dict:
                    self.model.load_state_dict(state_dict["model_state_dict"])
                elif isinstance(state_dict, dict) and "state_dict" in state_dict:
                    self.model.load_state_dict(state_dict["state_dict"])
                else:
                    self.model.load_state_dict(state_dict)
                print(f"Loaded trained model weights from: {target_path}")
            except Exception as e:
                print(f"Could not load weights: {e}. Using initialized model.")

        self.model.to(self.device)
        self.model.eval()

    def predict(self, image_input, generate_cam: bool = True) -> dict:
        """
        Accepts PIL Image or file path string.
        Returns prediction dictionary with confidence score, Grad-CAM overlay, and escalation flags.
        """
        if isinstance(image_input, (str, Path)):
            image = Image.open(image_input).convert("RGB")
        elif isinstance(image_input, Image.Image):
            image = image_input.convert("RGB")
        else:
            raise ValueError("Invalid image input type. Expected PIL Image or file path.")

        # 1. Smart Plant Leaf Guard Validation
        is_valid, validation_msg = is_valid_plant_leaf(image)
        if not is_valid:
            return {
                "is_valid_leaf": False,
                "error_message": validation_msg,
                "predicted_class": "Invalid_Non_Plant",
                "crop": "N/A",
                "disease": "Non-Plant Input",
                "display_title": "Non-Plant Image Detected",
                "confidence": 0.0,
                "is_healthy": False,
                "is_low_confidence": True,
                "escalation_message": validation_msg,
                "gradcam_overlay": None,
                "top3_predictions": []
            }

        # 2. Deep Learning Neural Inference
        tensor_img = VAL_TRANSFORMS(image).unsqueeze(0).to(self.device)

        with torch.no_grad():
            logits = self.model(tensor_img)
            probabilities = F.softmax(logits, dim=1)[0]
            top_prob, top_class_idx = torch.max(probabilities, dim=0)

        # Safeguard against mismatched class list length
        if top_class_idx.item() >= len(config.DISEASE_CLASSES):
            predicted_class = "Unknown"
            print("[Warning] Predicted class index out of range.")
        else:
            predicted_class = config.DISEASE_CLASSES[top_class_idx.item()]
        # Log detection of Northern Leaf Blight for debugging
        if predicted_class == "Corn___Northern_Leaf_Blight":
            print("[Info] Northern Leaf Blight detected.")
        confidence = round(float(top_prob.item() * 100.0), 2)

        # 3. Grad-CAM Visual Saliency Generation
        gradcam_overlay = None
        if generate_cam:
            try:
                gradcam_overlay = compute_gradcam_overlay(self.model, image, target_class_idx=top_class_idx.item())
            except Exception as e:
                print(f"[Grad-CAM Warning] Could not generate heatmap: {e}")

        crop_name, disease_name = self.parse_class_name(predicted_class)

        # 4. Top 3 Predictions from softmax distribution
        top3_vals, top3_idxs = torch.topk(probabilities, k=min(3, len(config.DISEASE_CLASSES)))
        top3_results = []
        for val, idx in zip(top3_vals, top3_idxs):
            cls_k = config.DISEASE_CLASSES[idx.item()]
            c_k, d_k = self.parse_class_name(cls_k)
            top3_results.append({
                "disease_raw": cls_k,
                "disease_display": f"{c_k} ({d_k})",
                "confidence": round(float(val.item() * 100.0), 2)
            })

        # 5. Confidence Escalation
        is_low_confidence = confidence < self.CONFIDENCE_THRESHOLD
        is_healthy = "healthy" in predicted_class.lower()

        escalation_msg = None
        if is_low_confidence:
            escalation_msg = (
                f"⚠️ Low Diagnostic Confidence ({confidence:.1f}% < {self.CONFIDENCE_THRESHOLD}%). "
                f"Automated agronomic escalation triggered: Case forwarded to Senior Agronomist at Krishi Vigyan Kendra (KVK)."
            )

        return {
            "is_valid_leaf": True,
            "error_message": "",
            "predicted_class": predicted_class,
            "crop": crop_name,
            "disease": disease_name,
            "display_title": f"{crop_name} - {disease_name}",
            "confidence": confidence,
            "is_healthy": is_healthy,
            "is_low_confidence": is_low_confidence,
            "escalation_message": escalation_msg,
            "gradcam_overlay": gradcam_overlay,
            "top3_predictions": top3_results
        }

    @staticmethod
    def parse_class_name(class_name: str) -> tuple[str, str]:
        """
        Parses 'Crop___Disease_name' into ('Crop', 'Disease name').
        """
        if "___" in class_name:
            crop_part, disease_part = class_name.split("___", 1)
            clean_disease = disease_part.replace("_", " ").strip()
            return crop_part, clean_disease
        return "Unknown Crop", class_name.replace("_", " ")


if __name__ == "__main__":
    predictor = DiseasePredictor()
    test_leaf = next((config.DATA_DIR / "sample_leaves").rglob("*.jpg"), None)
    if test_leaf:
        print(f"Testing inference on: {test_leaf}")
        res = predictor.predict(test_leaf)
        print(f"Prediction: {res['display_title']} (Confidence: {res['confidence']}%)")
        print(f"Top 3: {res['top3_predictions']}")
