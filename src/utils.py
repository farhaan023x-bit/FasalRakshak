import cv2
import numpy as np
from pathlib import Path
import random

# -----------------------------------------------------------------------------
# Basic image loading utilities
# -----------------------------------------------------------------------------

def load_image(path: str | Path) -> np.ndarray:
    """Load an image from *path* and convert it to RGB uint8.
    Returns a NumPy array of shape (H, W, 3).
    """
    img = cv2.imread(str(path), cv2.IMREAD_COLOR)
    if img is None:
        raise FileNotFoundError(f"Image not found at {path}")
    # Convert BGR (OpenCV default) to RGB
    return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

# -----------------------------------------------------------------------------
# Augmentation helpers (used for both training and test‑time augmentation)
# -----------------------------------------------------------------------------

def random_flip(img: np.ndarray) -> np.ndarray:
    """Random horizontal flip with 50% probability."""
    if random.random() < 0.5:
        return np.fliplr(img)
    return img

def random_rotate(img: np.ndarray, max_angle: int = 15) -> np.ndarray:
    """Rotate the image by a random angle in ``[-max_angle, max_angle]``.
    The image is rotated around its centre and the canvas is expanded to keep the whole picture.
    """
    angle = random.uniform(-max_angle, max_angle)
    h, w = img.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    cos = np.abs(M[0, 0])
    sin = np.abs(M[0, 1])
    new_w = int((h * sin) + (w * cos))
    new_h = int((h * cos) + (w * sin))
    M[0, 2] += (new_w / 2) - center[0]
    M[1, 2] += (new_h / 2) - center[1]
    rotated = cv2.warpAffine(img, M, (new_w, new_h), borderMode=cv2.BORDER_REFLECT)
    return rotated

def color_jitter(img: np.ndarray, brightness: float = 0.2, contrast: float = 0.2) -> np.ndarray:
    """Apply simple brightness/contrast jitter.
    ``brightness`` and ``contrast`` are fractions of the original range.
    """
    img_f = img.astype(np.float32) / 255.0
    beta = random.uniform(-brightness, brightness)
    img_f = np.clip(img_f + beta, 0, 1)
    alpha = random.uniform(1 - contrast, 1 + contrast)
    img_f = np.clip((img_f - 0.5) * alpha + 0.5, 0, 1)
    return (img_f * 255).astype(np.uint8)

# -----------------------------------------------------------------------------
# Quality checks (blur detection, CLAHE, leaf cropping)
# -----------------------------------------------------------------------------

def detect_blur(img: np.ndarray, threshold: float = 100.0) -> bool:
    """Return ``True`` if the image is considered *sharp*.
    Uses the variance of the Laplacian; a low variance means blurry.
    """
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    var_laplacian = cv2.Laplacian(gray, cv2.CV_64F).var()
    return bool(var_laplacian >= threshold)

def apply_clahe(img: np.ndarray, clip_limit: float = 2.0, tile_grid_size: tuple[int, int] = (8, 8)) -> np.ndarray:
    """Apply CLAHE to the *L* channel of an RGB image.
    Useful for normalising illumination across leaf images.
    """
    lab = cv2.cvtColor(img, cv2.COLOR_RGB2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid_size)
    cl = clahe.apply(l)
    merged = cv2.merge((cl, a, b))
    return cv2.cvtColor(merged, cv2.COLOR_LAB2RGB)

def crop_leaf_region(img: np.ndarray, margin: int = 10) -> np.ndarray:
    """Simple contour‑based leaf cropping.
    Steps:
    1. Convert to HSV and threshold the green channel.
    2. Find the largest contour (assumed leaf).
    3. Crop to its bounding box with an optional *margin*.
    """
    hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
    lower = np.array([30, 30, 30])
    upper = np.array([90, 255, 255])
    mask = cv2.inRange(hsv, lower, upper)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return img
    leaf_contour = max(contours, key=cv2.contourArea)
    x, y, w, h = cv2.boundingRect(leaf_contour)
    x = max(x - margin, 0)
    y = max(y - margin, 0)
    w = min(w + 2 * margin, img.shape[1] - x)
    h = min(h + 2 * margin, img.shape[0] - y)
    return img[y : y + h, x : x + w]

# -----------------------------------------------------------------------------
# Mixup augmentation (image‑level)
# -----------------------------------------------------------------------------

def mixup(img1: np.ndarray, img2: np.ndarray, lam: float) -> np.ndarray:
    """Linear interpolation between two images.
    ``lam`` should be in ``[0, 1]`` and represents the weight of *img1*.
    """
    return (lam * img1 + (1 - lam) * img2).astype(np.uint8)

# -----------------------------------------------------------------------------
# Helper for test‑time augmentation (TTA)
# -----------------------------------------------------------------------------

def tta_transforms(img: np.ndarray, n: int = 5) -> list[np.ndarray]:
    """Generate *n* augmented versions of *img* for TTA.
    Currently uses random flip, rotation and color jitter.
    """
    aug_imgs = []
    for _ in range(n):
        aug = random_flip(img)
        aug = random_rotate(aug)
        aug = color_jitter(aug)
        aug_imgs.append(aug)
    return aug_imgs

# End of utils.py
