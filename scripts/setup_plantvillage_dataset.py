"""
FasalRakshak - Authentic PlantVillage Dataset Downloader & Real Sample Populator
Checks out all 15 target crop disease classes from spMohanty/PlantVillage-Dataset,
organizes them into data/plant_village, removes synthetic/drawing samples,
and populates data/sample_leaves with verified real leaf photographs.
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT))
import config

TARGET_CLASSES_MAP = {
    "Apple___Apple_scab": "Apple___Apple_scab",
    "Apple___Black_rot": "Apple___Black_rot",
    "Apple___Cedar_apple_rust": "Apple___Cedar_apple_rust",
    "Apple___healthy": "Apple___healthy",
    "Corn___Cercospora_leaf_spot": "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot",
    "Corn___Common_rust": "Corn_(maize)___Common_rust_",
    "Corn___Northern_Leaf_Blight": "Corn_(maize)___Northern_Leaf_Blight",
    "Corn___healthy": "Corn_(maize)___healthy",
    "Potato___Early_blight": "Potato___Early_blight",
    "Potato___Late_blight": "Potato___Late_blight",
    "Potato___healthy": "Potato___healthy",
    "Tomato___Bacterial_spot": "Tomato___Bacterial_spot",
    "Tomato___Early_blight": "Tomato___Early_blight",
    "Tomato___Late_blight": "Tomato___Late_blight",
    "Tomato___healthy": "Tomato___healthy"
}


def setup_plantvillage():
    scratch_pv = ROOT / "scratch" / "test_pv"
    data_pv = config.DATA_DIR / "plant_village"
    sample_leaves = config.DATA_DIR / "sample_leaves"

    data_pv.mkdir(parents=True, exist_ok=True)

    print("=" * 65)
    print("  FasalRakshak: Setting Up Authentic PlantVillage Dataset")
    print("=" * 65)

    # 1. Ensure clone exists
    if not scratch_pv.exists() or not (scratch_pv / ".git").exists():
        print("[1/5] Initializing shallow blob-less clone of PlantVillage repo...")
        cmd_clone = [
            "git", "clone", "--depth", "1", "--filter=blob:none", "--no-checkout",
            "https://github.com/spMohanty/PlantVillage-Dataset.git", str(scratch_pv)
        ]
        subprocess.run(cmd_clone, check=True)
    else:
        print("[1/5] Using existing shallow clone at scratch/test_pv.")

    # 2. Write sparse-checkout configuration
    print("[2/5] Configuring sparse checkout for all 15 disease classes...")
    sparse_info_path = scratch_pv / ".git" / "info" / "sparse-checkout"
    sparse_info_path.parent.mkdir(parents=True, exist_ok=True)

    lines = [
        "/*\n",
        "!/*/\n",
        "/raw/\n",
        "!/raw/*/\n",
        "/raw/color/\n",
        "!/raw/color/*/\n"
    ]
    for norm_name, gh_folder in TARGET_CLASSES_MAP.items():
        lines.append(f"/raw/color/{gh_folder}/\n")

    with open(sparse_info_path, "w", encoding="utf-8") as f:
        f.writelines(lines)

    # Clean up stale index.lock if present
    lock_file = scratch_pv / ".git" / "index.lock"
    if lock_file.exists():
        try:
            lock_file.unlink()
        except Exception:
            pass

    # 3. Checkout matching files
    print("[3/5] Checking out real leaf photographs from Git repository...")
    subprocess.run(["git", "-C", str(scratch_pv), "checkout"], check=True)

    # 4. Copy to data/plant_village with standardized names
    print("[4/5] Organizing into data/plant_village...")
    source_color_dir = scratch_pv / "raw" / "color"

    total_real_images = 0
    for norm_name, gh_folder in TARGET_CLASSES_MAP.items():
        src_folder = source_color_dir / gh_folder
        dst_folder = data_pv / norm_name
        dst_folder.mkdir(parents=True, exist_ok=True)

        if not src_folder.exists():
            print(f"  [WARN] Source folder missing: {src_folder}")
            continue

        images = [f for f in src_folder.iterdir() if f.suffix.lower() in [".jpg", ".jpeg", ".png"]]
        for img in images:
            dst_file = dst_folder / img.name
            if not dst_file.exists():
                shutil.copy2(img, dst_file)
        
        count = len(list(dst_folder.glob("*.jpg"))) + len(list(dst_folder.glob("*.JPG")))
        total_real_images += count
        print(f"  [OK] {norm_name:<32}: {count:>5} real images")

    print(f"\n  Total authentic images in data/plant_village: {total_real_images}")

    # 5. Remove synthetic samples and populate sample_leaves with real leaf photos
    print("\n[5/5] Purging previous non-real/synthetic samples & updating sample library...")
    if sample_leaves.exists():
        # Remove old synthetic samples
        for item in sample_leaves.iterdir():
            if item.is_dir():
                shutil.rmtree(item)
            else:
                item.unlink()

    sample_leaves.mkdir(parents=True, exist_ok=True)

    sample_count = 0
    for norm_name in config.DISEASE_CLASSES:
        src_class_dir = data_pv / norm_name
        dst_class_dir = sample_leaves / norm_name
        dst_class_dir.mkdir(parents=True, exist_ok=True)

        available_imgs = sorted(list(src_class_dir.glob("*.jpg")) + list(src_class_dir.glob("*.JPG")))
        # Select first 15 real photos per class
        selected = available_imgs[:15]
        for idx, img in enumerate(selected):
            shutil.copy2(img, dst_class_dir / f"real_leaf_{idx+1:02d}.jpg")
            sample_count += 1

    print(f"  [OK] Successfully populated {sample_count} authentic real leaf photos into data/sample_leaves.")
    print("=" * 65 + "\n")
    return total_real_images


if __name__ == "__main__":
    setup_plantvillage()
