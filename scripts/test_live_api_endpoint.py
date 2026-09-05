import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))
import config
from fastapi.testclient import TestClient
from api import app

client = TestClient(app)

print("=" * 80)
print(f"{'GROUND TRUTH':<30} | {'FASTAPI /api/predict OUTPUT':<30} | {'CONFIDENCE':<10}")
print("=" * 80)

for cls in config.DISEASE_CLASSES:
    folder = config.DATA_DIR / "sample_leaves" / cls
    imgs = list(folder.glob("*.jpg"))
    if imgs:
        with open(imgs[0], "rb") as f:
            res = client.post(
                "/api/predict",
                files={"file": (imgs[0].name, f, "image/jpeg")},
                data={"language": "English"}
            )
        data = res.json()
        pred = data.get("prediction", {})
        title = pred.get("display_title", "Unknown")
        conf = pred.get("confidence", 0.0)
        print(f"{cls:<30} | {title:<30} | {conf:.1f}%")
