"""
FasalRakshak - PlantVillage Dataset Downloader & Extractor
Downloads PlantVillage dataset from HuggingFace Hub and extracts the target crop disease classes.
"""

import os
import sys
import zipfile
from pathlib import Path
from huggingface_hub import hf_hub_download

ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT))
import config
from src.dataset import normalize_class_name


def download_and_extract_plantvillage(max_samples_per_class=None):
    target_dir = config.DATA_DIR / "plant_village"
    target_dir.mkdir(parents=True, exist_ok=True)

    print("\n" + "="*65)
    print("  FasalRakshak - PlantVillage Dataset Downloader")
    print(f"  Target Directory: {target_dir}")
    print("="*65 + "\n")

    print("[1/3] Downloading PlantVillage dataset from Hugging Face Hub...")
    zip_path = hf_hub_download(
        repo_id="mohanty/PlantVillage",
        filename="data.zip",
        repo_type="dataset",
        local_dir=str(config.DATA_DIR / "_hf_cache")
    )
    print(f"  Downloaded archive to: {zip_path}")

    print("\n[2/3] Inspecting and extracting relevant crop leaf classes...")
    extracted_counts = {}
    target_classes = set(config.DISEASE_CLASSES)

    with zipfile.ZipFile(zip_path, "r") as zf:
        members = zf.namelist()
        print(f"  Total files in archive: {len(members)}")

        # Only extract from raw/color or color directory for target classes
        for member in members:
            # Look for color images
            if "raw/color/" in member or "color/" in member:
                parts = Path(member).parts
                # Identify folder name containing class
                for part in parts:
                    norm = normalize_class_name(part)
                    if norm in target_classes:
                        # This is a target class image
                        if Path(member).suffix.lower() in [".jpg", ".jpeg", ".png", ".bmp"]:
                            class_dir = target_dir / norm
                            class_dir.mkdir(parents=True, exist_ok=True)
                            
                            curr_count = extracted_counts.get(norm, 0)
                            if max_samples_per_class and curr_count >= max_samples_per_class:
                                continue
                            
                            filename = Path(member).name
                            target_file = class_dir / filename
                            
                            # Extract file directly
                            with zf.open(member) as src, open(target_file, "wb") as dst:
                                dst.write(src.read())
                            
                            extracted_counts[norm] = curr_count + 1
                        break

    print("\n[3/3] Extraction Summary:")
    total_imgs = 0
    for cls_name in sorted(config.DISEASE_CLASSES):
        count = extracted_counts.get(cls_name, 0)
        total_imgs += count
        print(f"  - {cls_name:<35}: {count:>5} images")

    print(f"\n  Total Extracted Images: {total_imgs}")
    print(f"  Dataset ready at: {target_dir}")
    print("="*65 + "\n")
    return total_imgs


if __name__ == "__main__":
    download_and_extract_plantvillage()
