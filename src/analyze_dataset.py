"""
FasalRakshak - Crop Dataset Imbalance & Distribution Analyzer
Scans authentic PlantVillage image directories to aggregate sample counts per crop
and per disease class, highlighting underrepresented categories.
"""

import os
import sys
import json
from pathlib import Path
from collections import defaultdict
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT))
import config
from src.dataset import normalize_class_name


def extract_crop_name(class_name: str) -> str:
    """Extracts base crop name from class string (e.g. 'Tomato___Early_blight' -> 'Tomato')."""
    if "___" in class_name:
        return class_name.split("___", 1)[0]
    return class_name


def scan_dataset(root_dir: Path) -> dict:
    """
    Scans dataset directory and returns file paths grouped by normalized class name.
    """
    class_images = defaultdict(list)
    search_dir = root_dir

    if (root_dir / "raw" / "color").exists():
        search_dir = root_dir / "raw" / "color"
    elif (root_dir / "color").exists():
        search_dir = root_dir / "color"

    valid_extensions = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}

    for item in search_dir.iterdir():
        if item.is_dir():
            norm_name = normalize_class_name(item.name)
            for f in item.glob("*.*"):
                if f.suffix.lower() in valid_extensions:
                    class_images[norm_name].append(str(f))

    return dict(class_images)


def analyze_dataset_distribution(dataset_path: Path = None, export_plot: bool = True) -> dict:
    """
    Analyzes dataset counts per crop and per class, generates metrics, and identifies underrepresented categories.
    """
    if dataset_path is None:
        dataset_path = config.DATA_DIR / "plant_village"
        if not dataset_path.exists() or len(list(dataset_path.glob("*"))) == 0:
            dataset_path = config.DATA_DIR / "sample_leaves"

    print(f"\n{'='*75}")
    print(f"  FASALRAKSHAK DATASET DISTRIBUTION ANALYSIS")
    print(f"  Target Directory: {dataset_path}")
    print(f"{'='*75}\n")

    class_images = scan_dataset(dataset_path)

    if not class_images:
        print("[WARNING] No valid crop leaf images discovered in target directory.")
        return {}

    # Aggregations
    crop_counts = defaultdict(int)
    crop_classes = defaultdict(list)
    class_counts = {}

    total_images = sum(len(imgs) for imgs in class_images.values())

    for cls_name, img_list in class_images.items():
        count = len(img_list)
        class_counts[cls_name] = count
        crop = extract_crop_name(cls_name)
        crop_counts[crop] += count
        crop_classes[crop].append(cls_name)

    crop_names = sorted(crop_counts.keys())
    counts_array = np.array([crop_counts[c] for c in crop_names])
    mean_per_crop = float(np.mean(counts_array))
    median_per_crop = float(np.median(counts_array))

    # Identify underrepresented crops (less than 50% of the mean crop volume)
    underrep_threshold = mean_per_crop * 0.5
    underrepresented_crops = [c for c in crop_names if crop_counts[c] < underrep_threshold]

    # Display Crop Summary Table
    print("┌" + "─" * 25 + "┬" + "─" * 14 + "┬" + "─" * 12 + "┬" + "─" * 12 + "┬" + "─" * 18 + "┐")
    print(f"│ {'CROP NAME':<23} │ {'IMAGE COUNT':<12} │ {'PERCENTAGE':<10} │ {'CLASSES':<10} │ {'STATUS':<16} │")
    print("├" + "─" * 25 + "┼" + "─" * 14 + "┼" + "─" * 12 + "┼" + "─" * 12 + "┼" + "─" * 18 + "┤")

    for crop in sorted(crop_counts.keys(), key=lambda k: crop_counts[k], reverse=True):
        count = crop_counts[crop]
        pct = (count / total_images) * 100.0 if total_images > 0 else 0
        n_classes = len(crop_classes[crop])
        status = "⚠️ Underrep." if crop in underrepresented_crops else "✅ Adequate"
        print(f"│ {crop:<23} │ {count:>12,d} │ {pct:>9.2f}% │ {n_classes:>10d} │ {status:<16} │")

    print("└" + "─" * 25 + "┴" + "─" * 14 + "┴" + "─" * 12 + "┴" + "─" * 12 + "┴" + "─" * 18 + "┘")

    print(f"\n[SUMMARY STATISTICS]")
    print(f"  • Total Images Indexed: {total_images:,d}")
    print(f"  • Distinct Crops: {len(crop_counts)}")
    print(f"  • Distinct Disease Classes: {len(class_counts)}")
    print(f"  • Mean Images / Crop: {mean_per_crop:,.1f}")
    print(f"  • Median Images / Crop: {median_per_crop:,.1f}")
    print(f"  • Underrepresented Crops (< {underrep_threshold:,.0f} images): {underrepresented_crops or 'None (Well Balanced)'}")

    # Export JSON report
    report_data = {
        "dataset_path": str(dataset_path),
        "total_images": total_images,
        "crop_counts": dict(crop_counts),
        "class_counts": class_counts,
        "mean_per_crop": mean_per_crop,
        "median_per_crop": median_per_crop,
        "underrepresented_threshold": underrep_threshold,
        "underrepresented_crops": underrepresented_crops
    }

    out_json = config.DATA_DIR / "dataset_summary.json"
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=2)
    print(f"\n[SAVED] Dataset distribution report saved to: {out_json}")

    # Generate Visualization Plot
    if export_plot:
        try:
            import matplotlib
            matplotlib.use("Agg")
            import matplotlib.pyplot as plt

            plt.figure(figsize=(12, 6))
            sorted_crops = sorted(crop_counts.keys(), key=lambda k: crop_counts[k], reverse=True)
            counts = [crop_counts[c] for c in sorted_crops]
            colors = ["#e06666" if c in underrepresented_crops else "#6aa84f" for c in sorted_crops]

            bars = plt.bar(sorted_crops, counts, color=colors, edgecolor="#333333", linewidth=0.8)
            plt.axhline(mean_per_crop, color="#cc0000", linestyle="--", linewidth=1.5, label=f"Mean ({mean_per_crop:.0f})")
            plt.axhline(underrep_threshold, color="#ff9900", linestyle=":", linewidth=1.5, label=f"Underrep. Threshold ({underrep_threshold:.0f})")

            plt.title("FasalRakshak - Plant Leaf Images Distribution by Crop", fontsize=14, fontweight="bold", pad=12)
            plt.xlabel("Crop Category", fontsize=11, fontweight="bold")
            plt.ylabel("Total Images", fontsize=11, fontweight="bold")
            plt.xticks(rotation=40, ha="right", fontsize=10)
            plt.grid(axis="y", linestyle="--", alpha=0.5)
            plt.legend(frameon=True, facecolor="#ffffff", framealpha=0.9)

            for bar in bars:
                height = bar.get_height()
                plt.text(bar.get_x() + bar.get_width() / 2.0, height + max(counts) * 0.01, f"{int(height):,}", ha="center", va="bottom", fontsize=8, rotation=0)

            plt.tight_layout()
            out_plot = config.MODELS_DIR / "dataset_distribution.png"
            config.MODELS_DIR.mkdir(parents=True, exist_ok=True)
            plt.savefig(out_plot, dpi=200)
            plt.close()
            print(f"[SAVED] Crop distribution chart saved to: {out_plot}")
        except Exception as e:
            print(f"[WARN] Could not generate distribution plot: {e}")

    return report_data


if __name__ == "__main__":
    analyze_dataset_distribution()
