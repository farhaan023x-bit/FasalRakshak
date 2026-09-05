"""
High-Precision Training with 200 samples/class and 60 epochs
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))
import config

from src.train import train_model

if __name__ == "__main__":
    print("Starting high-precision training...")
    train_model(epochs=60, lr=0.0015, batch_size=32)
