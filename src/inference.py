"""
FasalRakshak - Inference Pipeline
Loads trained EfficientNet-B4 checkpoint and runs single-image inference with confidence scoring,
top-K class probabilities, and optional test-time augmentation (TTA).
"""

import sys
import argparse
from pathlib import Path
import torch
import torch.nn.functional as F
import cv2
import numpy as np

# Add project root to sys.path
ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT))

import config
from src.model import build_model
from src.utils import load_image, tta_transforms, detect_blur, apply_clahe


def load_checkpoint(model, checkpoint_path=None):
    """Loads weights into model from checkpoint path."""
    ckpt_path = Path(checkpoint_path or config.MODEL_SAVE_PATH)
    if not ckpt_path.is_file():
        raise FileNotFoundError(f"Checkpoint not found at: {ckpt_path}. Train the model first.")
    
    state = torch.load(ckpt_path, map_location="cpu")
    if isinstance(state, dict) and "model_state_dict" in state:
        model.load_state_dict(state["model_state_dict"])
    elif isinstance(state, dict) and "state_dict" in state:
        model.load_state_dict(state["state_dict"])
    else:
        model.load_state_dict(state)
    
    model.eval()
    return model


def preprocess_image_tensor(img_rgb: np.ndarray) -> torch.Tensor:
    """Preprocesses RGB uint8 image into normalized PyTorch float tensor."""
    img_resized = cv2.resize(img_rgb, config.IMAGE_SIZE)
    img_tensor = torch.from_numpy(img_resized).permute(2, 0, 1).float() / 255.0
    mean = torch.tensor([0.485, 0.456, 0.406]).view(3, 1, 1)
    std = torch.tensor([0.229, 0.224, 0.225]).view(3, 1, 1)
    return (img_tensor - mean) / std


def predict_image(image_path: str | Path, model=None, use_tta: bool = False, top_k: int = 3) -> dict:
    """
    Runs inference on an image file.
    Returns:
      dict with:
        - class: predicted disease class
        - crop: crop name (extracted from class)
        - disease: disease name (extracted from class)
        - confidence: probability score in [0.0, 1.0]
        - is_sharp: True if image passes blur check
        - top_k: list of top k predictions with class and probability
    """
    img_path = Path(image_path)
    if not img_path.exists():
        raise FileNotFoundError(f"Image not found at: {img_path}")

    # Load and check image quality
    raw_img = load_image(img_path)
    is_sharp = detect_blur(raw_img, threshold=80.0)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    if model is None:
        model = build_model(pretrained=False)
        model = load_checkpoint(model, config.MODEL_SAVE_PATH)
    model = model.to(device)
    model.eval()

    if use_tta:
        # Test-Time Augmentation: average predictions over multiple augmented views
        augmented_views = [raw_img] + tta_transforms(raw_img, n=4)
        tensors = [preprocess_image_tensor(v) for v in augmented_views]
        batch = torch.stack(tensors).to(device)
        with torch.no_grad():
            logits = model(batch)
            all_probs = F.softmax(logits, dim=1)
            probs = torch.mean(all_probs, dim=0)
    else:
        tensor = preprocess_image_tensor(raw_img).unsqueeze(0).to(device)
        with torch.no_grad():
            logits = model(tensor)
            probs = F.softmax(logits, dim=1).squeeze(0)

    probs_np = probs.cpu().numpy()
    top_indices = np.argsort(probs_np)[::-1][:top_k]

    top_predictions = [
        {
            "class": config.DISEASE_CLASSES[i],
            "confidence": float(probs_np[i])
        }
        for i in top_indices
    ]

    best_idx = int(top_indices[0])
    best_class = config.DISEASE_CLASSES[best_idx]
    best_conf = float(probs_np[best_idx])

    if "___" in best_class:
        crop_name, disease_name = best_class.split("___", 1)
    else:
        crop_name, disease_name = "Unknown", best_class

    return {
        "class": best_class,
        "crop": crop_name,
        "disease": disease_name.replace("_", " "),
        "confidence": best_conf,
        "is_sharp": is_sharp,
        "top_k": top_predictions
    }


def main():
    parser = argparse.ArgumentParser(description="FasalRakshak Crop Disease Inference Engine")
    parser.add_argument("image_path", type=str, help="Path to leaf image file")
    parser.add_argument("--tta", action="store_true", help="Enable Test-Time Augmentation (TTA)")
    parser.add_argument("--model-path", type=str, default=None, help="Custom path to model checkpoint")
    args = parser.parse_args()

    try:
        model = build_model(pretrained=False)
        load_checkpoint(model, args.model_path)
    except Exception as e:
        print(f"[ERROR] Could not load model: {e}")
        sys.exit(1)

    result = predict_image(args.image_path, model=model, use_tta=args.tta)

    print(f"\n{'='*55}")
    print(f"  FasalRakshak Prediction Result")
    print(f"{'='*55}")
    print(f"  Image Path  : {args.image_path}")
    print(f"  Crop        : {result['crop']}")
    print(f"  Diagnosis   : {result['disease']}")
    print(f"  Full Class  : {result['class']}")
    print(f"  Confidence  : {result['confidence']:.2%}")
    print(f"  Sharpness   : {'Pass (Sharp)' if result['is_sharp'] else 'Warning (Slightly Blurry)'}")
    print(f"\n  Top Predictions:")
    for rank, item in enumerate(result['top_k'], 1):
        print(f"    {rank}. {item['class']} : {item['confidence']:.2%}")
    print(f"{'='*55}\n")


if __name__ == "__main__":
    main()
