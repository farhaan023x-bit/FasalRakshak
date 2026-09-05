"""
FasalRakshak - Model Architecture
Uses EfficientNet‑B4 backbone for high‑accuracy crop disease classification.
Designed for GPU training but can run on CPU.
"""

import torch
import torch.nn as nn
from torchvision import models
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parent.parent))
import config


class FasalRakshakNet(nn.Module):
    """EfficientNet‑B4 based classifier.
    The backbone is loaded with pretrained ImageNet weights.
    The final classification head is replaced to match the number of disease classes.
    """
    def __init__(self, num_classes=config.NUM_CLASSES, pretrained=True):
        super(FasalRakshakNet, self).__init__()
        
        # Load EfficientNet‑B4 backbone
        if pretrained:
            weights = models.EfficientNet_B4_Weights.DEFAULT
            self.backbone = models.efficientnet_b4(weights=weights)
        else:
            self.backbone = models.efficientnet_b4(weights=None)
        
        # Replace the classifier head (original has a Linear layer called classifier)
        in_features = self.backbone.classifier[1].in_features
        self.backbone.classifier = nn.Sequential(
            nn.Dropout(p=0.3),
            nn.Linear(in_features, num_classes)
        )

    def forward(self, x):
        return self.backbone(x)


def build_model(pretrained=True):
    """Factory to instantiate the model."""
    model = FasalRakshakNet(num_classes=len(config.DISEASE_CLASSES), pretrained=pretrained)
    return model


if __name__ == "__main__":
    print("[Model Module] Initializing EfficientNet‑B4 architecture...")
    try:
        model = build_model(pretrained=True)
        print("Pretrained EfficientNet‑B4 loaded successfully.")
    except Exception as e:
        print(f"Failed to load pretrained weights: {e}. Falling back to random init.")
        model = build_model(pretrained=False)

    dummy_input = torch.randn(1, 3, config.IMAGE_SIZE[0], config.IMAGE_SIZE[1])
    output = model(dummy_input)

    print(f"Model output shape: {output.shape}")
    print(f"Number of classes: {len(config.DISEASE_CLASSES)}")
    print("Model built successfully.")
