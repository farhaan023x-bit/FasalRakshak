"""
FasalRakshak - Fine-Tuning Script for Custom User Samples
Incorporates user-provided field samples into the trained model using transfer learning,
feature caching, and data augmentation while preserving knowledge across all 38 classes.
"""

import os
import sys
import time
import random
from pathlib import Path
from collections import defaultdict
from PIL import Image
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT))
import config

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader, TensorDataset
from torchvision import transforms
from sklearn.utils.class_weight import compute_class_weight

from src.model import build_model
from src.dataset import TRAIN_TRANSFORMS, VAL_TRANSFORMS, normalize_class_name


def load_model_for_finetuning(model_path: Path, device: torch.device):
    """Loads existing trained weights into FasalRakshakNet."""
    model = build_model(pretrained=False)
    if model_path.exists():
        state_dict = torch.load(model_path, map_location=device)
        if isinstance(state_dict, dict) and "state_dict" in state_dict:
            model.load_state_dict(state_dict["state_dict"])
        else:
            model.load_state_dict(state_dict)
        print(f"[Model] Successfully loaded weights from {model_path}")
    else:
        raise FileNotFoundError(f"Model weights not found at {model_path}")
    model.to(device)
    return model


def prepare_balanced_samples(user_samples_dir: Path, anchor_samples_dir: Path):
    """
    Combines new user samples with anchor images from all 38 classes to prevent catastrophic forgetting.
    Returns:
        user_samples: list of (path, class_idx)
        anchor_samples: list of (path, class_idx)
    """
    class_to_idx = {cls_name: i for i, cls_name in enumerate(config.DISEASE_CLASSES)}
    valid_exts = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}

    # 1. Collect user samples from the MoreSamples directory
    user_samples = []
    category_mapping = {
        "Healthy Tomatoes": "Tomato___healthy",
        "Tomato EarlyBlight": "Tomato___Early_blight",
        "Tomato Septoria Leaf spot": "Tomato___Septoria_leaf_spot",
    }

    for folder_name, target_class in category_mapping.items():
        folder = user_samples_dir / folder_name
        if folder.exists():
            cls_idx = class_to_idx[target_class]
            for img_p in folder.glob("*.*"):
                if img_p.suffix.lower() in valid_exts:
                    user_samples.append((img_p, cls_idx))

    print(f"[Data] Found {len(user_samples)} custom user samples across {len(category_mapping)} classes.")

    # 2. Collect anchor samples from existing dataset (sample_leaves) across all classes
    anchor_samples = []
    if anchor_samples_dir.exists():
        for folder in anchor_samples_dir.iterdir():
            if folder.is_dir():
                norm_name = normalize_class_name(folder.name)
                if norm_name in class_to_idx:
                    cls_idx = class_to_idx[norm_name]
                    class_imgs = [p for p in folder.glob("*.*") if p.suffix.lower() in valid_exts and "user_sample" not in p.name]
                    # Take up to 12 anchor images per class
                    selected = class_imgs[:12]
                    for p in selected:
                        anchor_samples.append((p, cls_idx))

    print(f"[Data] Found {len(anchor_samples)} anchor samples across existing classes to preserve generalization.")
    return user_samples, anchor_samples


def extract_features_with_augmentation(backbone, user_samples, anchor_samples, device, augment_repeats=20):
    """
    Extracts deep pooled 1792-dim embeddings from the EfficientNet backbone.
    Applies strong data augmentation repeats for user samples to ensure high representation.
    """
    backbone.eval()
    all_features = []
    all_labels = []

    print(f"\n[Feature Extraction] Extracting anchor sample embeddings ({len(anchor_samples)} images)...")
    with torch.no_grad():
        for p, lbl in anchor_samples:
            try:
                img = Image.open(p).convert("RGB")
                tensor_img = VAL_TRANSFORMS(img).unsqueeze(0).to(device)
                feat = backbone.features(tensor_img)
                feat = backbone.avgpool(feat)
                feat = torch.flatten(feat, 1)
                all_features.append(feat.cpu())
                all_labels.append(lbl)
            except Exception as e:
                print(f"Error loading {p}: {e}")

    print(f"[Feature Extraction] Applying {augment_repeats}x augmentation on user samples ({len(user_samples)} images -> {len(user_samples) * augment_repeats} features)...")
    with torch.no_grad():
        for p, lbl in user_samples:
            try:
                img = Image.open(p).convert("RGB")
                for _ in range(augment_repeats):
                    aug_tensor = TRAIN_TRANSFORMS(img).unsqueeze(0).to(device)
                    feat = backbone.features(aug_tensor)
                    feat = backbone.avgpool(feat)
                    feat = torch.flatten(feat, 1)
                    all_features.append(feat.cpu())
                    all_labels.append(lbl)
            except Exception as e:
                print(f"Error loading {p}: {e}")

    feats_cat = torch.cat(all_features, dim=0)
    labels_cat = torch.tensor(all_labels, dtype=torch.long)
    print(f"[Feature Extraction] Total training feature vectors: {feats_cat.shape[0]}, Dim: {feats_cat.shape[1]}")
    return feats_cat, labels_cat


def run_finetuning(epochs=35, lr=8e-4, batch_size=32):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"[Fine-Tuning] Running on device: {device}")

    model_path = config.MODEL_SAVE_PATH
    user_samples_dir = Path(r"C:\Users\FARHAN\OneDrive\Desktop\MoreSamples")
    anchor_samples_dir = config.DATA_DIR / "sample_leaves"

    # 1. Load model
    model = load_model_for_finetuning(model_path, device)
    backbone = model.backbone

    # 2. Collect samples
    user_samples, anchor_samples = prepare_balanced_samples(user_samples_dir, anchor_samples_dir)

    # 3. Extract deep representations with augmentation
    feats, labels = extract_features_with_augmentation(backbone, user_samples, anchor_samples, device, augment_repeats=25)

    # Compute class weights for the active classes
    unique_labels = np.unique(labels.numpy())
    raw_weights = compute_class_weight(class_weight="balanced", classes=unique_labels, y=labels.numpy())
    full_weights = np.ones(config.NUM_CLASSES, dtype=np.float32)
    for cls_idx, w in zip(unique_labels, raw_weights):
        full_weights[cls_idx] = w
    class_weights = torch.tensor(full_weights / np.mean(full_weights), dtype=torch.float32).to(device)

    # 4. Train classifier head
    classifier = model.backbone.classifier.to(device)
    dataset = TensorDataset(feats, labels)
    loader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

    criterion = nn.CrossEntropyLoss(weight=class_weights)
    optimizer = torch.optim.AdamW(classifier.parameters(), lr=lr, weight_decay=1e-4)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs, eta_min=1e-6)

    print(f"\n[Training] Optimizing classification head for {epochs} epochs...")
    t_start = time.time()
    for ep in range(1, epochs + 1):
        classifier.train()
        total_loss = 0.0
        correct = 0
        total = 0
        for b_feats, b_labels in loader:
            b_feats, b_labels = b_feats.to(device), b_labels.to(device)
            optimizer.zero_grad()
            out = classifier(b_feats)
            loss = criterion(out, b_labels)
            loss.backward()
            optimizer.step()

            total_loss += loss.item() * b_feats.size(0)
            preds = torch.argmax(out, dim=1)
            correct += (preds == b_labels).sum().item()
            total += b_labels.size(0)

        scheduler.step()
        if ep % 5 == 0 or ep == epochs:
            acc = (correct / total) * 100
            avg_loss = total_loss / total
            print(f"  Epoch {ep:2d}/{epochs} - Loss: {avg_loss:.4f} | Training Acc: {acc:.1f}%")

    elapsed = time.time() - t_start
    print(f"[Training] Completed in {elapsed:.2f} seconds.")

    # 5. Save updated model
    torch.save(model.state_dict(), model_path)
    print(f"[Model] Saved fine-tuned model checkpoint to {model_path}")


if __name__ == "__main__":
    run_finetuning(epochs=30, lr=1e-3, batch_size=32)
