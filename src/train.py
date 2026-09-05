"""
FasalRakshak - High-Performance Deep Learning Model Training Pipeline
Uses transfer learning with EfficientNet-B4 backbone pretrained on ImageNet.
Features:
1. Stronger data augmentations (Rotation, ColorJitter, Affine scaling, Flips).
2. Stratified train/val dataset splitting by crop type & class.
3. Class-weighted CrossEntropyLoss to heavily penalize minority class errors.
4. Comprehensive post-training evaluation with confusion matrix heatmap and per-crop report.
"""

import os
import sys
import json
import time
import argparse
import random
from pathlib import Path
from collections import defaultdict
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.utils.class_weight import compute_class_weight

ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT))
import config

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader, TensorDataset
from torchvision import models
from PIL import Image

from src.model import build_model, FasalRakshakNet
from src.dataset import CropLeafDataset, VAL_TRANSFORMS, TRAIN_TRANSFORMS, normalize_class_name
from src.evaluate import evaluate_model


def collect_stratified_dataset(root_dir, max_samples_per_class=250, val_split=0.2, seed=42):
    """
    Collects images from PlantVillage directory and performs a stratified split across classes.
    Ensures every crop and disease condition is proportionately represented in train and val sets.
    """
    pv_dir = Path(root_dir)
    if (pv_dir / "raw" / "color").exists():
        search_dir = pv_dir / "raw" / "color"
    elif (pv_dir / "color").exists():
        search_dir = pv_dir / "color"
    else:
        search_dir = pv_dir

    class_to_idx = {cls_name: i for i, cls_name in enumerate(config.DISEASE_CLASSES)}
    class_images = defaultdict(list)

    valid_exts = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}

    for folder in search_dir.iterdir():
        if folder.is_dir():
            norm_name = normalize_class_name(folder.name)
            if norm_name in class_to_idx:
                for img_p in folder.glob("*.*"):
                    if img_p.suffix.lower() in valid_exts:
                        class_images[norm_name].append(img_p)

    rng = random.Random(seed)
    all_paths = []
    all_labels = []

    # Subsample per-class if necessary to keep training tractable while preserving minority representation
    for cls_name in config.DISEASE_CLASSES:
        imgs = list(class_images.get(cls_name, []))
        if not imgs:
            continue
        rng.shuffle(imgs)
        if max_samples_per_class is not None and len(imgs) > max_samples_per_class:
            imgs = imgs[:max_samples_per_class]

        cls_idx = class_to_idx[cls_name]
        for p in imgs:
            all_paths.append(p)
            all_labels.append(cls_idx)

    if not all_paths:
        raise ValueError(f"No valid images found in {root_dir}")

    # Stratified Train/Val Split
    train_paths, val_paths, train_labels, val_labels = train_test_split(
        all_paths,
        all_labels,
        test_size=val_split,
        stratify=all_labels,
        random_state=seed
    )

    train_samples = list(zip(train_paths, train_labels))
    val_samples = list(zip(val_paths, val_labels))

    print(f"\n[STRATIFIED DATASET SPLIT]")
    print(f"  • Total Images Sampled: {len(all_paths)}")
    print(f"  • Training Samples:     {len(train_samples)} ({(1 - val_split)*100:.0f}%)")
    print(f"  • Validation Samples:   {len(val_samples)} ({val_split*100:.0f}%)")
    print(f"  • Classes Represented:  {len(set(all_labels))}/{len(config.DISEASE_CLASSES)}")

    return train_samples, val_samples


def compute_balanced_class_weights(train_labels: list, num_classes: int, device: torch.device) -> torch.Tensor:
    """
    Calculates balanced class weights using inverse class frequency:
    w_c = N / (C * N_c), normalized to mean 1.0.
    Heavily penalizes errors on minority/underrepresented crops.
    """
    labels_np = np.array(train_labels)
    unique_classes = np.unique(labels_np)

    raw_weights = compute_class_weight(
        class_weight="balanced",
        classes=unique_classes,
        y=labels_np
    )

    full_weights = np.ones(num_classes, dtype=np.float32)
    for cls_idx, w in zip(unique_classes, raw_weights):
        full_weights[cls_idx] = w

    # Normalize so mean weight is 1.0
    full_weights = full_weights / np.mean(full_weights)

    print(f"\n[CLASS WEIGHTS]")
    print(f"  • Computed weights for {len(unique_classes)} active classes.")
    print(f"  • Min Weight (Majority Class): {full_weights.min():.3f}")
    print(f"  • Max Weight (Minority Class): {full_weights.max():.3f}")
    print(f"  • Weight Mean: {full_weights.mean():.3f}")

    return torch.tensor(full_weights, dtype=torch.float32).to(device)


def extract_features(feature_extractor, samples, transform, device, batch_size=32):
    """
    Extracts deep 1792-dimensional pooled embeddings from EfficientNet backbone.
    """
    feature_extractor.eval()
    all_features = []
    all_labels = []

    total = len(samples)
    print(f"Extracting deep representations for {total} images...")

    for i in range(0, total, batch_size):
        batch_samples = samples[i:i + batch_size]
        tensors = []
        labels = []
        for img_path, label in batch_samples:
            try:
                img = Image.open(img_path).convert("RGB")
                tensors.append(transform(img))
                labels.append(label)
            except Exception as e:
                print(f"[WARN] Error loading {img_path}: {e}")

        if not tensors:
            continue

        batch_tensor = torch.stack(tensors).to(device)
        with torch.no_grad():
            feat = feature_extractor.features(batch_tensor)
            feat = feature_extractor.avgpool(feat)
            feat = torch.flatten(feat, 1)

        all_features.append(feat.cpu())
        all_labels.extend(labels)

        if (i // batch_size) % 15 == 0 or (i + batch_size) >= total:
            print(f"  Processed {min(i + batch_size, total)}/{total} images...")

    features_cat = torch.cat(all_features, dim=0)
    labels_cat = torch.tensor(all_labels, dtype=torch.long)
    return features_cat, labels_cat


def train_model(epochs=35, lr=0.001, batch_size=32, max_samples_per_class=200):
    """
    Executes transfer learning with class-weighted loss, stratified data splits,
    strong augmentations, and full post-training evaluation.
    """
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"[TRAIN] Training Device: {device}")

    # 1. Initialize full model with pretrained ImageNet weights
    print("[TRAIN] Initializing EfficientNet-B4 with pretrained ImageNet weights...")
    model = build_model(pretrained=True).to(device)

    # 2. Collect stratified dataset
    pv_dir = config.DATA_DIR / "plant_village"
    if not pv_dir.exists() or len(list(pv_dir.glob("*"))) == 0:
        pv_dir = config.DATA_DIR / "sample_leaves"

    train_samples, val_samples = collect_stratified_dataset(
        pv_dir,
        max_samples_per_class=max_samples_per_class,
        val_split=0.2
    )

    # 3. Calculate Class Weights
    train_labels_list = [lbl for _, lbl in train_samples]
    class_weights = compute_balanced_class_weights(
        train_labels_list,
        num_classes=config.NUM_CLASSES,
        device=device
    )

    # 4. Extract deep feature embeddings with Strong Augmentations
    backbone_base = model.backbone
    print("\n[AUGMENTATION] Applying Strong Training Augmentations (Rotation 20°, ColorJitter, RandomAffine scale 0.8-1.2, Flips)...")
    train_feats, train_labels = extract_features(backbone_base, train_samples, TRAIN_TRANSFORMS, device, batch_size=batch_size)
    val_feats, val_labels = extract_features(backbone_base, val_samples, VAL_TRANSFORMS, device, batch_size=batch_size)

    train_loader = DataLoader(TensorDataset(train_feats, train_labels), batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(TensorDataset(val_feats, val_labels), batch_size=batch_size, shuffle=False)

    # 5. Classifier Head Optimization with Weighted Loss
    classifier = model.backbone.classifier.to(device)
    criterion = nn.CrossEntropyLoss(weight=class_weights)
    optimizer = torch.optim.AdamW(classifier.parameters(), lr=lr, weight_decay=1e-4)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs, eta_min=1e-6)

    history = {
        "train_loss": [],
        "val_loss": [],
        "train_acc": [],
        "val_acc": [],
        "epoch_times": []
    }

    best_val_acc = 0.0
    best_classifier_weights = None

    print(f"\n[TRAIN] Training classifier head with Class-Weighted CrossEntropyLoss for {epochs} epochs...")
    start_time = time.time()

    for epoch in range(1, epochs + 1):
        t0 = time.time()
        classifier.train()
        running_loss = 0.0
        correct = 0
        total = 0

        for feats, labels in train_loader:
            feats, labels = feats.to(device), labels.to(device)
            optimizer.zero_grad()
            outputs = classifier(feats)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            running_loss += loss.item() * feats.size(0)
            _, preds = torch.max(outputs, 1)
            correct += (preds == labels).sum().item()
            total += labels.size(0)

        train_loss = running_loss / max(total, 1)
        train_acc = (correct / max(total, 1)) * 100.0

        # Validate
        classifier.eval()
        val_loss_sum = 0.0
        val_correct = 0
        val_total = 0

        with torch.no_grad():
            for feats, labels in val_loader:
                feats, labels = feats.to(device), labels.to(device)
                outputs = classifier(feats)
                loss = criterion(outputs, labels)
                val_loss_sum += loss.item() * feats.size(0)
                _, preds = torch.max(outputs, 1)
                val_correct += (preds == labels).sum().item()
                val_total += labels.size(0)

        val_loss = val_loss_sum / max(val_total, 1)
        val_acc = (val_correct / max(val_total, 1)) * 100.0
        scheduler.step()
        elapsed = time.time() - t0

        history["train_loss"].append(round(train_loss, 4))
        history["val_loss"].append(round(val_loss, 4))
        history["train_acc"].append(round(train_acc, 2))
        history["val_acc"].append(round(val_acc, 2))
        history["epoch_times"].append(round(elapsed, 2))

        if val_acc > best_val_acc:
            best_val_acc = val_acc
            best_classifier_weights = {k: v.cpu().clone() for k, v in classifier.state_dict().items()}

        if epoch % 5 == 0 or epoch == 1 or epoch == epochs:
            print(f"  Epoch [{epoch:02d}/{epochs:02d}] | Train Loss: {train_loss:.4f} (Acc: {train_acc:.1f}%) | Val Loss: {val_loss:.4f} (Acc: {val_acc:.1f}%) | Time: {elapsed:.2f}s")

    # Load best weights into the classifier
    if best_classifier_weights:
        classifier.load_state_dict(best_classifier_weights)
        model.backbone.classifier.load_state_dict(best_classifier_weights)

    total_time = time.time() - start_time
    print(f"\n{'='*65}")
    print(f"  Training Completed in {total_time:.1f}s")
    print(f"  Best Validation Accuracy: {best_val_acc:.2f}%")
    print(f"{'='*65}\n")

    # 6. Post-Training Detailed Evaluation & Confusion Matrix Heatmap
    evaluate_model(
        model=classifier,
        dataloader=val_loader,
        device=device,
        class_names=config.DISEASE_CLASSES,
        output_dir=config.MODELS_DIR,
        export_plot=True,
        is_feature_loader=True
    )

    # 7. Save Model Weights
    config.MODEL_SAVE_PATH.parent.mkdir(parents=True, exist_ok=True)
    torch.save(model.state_dict(), config.MODEL_SAVE_PATH)
    print(f"[SAVE] Trained model checkpoint saved to: {config.MODEL_SAVE_PATH}")

    # 8. Save Training History
    history_path = config.MODELS_DIR / "training_history.json"
    with open(history_path, "w") as f:
        json.dump(history, f, indent=2)
    print(f"[SAVE] Training metrics saved to: {history_path}")

    return model, best_val_acc


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="FasalRakshak Model Training Pipeline")
    parser.add_argument("--epochs", type=int, default=30, help="Number of training epochs")
    parser.add_argument("--lr", type=float, default=0.001, help="Learning rate")
    parser.add_argument("--batch-size", type=int, default=32, help="Batch size")
    parser.add_argument("--max-samples", type=int, default=150, help="Max samples per class for training balance")
    args = parser.parse_args()

    train_model(
        epochs=args.epochs,
        lr=args.lr,
        batch_size=args.batch_size,
        max_samples_per_class=args.max_samples
    )
