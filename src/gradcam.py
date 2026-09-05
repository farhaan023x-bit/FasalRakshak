"""
FasalRakshak - Grad-CAM (Gradient-Weighted Class Activation Mapping)
Generates visual saliency heatmaps for MobileNetV3 leaf pathology explainability.
Highlights regions of interest (lesions, margins, pustules) that drove the AI prediction.
"""

import numpy as np
import torch
import torch.nn.functional as F
from PIL import Image
import matplotlib.cm as cm
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parent.parent))
import config
from src.dataset import VAL_TRANSFORMS


class GradCAM:
    """
    Grad-CAM Explainer for Convolutional Neural Networks.
    Hooks into target convolutional layer activations and gradients.
    """

    def __init__(self, model, target_layer=None):
        self.model = model
        self.model.eval()
        self.target_layer = target_layer or self.model.backbone.features[-1]
        
        self.gradients = None
        self.activations = None
        
        # Register hooks
        self._register_hooks()

    def _register_hooks(self):
        def forward_hook(module, input, output):
            self.activations = output

        def backward_hook(module, grad_in, grad_out):
            self.gradients = grad_out[0]

        self.target_layer.register_forward_hook(forward_hook)
        self.target_layer.register_full_backward_hook(backward_hook)

    def generate_heatmap(self, input_tensor, target_class_idx=None):
        """
        Generates 2D Grad-CAM heatmap array normalized in range [0, 1].
        """
        self.model.zero_grad()
        output = self.model(input_tensor)

        if target_class_idx is None:
            target_class_idx = torch.argmax(output, dim=1).item()

        # Backward pass on target score
        target_score = output[0, target_class_idx]
        target_score.backward(retain_graph=True)

        # Global Average Pooling of gradients
        pooled_gradients = torch.mean(self.gradients, dim=[0, 2, 3])

        # Weight the channels by corresponding gradients
        activations = self.activations[0]
        for i in range(activations.size(0)):
            activations[i, :, :] *= pooled_gradients[i]

        # Heatmap is the channel-wise mean of weighted activations
        heatmap = torch.mean(activations, dim=0).squeeze().cpu().detach().numpy()
        
        # Apply ReLU to retain only positive influences
        heatmap = np.maximum(heatmap, 0)

        # Normalize between 0 and 1
        if np.max(heatmap) > 0:
            heatmap /= np.max(heatmap)

        return heatmap

    def overlay_heatmap(self, original_image: Image.Image, heatmap: np.ndarray, alpha: float = 0.45) -> Image.Image:
        """
        Overlays colorized Grad-CAM heatmap onto the original PIL leaf photograph.
        """
        orig_w, orig_h = original_image.size
        
        # Resize heatmap to match original image dimensions
        heatmap_img = Image.fromarray(np.uint8(255 * heatmap)).resize((orig_w, orig_h), resample=Image.Resampling.BICUBIC)
        heatmap_resized = np.array(heatmap_img) / 255.0

        # Apply Jet colormap (Red = high influence, Blue = low influence)
        try:
            import matplotlib.pyplot as plt
            colormap = plt.get_cmap("jet")
        except Exception:
            import matplotlib
            colormap = matplotlib.colormaps["jet"]
        colored_heatmap = colormap(heatmap_resized)[:, :, :3]  # RGB
        colored_heatmap_uint8 = np.uint8(255 * colored_heatmap)

        # Superimpose onto original RGB image
        orig_array = np.array(original_image.convert("RGB"))
        superimposed = np.uint8((1 - alpha) * orig_array + alpha * colored_heatmap_uint8)

        return Image.fromarray(superimposed)


def compute_gradcam_overlay(model, pil_image: Image.Image, target_class_idx: int = None) -> Image.Image:
    """
    Convenience function: computes and returns Grad-CAM overlay PIL image for a given leaf.
    """
    device = next(model.parameters()).device
    tensor_img = VAL_TRANSFORMS(pil_image.convert("RGB")).unsqueeze(0).to(device)

    explainer = GradCAM(model)
    heatmap = explainer.generate_heatmap(tensor_img, target_class_idx=target_class_idx)
    overlay = explainer.overlay_heatmap(pil_image, heatmap, alpha=0.45)
    return overlay


if __name__ == "__main__":
    print("[Grad-CAM Module] Testing visual saliency computation on MobileNetV3...")
    from src.model import build_model
    model = build_model(pretrained=False)
    
    # Test on synthetic leaf
    test_leaf = Image.new("RGB", (300, 300), color=(40, 140, 40))
    overlay_img = compute_gradcam_overlay(model, test_leaf, target_class_idx=0)
    
    test_save = config.ASSETS_DIR / "test_gradcam_overlay.png"
    overlay_img.save(test_save)
    print(f"Grad-CAM visual overlay generated and saved to: {test_save}")
