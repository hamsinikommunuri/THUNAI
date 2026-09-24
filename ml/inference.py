"""
THUNAI Production ML Inference Engine with Grad-CAM Explainability
==================================================================
Features:
- Single-load in-memory model lifecycle
- Crop-conditioned hierarchical probability calibration
- Grad-CAM heatmap visualization (explaining morphological lesion focus)
- Uncertainty tiering (High >= 0.80, Moderate 0.60-0.80, Low < 0.60)
- Top-3 candidate ranking
"""

import os
import io
import json
import base64
from typing import Dict, Any, List, Optional, Tuple

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import torchvision.transforms as transforms
from PIL import Image
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from ml.train import build_model, DEVICE

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CHECKPOINT_PATH = os.path.join(BASE_DIR, "ml", "checkpoints", "best_model.pth")
KNOWLEDGE_DIR = os.path.join(BASE_DIR, "backend", "app", "knowledge")

# Class index mapping from model
_MODEL_INSTANCE = None
_CLASSES: List[str] = []
_DISEASES_DB: Dict[str, Any] = {}

def get_inference_engine():
    global _MODEL_INSTANCE, _CLASSES, _DISEASES_DB

    if _MODEL_INSTANCE is None:
        if not os.path.exists(CHECKPOINT_PATH):
            raise FileNotFoundError(f"Model checkpoint not found at {CHECKPOINT_PATH}")

        checkpoint = torch.load(CHECKPOINT_PATH, map_location=DEVICE, weights_only=False)
        _CLASSES = checkpoint["classes"]
        model = build_model(len(_CLASSES))
        model.load_state_dict(checkpoint["model_state_dict"])
        model.to(DEVICE)
        model.eval()
        _MODEL_INSTANCE = model
        print(f"THUNAI Inference Engine initialized with {len(_CLASSES)} classes on {DEVICE}.")

        # Load disease database for metadata
        dis_path = os.path.join(KNOWLEDGE_DIR, "diseases.json")
        if os.path.exists(dis_path):
            with open(dis_path, "r", encoding="utf-8") as f:
                _DISEASES_DB = json.load(f)

    return _MODEL_INSTANCE, _CLASSES, _DISEASES_DB

class GradCAM:
    def __init__(self, model, target_layer):
        self.model = model
        self.target_layer = target_layer
        self.gradients = None
        self.activations = None
        self.hook_handles = []
        self._register_hooks()

    def _register_hooks(self):
        def forward_hook(module, input, output):
            self.activations = output

        def backward_hook(module, grad_input, grad_output):
            self.gradients = grad_output[0]

        self.hook_handles.append(self.target_layer.register_forward_hook(forward_hook))
        self.hook_handles.append(self.target_layer.register_full_backward_hook(backward_hook))

    def generate_heatmap(self, input_tensor: torch.Tensor, class_idx: int) -> np.ndarray:
        self.model.zero_grad()
        output = self.model(input_tensor)
        score = output[0, class_idx]
        score.backward()

        # Global average pooling of gradients
        pooled_gradients = torch.mean(self.gradients, dim=[0, 2, 3])
        activations = self.activations[0]

        # Weight channels by gradient significance
        for i in range(activations.size(0)):
            activations[i, :, :] *= pooled_gradients[i]

        heatmap = torch.mean(activations, dim=0).squeeze().cpu().detach().numpy()
        heatmap = np.maximum(heatmap, 0)
        max_val = np.max(heatmap)
        if max_val > 0:
            heatmap /= max_val
        return heatmap

    def remove_hooks(self):
        for h in self.hook_handles:
            h.remove()

def preprocess_image(pil_image: Image.Image) -> torch.Tensor:
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    return transform(pil_image).unsqueeze(0).to(DEVICE)

def overlay_gradcam(pil_image: Image.Image, heatmap: np.ndarray) -> str:
    """
    Overlays Grad-CAM attention heatmap onto the original image
    and returns a base64-encoded PNG data URI.
    """
    # Resize heatmap from 7x7 feature space to full 224x224 image dimensions
    heatmap_pil = Image.fromarray((heatmap * 255).astype(np.uint8)).resize((224, 224), resample=Image.BILINEAR)
    heatmap_resized = np.array(heatmap_pil) / 255.0

    img_resized = pil_image.resize((224, 224))
    img_arr = np.array(img_resized) / 255.0

    # Apply colormap (jet)
    cmap = plt.cm.jet
    heatmap_colored = cmap(heatmap_resized)[:, :, :3]  # drop alpha

    # Alpha blend
    blended = 0.55 * img_arr + 0.45 * heatmap_colored
    blended = np.clip(blended, 0.0, 1.0)
    blended_uint8 = (blended * 255).astype(np.uint8)

    buf = io.BytesIO()
    Image.fromarray(blended_uint8).save(buf, format="PNG")
    b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
    return f"data:image/png;base64,{b64}"

def run_diagnosis(
    image: Image.Image, 
    crop_selected: Optional[str] = "tomato"
) -> Dict[str, Any]:
    """
    Executes actual deep learning inference on the image.
    Supports crop conditioning and Grad-CAM explainability.
    """
    model, classes, diseases_db = get_inference_engine()
    input_tensor = preprocess_image(image)

    # 1. Forward pass
    with torch.no_grad():
        logits = model(input_tensor)[0]
        all_probs = F.softmax(logits, dim=0).cpu().numpy()

    # 2. Crop-Conditioned Filtering
    crop_key = (crop_selected or "tomato").lower()
    crop_indices = [i for i, cls_name in enumerate(classes) if cls_name.startswith(f"{crop_key}__")]

    if crop_indices:
        # Re-normalize probabilities over the selected crop classes
        sub_probs = all_probs[crop_indices]
        sum_sub = np.sum(sub_probs)
        if sum_sub > 0:
            calibrated_sub_probs = sub_probs / sum_sub
        else:
            calibrated_sub_probs = sub_probs

        sorted_order = np.argsort(calibrated_sub_probs)[::-1]
        best_sub_idx = sorted_order[0]
        primary_global_idx = crop_indices[best_sub_idx]
        primary_confidence = float(calibrated_sub_probs[best_sub_idx])

        # Top candidates
        top_candidates = []
        for rank_idx in sorted_order[:3]:
            g_idx = crop_indices[rank_idx]
            cls_key = classes[g_idx]
            dis_info = diseases_db.get(cls_key, {})
            score = float(calibrated_sub_probs[rank_idx])
            top_candidates.append({
                "crop": crop_key,
                "disease_id": cls_key.split("__")[1],
                "common_name": dis_info.get("common_name", cls_key.replace("__", " ").title()),
                "scientific_name": dis_info.get("scientific_name", "Identified Agricultural Variant"),
                "confidence": round(score, 4),
                "confidence_percent": round(score * 100, 1)
            })
    else:
        # Fallback to global argmax across all classes
        primary_global_idx = int(np.argmax(all_probs))
        primary_confidence = float(all_probs[primary_global_idx])
        top_indices = np.argsort(all_probs)[::-1][:3]
        top_candidates = []
        for g_idx in top_indices:
            cls_key = classes[g_idx]
            dis_info = diseases_db.get(cls_key, {})
            score = float(all_probs[g_idx])
            top_candidates.append({
                "crop": cls_key.split("__")[0],
                "disease_id": cls_key.split("__")[1],
                "common_name": dis_info.get("common_name", cls_key),
                "scientific_name": dis_info.get("scientific_name", "Foliar Pathogen"),
                "confidence": round(score, 4),
                "confidence_percent": round(score * 100, 1)
            })

    predicted_class_key = classes[primary_global_idx]
    predicted_disease_id = predicted_class_key.split("__")[1]
    disease_meta = diseases_db.get(predicted_class_key, {})

    # 3. Grad-CAM Generation
    gradcam_b64 = None
    try:
        # Target layer is last convolutional block
        target_layer = model.features[-1]
        gradcam = GradCAM(model, target_layer)
        # Re-enable grad for CAM
        input_tensor_grad = input_tensor.clone().detach().requires_grad_(True)
        heatmap = gradcam.generate_heatmap(input_tensor_grad, primary_global_idx)
        gradcam_b64 = overlay_gradcam(image, heatmap)
        gradcam.remove_hooks()
    except Exception as cam_err:
        print(f"Grad-CAM generation notice: {cam_err}")

    # 4. Uncertainty Handling & Confidence Tiering
    if primary_confidence >= 0.80:
        confidence_tier = "High"
        requires_escalation = False
        escalation_reason = None
    elif primary_confidence >= 0.60:
        confidence_tier = "Moderate"
        requires_escalation = False
        escalation_reason = None
    else:
        confidence_tier = "Low"
        requires_escalation = True
        escalation_reason = "Model confidence is below 60%. Visual ambiguity exists between candidate foliar pathologies."

    return {
        "class_key": predicted_class_key,
        "crop": crop_key,
        "disease_id": predicted_disease_id,
        "common_name": disease_meta.get("common_name", predicted_class_key),
        "scientific_name": disease_meta.get("scientific_name", "Pathogen Unspecified"),
        "pathogen_type": disease_meta.get("pathogen_type", "Fungal / Bacterial"),
        "confidence": round(primary_confidence, 4),
        "confidence_tier": confidence_tier,
        "top_predictions": top_candidates,
        "gradcam_base64": gradcam_b64,
        "requires_escalation": requires_escalation,
        "escalation_reason": escalation_reason,
        "disease_metadata": disease_meta
    }
