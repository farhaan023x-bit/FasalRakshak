"""
FasalRakshak - Dataset Pipeline & Data Loading Module
Handles data preprocessing, PyTorch DataLoaders, image augmentation,
and synthetic sample creation for quick local testing.
"""

import os
from pathlib import Path
import torch
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
from PIL import Image, ImageDraw
import numpy as np

import sys
sys.path.append(str(Path(__file__).resolve().parent.parent))
import config

# Stronger Data Augmentations for Plant Leaf Disease Classification & Underrepresented Crops
TRAIN_TRANSFORMS = transforms.Compose([
    transforms.Resize(config.IMAGE_SIZE),
    transforms.RandomRotation(degrees=20),
    transforms.ColorJitter(brightness=0.2, contrast=0.2),
    transforms.RandomAffine(degrees=0, scale=(0.8, 1.2)),
    transforms.RandomHorizontalFlip(p=0.5),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

VAL_TRANSFORMS = transforms.Compose([
    transforms.Resize(config.IMAGE_SIZE),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])


def normalize_class_name(name: str) -> str:
    """Normalizes PlantVillage folder naming differences to match config.DISEASE_CLASSES."""
    clean = name.replace("Corn_(maize)", "Corn")
    clean = clean.replace("Cherry_(including_sour)___", "Cherry___")
    clean = clean.replace("Pepper,_bell___", "Pepper_bell___").strip()
    if clean.endswith("_"):
        clean = clean[:-1]
    if "Cercospora_leaf_spot" in clean:
        return "Corn___Cercospora_leaf_spot"
    if "Common_rust" in clean:
        return "Corn___Common_rust"
    if "Northern_Leaf_Blight" in clean:
        return "Corn___Northern_Leaf_Blight"
    if clean == "Corn___healthy":
        return "Corn___healthy"
    return clean


class CropLeafDataset(Dataset):
    """
    Custom PyTorch Dataset for loading Crop Leaf Images from folder structure.
    Recursively scans directory or raw/color subfolder, handles naming variations,
    and supports explicit image_paths/labels lists for clean train/val splits.
    """
    def __init__(self, root_dir=None, image_paths=None, labels=None, transform=None):
        self.transform = transform
        self.image_paths = []
        self.labels = []
        self.class_to_idx = {cls_name: i for i, cls_name in enumerate(config.DISEASE_CLASSES)}

        if image_paths is not None and labels is not None:
            self.image_paths = list(image_paths)
            self.labels = list(labels)
        elif root_dir is not None:
            root_path = Path(root_dir)
            if not root_path.exists():
                return

            # Check if dataset is in raw/color subfolder
            if (root_path / "raw" / "color").exists():
                search_dir = root_path / "raw" / "color"
            elif (root_path / "color").exists():
                search_dir = root_path / "color"
            else:
                search_dir = root_path

            for folder in search_dir.iterdir():
                if folder.is_dir():
                    norm_name = normalize_class_name(folder.name)
                    if norm_name in self.class_to_idx:
                        label_idx = self.class_to_idx[norm_name]
                        for img_file in folder.glob("*.*"):
                            if img_file.suffix.lower() in [".jpg", ".jpeg", ".png", ".bmp"]:
                                self.image_paths.append(img_file)
                                self.labels.append(label_idx)

    def __len__(self):
        return len(self.image_paths)

    def __getitem__(self, idx):
        img_path = self.image_paths[idx]
        image = Image.open(img_path).convert("RGB")
        label = self.labels[idx]

        if self.transform:
            image = self.transform(image)

        return image, label


def get_train_val_datasets(root_dir, val_split=0.2, seed=42):
    """
    Creates separate train and val CropLeafDataset instances with stratified split by class/crop
    and independent data augmentations.
    """
    from sklearn.model_selection import train_test_split

    full_ds = CropLeafDataset(root_dir=root_dir)
    if len(full_ds) == 0:
        raise ValueError(f"No valid images found in {root_dir}")

    train_paths, val_paths, train_labels, val_labels = train_test_split(
        full_ds.image_paths,
        full_ds.labels,
        test_size=val_split,
        stratify=full_ds.labels,
        random_state=seed
    )

    train_ds = CropLeafDataset(image_paths=train_paths, labels=train_labels, transform=TRAIN_TRANSFORMS)
    val_ds = CropLeafDataset(image_paths=val_paths, labels=val_labels, transform=VAL_TRANSFORMS)

    return train_ds, val_ds


def create_synthetic_sample_dataset():
    """
    Generates synthetic leaf images for rapid testing without requiring huge downloads.
    """
    sample_dir = config.DATA_DIR / "sample_leaves"
    print(f"Creating synthetic sample dataset at: {sample_dir}")

    for cls_name in config.DISEASE_CLASSES[:5]:  # Create samples for first 5 classes
        cls_folder = sample_dir / cls_name
        cls_folder.mkdir(parents=True, exist_ok=True)

        for i in range(3):
            # Create synthetic leaf image (green oval with spot)
            img = Image.new("RGB", (256, 256), color=(240, 240, 240))
            draw = ImageDraw.Draw(img)
            
            # Base Leaf shape
            draw.ellipse([40, 30, 216, 226], fill=(34, 139, 34))
            
            # Disease spot if not healthy
            if "healthy" not in cls_name:
                draw.ellipse([90, 80, 150, 140], fill=(139, 69, 19))
                draw.ellipse([110, 120, 170, 170], fill=(100, 50, 20))

            img_path = cls_folder / f"sample_{i+1}.jpg"
            img.save(img_path)

    print("Synthetic sample dataset created successfully.")
    return sample_dir


if __name__ == "__main__":
    print("[Dataset Module] Testing Dataset Pipeline...")
    sample_path = config.DATA_DIR / "sample_leaves"
    if not sample_path.exists():
        sample_path = create_synthetic_sample_dataset()
    dataset = CropLeafDataset(sample_path, transform=VAL_TRANSFORMS)
    print(f"Loaded {len(dataset)} sample images from {sample_path}.")
    if len(dataset) > 0:
        sample_img, sample_lbl = dataset[0]
        print(f"Sample Image Tensor Shape: {sample_img.shape}, Label Index: {sample_lbl}")

