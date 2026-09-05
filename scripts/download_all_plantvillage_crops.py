"""
Downloads and sets up all PlantVillage crop classes (including Cherry, Orange, Blueberry,
Grape, Peach, Pepper, Raspberry, Soybean, Strawberry, Squash).
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
PV_DIR = DATA_DIR / "plant_village"
SAMPLE_DIR = DATA_DIR / "sample_leaves"
SCRATCH_DIR = ROOT / "scratch" / "test_pv"


def setup_all_crops():
    print("[1/4] Configuring sparse-checkout for all PlantVillage crops...")
    SCRATCH_DIR.mkdir(parents=True, exist_ok=True)

    if not (SCRATCH_DIR / ".git").exists():
        print("Cloning PlantVillage repository (sparse)...")
        subprocess.run([
            "git", "clone", "--filter=blob:none", "--no-checkout", "--depth=1",
            "https://github.com/spMohanty/PlantVillage-Dataset.git", str(SCRATCH_DIR)
        ], check=True)

    # Clean up any stale git locks
    for lock in (SCRATCH_DIR / ".git").rglob("*.lock"):
        try:
            lock.unlink()
        except Exception:
            pass

    # Enable sparse checkout for all raw/color folders
    subprocess.run(["git", "-C", str(SCRATCH_DIR), "sparse-checkout", "set", "raw/color"], check=True)
    subprocess.run(["git", "-C", str(SCRATCH_DIR), "checkout"], check=True)

    src_color = SCRATCH_DIR / "raw" / "color"
    if not src_color.exists():
        raise RuntimeError("Failed to checkout raw/color directory.")

    print("[2/4] Copying all crop classes to data/plant_village...")
    PV_DIR.mkdir(parents=True, exist_ok=True)
    SAMPLE_DIR.mkdir(parents=True, exist_ok=True)

    all_folders = [d for d in src_color.iterdir() if d.is_dir()]
    print(f"Found {len(all_folders)} total crop categories in PlantVillage.")

    total_images_copied = 0
    total_samples_copied = 0

    for folder in all_folders:
        folder_name = folder.name
        # Normalize folder name
        norm_name = folder_name.replace("Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot", "Corn___Cercospora_leaf_spot")
        norm_name = norm_name.replace("Corn_(maize)___Common_rust_", "Corn___Common_rust")
        norm_name = norm_name.replace("Corn_(maize)___Northern_Leaf_Blight", "Corn___Northern_Leaf_Blight")
        norm_name = norm_name.replace("Corn_(maize)___healthy", "Corn___healthy")
        norm_name = norm_name.replace("Cherry_(including_sour)___", "Cherry___")
        norm_name = norm_name.replace("Pepper,_bell___", "Pepper_bell___")

        dest_pv = PV_DIR / norm_name
        dest_pv.mkdir(parents=True, exist_ok=True)

        dest_sample = SAMPLE_DIR / norm_name
        dest_sample.mkdir(parents=True, exist_ok=True)

        images = [f for f in folder.iterdir() if f.is_file() and f.suffix.lower() in [".jpg", ".jpeg", ".png"]]
        for img in images:
            target_file = dest_pv / img.name
            if not target_file.exists():
                shutil.copy2(img, target_file)
                total_images_copied += 1

        # Populate sample_leaves with up to 15 real photos
        for idx, img in enumerate(images[:15]):
            sample_file = dest_sample / f"real_leaf_{idx+1:02d}.jpg"
            if not sample_file.exists():
                shutil.copy2(img, sample_file)
                total_samples_copied += 1

        print(f"  + {norm_name}: {len(images)} images")

    print(f"\n[3/4] Setup completed successfully!")
    print(f"Total categories available: {len(all_folders)}")
    print(f"Total images in data/plant_village: {sum(len(list(d.glob('*.*'))) for d in PV_DIR.iterdir() if d.is_dir())}")
    print(f"Total sample folders in data/sample_leaves: {len(list(SAMPLE_DIR.iterdir()))}")


if __name__ == "__main__":
    setup_all_crops()
