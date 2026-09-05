import sys
import random
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))
import config
from src.predict import DiseasePredictor
from src.inference import predict_image

predictor = DiseasePredictor(model_path=config.MODEL_SAVE_PATH)

classes_to_sample = [
    'Tomato___Early_blight',
    'Tomato___Late_blight',
    'Tomato___healthy',
    'Potato___Late_blight',
    'Potato___Early_blight',
    'Corn___Common_rust',
    'Corn___healthy',
    'Apple___Cedar_apple_rust',
    'Apple___Black_rot'
]

print("=" * 80)
print(f"{'GROUND TRUTH':<30} | {'PREDICT_IMAGE (NN)':<30} | {'PREDICTOR':<20}")
print("=" * 80)
for cls in classes_to_sample:
    cls_dir = config.DATA_DIR / "sample_leaves" / cls
    images = list(cls_dir.glob("*.jpg"))
    if images:
        chosen = images[0]
        res_inf = predict_image(chosen, use_tta=True)
        res_pred = predictor.predict(chosen)
        print(f"{cls:<30} | {res_inf['class']} ({res_inf['confidence']*100:.1f}%) | {res_pred['predicted_class']} ({res_pred['confidence']:.1f}%)")
