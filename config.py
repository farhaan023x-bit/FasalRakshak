"""
FasalRakshak - Configuration File
Centralized settings for directory paths, model hyperparameters, disease classes, and advisory settings.
"""

import os
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "models"
SRC_DIR = BASE_DIR / "src"
ASSETS_DIR = BASE_DIR / "assets"

# Ensure essential directories exist
for folder in [DATA_DIR, MODELS_DIR, SRC_DIR, ASSETS_DIR]:
    folder.mkdir(parents=True, exist_ok=True)

# Image & Model Configurations
IMAGE_SIZE = (380, 380)
BATCH_SIZE = 32
EPOCHS = 10
NUM_CLASSES = 38
MODEL_SAVE_PATH = MODELS_DIR / "fasal_rakshak_model.pth"

# All 38 Supported PlantVillage Crop and Disease Classes
DISEASE_CLASSES = [
    "Apple___Apple_scab",
    "Apple___Black_rot",
    "Apple___Cedar_apple_rust",
    "Apple___healthy",
    "Blueberry___healthy",
    "Cherry___Powdery_mildew",
    "Cherry___healthy",
    "Corn___Cercospora_leaf_spot",
    "Corn___Common_rust",
    "Corn___Northern_Leaf_Blight",
    "Corn___healthy",
    "Grape___Black_rot",
    "Grape___Esca_(Black_Measles)",
    "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)",
    "Grape___healthy",
    "Orange___Haunglongbing_(Citrus_greening)",
    "Peach___Bacterial_spot",
    "Peach___healthy",
    "Pepper_bell___Bacterial_spot",
    "Pepper_bell___healthy",
    "Potato___Early_blight",
    "Potato___Late_blight",
    "Potato___healthy",
    "Raspberry___healthy",
    "Soybean___healthy",
    "Squash___Powdery_mildew",
    "Strawberry___Leaf_scorch",
    "Strawberry___healthy",
    "Tomato___Bacterial_spot",
    "Tomato___Early_blight",
    "Tomato___Late_blight",
    "Tomato___Leaf_Mold",
    "Tomato___Septoria_leaf_spot",
    "Tomato___Spider_mites Two-spotted_spider_mite",
    "Tomato___Target_Spot",
    "Tomato___Tomato_Yellow_Leaf_Curl_Virus",
    "Tomato___Tomato_mosaic_virus",
    "Tomato___healthy"
]

# Project Metadata
PROJECT_NAME = "FasalRakshak"
PROJECT_FULL_NAME = "FasalRakshak: Predictive Deep Learning & AI Farmer Advisory System"
VERSION = "1.0.0"
SDG_ALIGNMENT = ["SDG 2: Zero Hunger", "SDG 12: Responsible Consumption", "SDG 15: Life on Land"]

if __name__ == "__main__":
    print(f"[{PROJECT_NAME}] Configuration Initialized Successfully.")
    print(f"Base Directory: {BASE_DIR}")
    print(f"Model Save Path: {MODEL_SAVE_PATH}")
    print(f"Supported Classes ({len(DISEASE_CLASSES)}): {DISEASE_CLASSES[:4]}...")
