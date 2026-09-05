"""
FasalRakshak - Model Evaluation & Performance Analytics Module
Generates detailed classification reports, per-crop error analysis, and confusion matrix heatmaps
to diagnose which crops and diseases are being confused.
"""

import os
import sys
import json
from pathlib import Path
from collections import defaultdict
import numpy as np
import torch
import torch.nn.functional as F

ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT))
import config
from src.dataset import normalize_class_name


def extract_crop_name(class_name: str) -> str:
    if "___" in class_name:
        return class_name.split("___", 1)[0]
    return class_name


def evaluate_model(
    model,
    dataloader,
    device,
    class_names=None,
    output_dir=None,
    export_plot=True,
    is_feature_loader=False
):
    """
    Evaluates model performance on validation/test dataloader.
    Computes per-class and per-crop classification reports, top-3 accuracy,
    and renders a confusion matrix heatmap.
    """
    if class_names is None:
        class_names = config.DISEASE_CLASSES
    if output_dir is None:
        output_dir = config.MODELS_DIR
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    model.eval()
    all_preds = []
    all_targets = []
    all_top3_hits = []

    print(f"\n[EVALUATION] Evaluating model performance across {len(class_names)} classes...")

    with torch.no_grad():
        for batch in dataloader:
            inputs, targets = batch[0].to(device), batch[1].to(device)

            if is_feature_loader:
                # inputs are already pooled features
                outputs = model(inputs)
            else:
                outputs = model(inputs)

            probabilities = F.softmax(outputs, dim=1)
            _, preds = torch.max(outputs, 1)

            # Top-3 predictions
            _, top3_indices = torch.topk(probabilities, k=min(3, probabilities.size(1)), dim=1)
            for target_val, top3_row in zip(targets, top3_indices):
                all_top3_hits.append(int(target_val.item() in top3_row.cpu().numpy()))

            all_preds.extend(preds.cpu().numpy().tolist())
            all_targets.extend(targets.cpu().numpy().tolist())

    y_true = np.array(all_targets)
    y_pred = np.array(all_preds)

    total_samples = len(y_true)
    top1_acc = float(np.mean(y_true == y_pred) * 100.0) if total_samples > 0 else 0.0
    top3_acc = float(np.mean(all_top3_hits) * 100.0) if all_top3_hits else 0.0

    # Scikit-learn Metrics
    from sklearn.metrics import classification_report, confusion_matrix, f1_score

    present_classes = sorted(list(set(y_true) | set(y_pred)))
    target_names = [class_names[i] for i in present_classes]

    report_dict = classification_report(
        y_true,
        y_pred,
        labels=present_classes,
        target_names=target_names,
        output_dict=True,
        zero_division=0
    )

    macro_f1 = float(f1_score(y_true, y_pred, average="macro", zero_division=0) * 100.0)
    weighted_f1 = float(f1_score(y_true, y_pred, average="weighted", zero_division=0) * 100.0)

    # 1. Per-Crop Grouped Analysis
    crop_stats = defaultdict(lambda: {"total": 0, "correct": 0, "confused_with": defaultdict(int)})

    for true_idx, pred_idx in zip(y_true, y_pred):
        true_cls = class_names[true_idx] if true_idx < len(class_names) else f"Class_{true_idx}"
        pred_cls = class_names[pred_idx] if pred_idx < len(class_names) else f"Class_{pred_idx}"

        true_crop = extract_crop_name(true_cls)
        pred_crop = extract_crop_name(pred_cls)

        crop_stats[true_crop]["total"] += 1
        if true_crop == pred_crop:
            crop_stats[true_crop]["correct"] += 1
        else:
            crop_stats[true_crop]["confused_with"][pred_crop] += 1

    # Print Terminal Report
    print("\n" + "=" * 78)
    print("  FASALRAKSHAK EVALUATION REPORT: PER-CROP ACCURACY & ERROR BREAKDOWN")
    print("=" * 78)
    print(f"  • Top-1 Accuracy:     {top1_acc:.2f}%")
    print(f"  • Top-3 Accuracy:     {top3_acc:.2f}%")
    print(f"  • Macro F1-Score:     {macro_f1:.2f}%")
    print(f"  • Weighted F1-Score:  {weighted_f1:.2f}%\n")

    print("┌" + "─" * 20 + "┬" + "─" * 12 + "┬" + "─" * 12 + "┬" + "─" * 14 + "┬" + "─" * 16 + "┐")
    print(f"│ {'CROP':<18} │ {'SAMPLES':<10} │ {'CORRECT':<10} │ {'ACCURACY':<12} │ {'PRIMARY ERROR':<14} │")
    print("├" + "─" * 20 + "┼" + "─" * 12 + "┼" + "─" * 12 + "┼" + "─" * 14 + "┼" + "─" * 16 + "┤")

    per_crop_summary = {}
    for crop in sorted(crop_stats.keys()):
        stats = crop_stats[crop]
        tot = stats["total"]
        cor = stats["correct"]
        acc = (cor / tot * 100.0) if tot > 0 else 0.0

        top_err = "None (Perfect)"
        if stats["confused_with"]:
            most_confused = max(stats["confused_with"].items(), key=lambda x: x[1])
            top_err = f"-> {most_confused[0]} ({most_confused[1]})"

        per_crop_summary[crop] = {
            "samples": tot,
            "correct": cor,
            "accuracy": round(acc, 2),
            "confused_with": dict(stats["confused_with"])
        }
        print(f"│ {crop:<18} │ {tot:>10d} │ {cor:>10d} │ {acc:>11.1f}% │ {top_err:<14} │")

    print("└" + "─" * 20 + "┴" + "─" * 12 + "┴" + "─" * 12 + "┴" + "─" * 14 + "┴" + "─" * 16 + "┘")

    # 2. Confusion Matrix Computation & Heatmap
    cm = confusion_matrix(y_true, y_pred, labels=present_classes)

    cm_path = None
    if export_plot:
        try:
            import matplotlib
            matplotlib.use("Agg")
            import matplotlib.pyplot as plt
            import seaborn as sns

            plt.figure(figsize=(16, 14))

            # Display short names for readability
            short_names = [name.replace("___", " \n ") for name in target_names]

            sns.heatmap(
                cm,
                annot=len(present_classes) <= 20,
                fmt="d",
                cmap="YlGnBu",
                xticklabels=short_names,
                yticklabels=short_names,
                cbar=True,
                linewidths=0.5,
                linecolor="#e0e0e0"
            )

            plt.title("FasalRakshak - Crop Disease Confusion Matrix Heatmap", fontsize=15, fontweight="bold", pad=15)
            plt.xlabel("Predicted Class", fontsize=12, fontweight="bold")
            plt.ylabel("Ground Truth Class", fontsize=12, fontweight="bold")
            plt.xticks(rotation=90, fontsize=8)
            plt.yticks(rotation=0, fontsize=8)
            plt.tight_layout()

            cm_path = output_dir / "confusion_matrix.png"
            plt.savefig(cm_path, dpi=200)
            plt.close()
            print(f"\n[SAVED] Confusion matrix heatmap saved to: {cm_path}")
        except Exception as e:
            print(f"[WARN] Could not render confusion matrix heatmap: {e}")

    # 3. Save Full Evaluation Report JSON
    evaluation_record = {
        "top1_accuracy": round(top1_acc, 2),
        "top3_accuracy": round(top3_acc, 2),
        "macro_f1": round(macro_f1, 2),
        "weighted_f1": round(weighted_f1, 2),
        "total_samples": total_samples,
        "per_crop_summary": per_crop_summary,
        "classification_report": report_dict,
        "confusion_matrix_path": str(cm_path) if cm_path else None
    }

    report_json_path = output_dir / "evaluation_report.json"
    with open(report_json_path, "w", encoding="utf-8") as f:
        json.dump(evaluation_record, f, indent=2)
    print(f"[SAVED] Evaluation metrics saved to: {report_json_path}")

    return evaluation_record


if __name__ == "__main__":
    print("[FasalRakshak Evaluation Module Ready]")
