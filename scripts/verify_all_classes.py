import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))
import config
from src.predict import DiseasePredictor

predictor = DiseasePredictor()

print("=" * 75)
print(f"{'CLASS NAME':<32} | {'SAMPLES TESTED':<15} | {'ACCURACY':<10}")
print("=" * 75)

total_correct = 0
total_tested = 0

for cls in config.DISEASE_CLASSES:
    folder = config.DATA_DIR / "sample_leaves" / cls
    imgs = list(folder.glob("*.jpg"))[:10]  # Test 10 real samples per class
    cls_correct = 0
    for img_p in imgs:
        res = predictor.predict(img_p)
        if res["predicted_class"] == cls:
            cls_correct += 1
            total_correct += 1
        total_tested += 1
    acc = (cls_correct / max(len(imgs), 1)) * 100.0
    print(f"{cls:<32} | {len(imgs):<15} | {acc:.1f}%")

print("=" * 75)
print(f"OVERALL ACCURACY: {total_correct}/{total_tested} ({(total_correct/total_tested)*100:.1f}%)")
print("=" * 75)
