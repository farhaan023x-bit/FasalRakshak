import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))
import config
from src.predict import DiseasePredictor

predictor = DiseasePredictor()

test_classes = [
    'Apple___Apple_scab',
    'Apple___Black_rot',
    'Apple___Cedar_apple_rust',
    'Apple___healthy',
    'Potato___Early_blight',
    'Potato___Late_blight',
    'Tomato___Early_blight',
    'Tomato___healthy',
    'Corn___Common_rust',
    'Corn___Cercospora_leaf_spot'
]

print("TESTING PREDICTIONS FROM SAMPLE LEAVES:")
for cls in test_classes:
    folder = config.DATA_DIR / "sample_leaves" / cls
    img_files = list(folder.glob("*.jpg"))
    if img_files:
        res = predictor.predict(img_files[0])
        print(f"{cls:<30} -> Predicted: {res['display_title']:<30} (Conf: {res['confidence']}%)")
