"""
FasalRakshak - Dataset Verification Script
Verifies dataset integrity and displays sample counts for each supported disease class.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT))
import config
from src.dataset import CropLeafDataset


def verify_dataset(data_dir=None):
    if data_dir is None:
        pv_path = config.DATA_DIR / "plant_village"
        sample_path = config.DATA_DIR / "sample_leaves"
        if pv_path.exists() and len(CropLeafDataset(root_dir=pv_path)) > 0:
            data_dir = pv_path
        elif sample_path.exists():
            data_dir = sample_path
        else:
            data_dir = pv_path

    data_path = Path(data_dir)
    print("\n" + "="*60)
    print("  FasalRakshak - Dataset Integrity Check")
    print(f"  Target Path: {data_path}")
    print("="*60)

    if not data_path.exists():
        print(f"\n[ERROR] Dataset directory not found: {data_path}")
        return False

    dataset = CropLeafDataset(root_dir=data_path)
    total = len(dataset)
    print(f"\nTotal Valid Images Loaded: {total}")

    # Count per class
    counts = {cls: 0 for cls in config.DISEASE_CLASSES}
    for label_idx in dataset.labels:
        cls_name = config.DISEASE_CLASSES[label_idx]
        counts[cls_name] += 1

    print("\nPer-Class Breakdown:")
    missing = []
    for cls_name, cnt in counts.items():
        status = f"{cnt:>5} images" if cnt > 0 else "[MISSING]"
        if cnt == 0:
            missing.append(cls_name)
        print(f"  - {cls_name:<35}: {status}")

    print("\n" + "-"*60)
    if total == 0:
        print("[FAIL] Dataset contains 0 images.")
        return False
    elif missing:
        print(f"[WARN] {len(missing)} class(es) have no images: {', '.join(missing)}")
    else:
        print(f"[SUCCESS] All {len(config.DISEASE_CLASSES)} classes verified with active image data.")
    print("="*60 + "\n")
    return total > 0


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else None
    passed = verify_dataset(target)
    sys.exit(0 if passed else 1)
