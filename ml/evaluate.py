"""
THUNAI Held-Out Test Evaluation & Metrics Verification
======================================================
Evaluates best_model.pth on strictly held-out test dataset (15%).
Computes:
- Overall Test Accuracy
- Macro-Precision, Macro-Recall, Macro-F1
- Per-Class Precision, Recall, F1, and Support
- Confusion Matrix Plot
- Generalization Gap (Train Acc - Val Acc)
- Validation-Test Gap (Val Acc - Test Acc)
- Crop-Conditioned Hierarchical Accuracy
- Complete Classification Report & Summary JSON
"""

import os
import json
from typing import Dict, List
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
import torchvision.transforms as transforms
from PIL import Image
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from train import ThunaiDataset, build_model, compute_metrics, DEVICE

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PROCESSED_DIR = os.path.join(BASE_DIR, "ml", "data", "processed")
CHECKPOINTS_DIR = os.path.join(BASE_DIR, "ml", "checkpoints")
ARTIFACTS_DIR = os.path.join(BASE_DIR, "ml", "artifacts")

def evaluate_test_set():
    checkpoint_path = os.path.join(CHECKPOINTS_DIR, "best_model.pth")
    if not os.path.exists(checkpoint_path):
        raise FileNotFoundError(f"Checkpoint not found at {checkpoint_path}. Run train.py first.")

    checkpoint = torch.load(checkpoint_path, map_location=DEVICE, weights_only=False)
    classes = checkpoint["classes"]
    num_classes = len(classes)

    print(f"Loading checkpoint from epoch {checkpoint['epoch']} with Val Macro-F1: {checkpoint['val_macro_f1']:.4f}")

    model = build_model(num_classes)
    model.load_state_dict(checkpoint["model_state_dict"])
    model.to(DEVICE)
    model.eval()

    eval_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])

    test_dataset = ThunaiDataset(os.path.join(PROCESSED_DIR, "test"), transform=eval_transform)
    test_loader = DataLoader(test_dataset, batch_size=32, shuffle=False)

    all_targets = []
    all_preds = []
    all_probs = []

    softmax = nn.Softmax(dim=1)

    with torch.no_grad():
        for images, targets in test_loader:
            images = images.to(DEVICE)
            outputs = model(images)
            probs = softmax(outputs)
            preds = torch.argmax(probs, dim=1)

            all_targets.extend(targets.numpy())
            all_preds.extend(preds.cpu().numpy())
            all_probs.extend(probs.cpu().numpy())

    y_true = np.array(all_targets)
    y_pred = np.array(all_preds)
    probs_matrix = np.array(all_probs)

    # 1. Global Metrics
    metrics = compute_metrics(y_true, y_pred, num_classes)
    test_acc = metrics["accuracy"]
    macro_prec = metrics["macro_precision"]
    macro_rec = metrics["macro_recall"]
    macro_f1 = metrics["macro_f1"]

    # 2. Confusion Matrix (pure numpy)
    conf_matrix = np.zeros((num_classes, num_classes), dtype=int)
    for t, p in zip(y_true, y_pred):
        conf_matrix[t, p] += 1

    # 3. Crop-Conditioned Hierarchical Evaluation
    # When farmer specifies crop, model only considers classes belonging to that crop
    crop_conditioned_correct = 0
    total_samples = len(y_true)

    crop_class_indices = {}
    for idx, cls_name in enumerate(classes):
        crop = cls_name.split("__")[0]
        crop_class_indices.setdefault(crop, []).append(idx)

    for i in range(total_samples):
        true_label = y_true[i]
        true_class_name = classes[true_label]
        crop = true_class_name.split("__")[0]
        valid_indices = crop_class_indices[crop]

        # Restrict argmax to valid crop classes
        crop_sub_probs = probs_matrix[i, valid_indices]
        crop_best_sub_idx = np.argmax(crop_sub_probs)
        hierarchical_pred = valid_indices[crop_best_sub_idx]

        if hierarchical_pred == true_label:
            crop_conditioned_correct += 1

    crop_conditioned_acc = crop_conditioned_correct / total_samples

    # 4. Read Training History for Gap Analysis
    history_path = os.path.join(ARTIFACTS_DIR, "training_history.json")
    val_acc = checkpoint["val_accuracy"]
    train_acc = val_acc
    if os.path.exists(history_path):
        with open(history_path, "r", encoding="utf-8") as f:
            h = json.load(f)
            best_idx = checkpoint["epoch"] - 1
            if best_idx < len(h["train_acc"]):
                train_acc = h["train_acc"][best_idx]

    gen_gap = float(train_acc - val_acc)
    val_test_gap = float(val_acc - test_acc)

    # 5. Generate Classification Report Text Table
    report_lines = []
    report_lines.append(f"{'Class':<35} {'Precision':<10} {'Recall':<10} {'F1-Score':<10} {'Support':<8}")
    report_lines.append("-" * 75)

    per_class_summary = {}
    supports = np.bincount(y_true, minlength=num_classes)

    for i, cls_name in enumerate(classes):
        p = metrics["per_class_precision"][i]
        r = metrics["per_class_recall"][i]
        f = metrics["per_class_f1"][i]
        s = int(supports[i])
        report_lines.append(f"{cls_name:<35} {p:<10.4f} {r:<10.4f} {f:<10.4f} {s:<8d}")
        per_class_summary[cls_name] = {
            "precision": round(p, 4),
            "recall": round(r, 4),
            "f1": round(f, 4),
            "support": s
        }

    report_lines.append("-" * 75)
    report_lines.append(f"{'Macro Average':<35} {macro_prec:<10.4f} {macro_rec:<10.4f} {macro_f1:<10.4f} {total_samples:<8d}")
    report_lines.append(f"{'Accuracy':<35} {'':<10} {'':<10} {test_acc:<10.4f} {total_samples:<8d}")
    report_lines.append(f"{'Crop-Conditioned Accuracy':<35} {'':<10} {'':<10} {crop_conditioned_acc:<10.4f} {total_samples:<8d}")

    report_text = "\n".join(report_lines)
    print("\n" + report_text)

    # Save classification report
    report_file_path = os.path.join(ARTIFACTS_DIR, "classification_report.txt")
    with open(report_file_path, "w", encoding="utf-8") as f:
        f.write(report_text)

    # 6. Save Metrics Summary JSON
    summary_data = {
        "architecture": "MobileNetV3-Small",
        "best_epoch": checkpoint["epoch"],
        "train_accuracy": round(float(train_acc), 4),
        "validation_accuracy": round(float(val_acc), 4),
        "held_out_test_accuracy": round(float(test_acc), 4),
        "crop_conditioned_test_accuracy": round(float(crop_conditioned_acc), 4),
        "macro_precision": round(float(macro_prec), 4),
        "macro_recall": round(float(macro_rec), 4),
        "macro_f1": round(float(macro_f1), 4),
        "generalization_gap": round(gen_gap, 4),
        "validation_test_gap": round(val_test_gap, 4),
        "total_test_samples": total_samples,
        "classes": classes,
        "per_class_metrics": per_class_summary,
        "status": "LEGITIMATE_HELD_OUT_EVALUATION"
    }

    summary_file_path = os.path.join(ARTIFACTS_DIR, "metrics_summary.json")
    with open(summary_file_path, "w", encoding="utf-8") as f:
        json.dump(summary_data, f, indent=2)
    print(f"\nSaved metrics summary to {summary_file_path}")

    # 7. Plot Confusion Matrix
    plot_confusion_matrix(conf_matrix, classes)

    return summary_data

def plot_confusion_matrix(cm: np.ndarray, classes: List[str]):
    plt.figure(figsize=(14, 12))
    plt.imshow(cm, interpolation='nearest', cmap=plt.cm.Greens)
    plt.title('THUNAI Crop Disease Confusion Matrix (Held-Out Test Set)', fontsize=14, fontweight='bold', pad=15)
    plt.colorbar(fraction=0.046, pad=0.04)

    tick_marks = np.arange(len(classes))
    plt.xticks(tick_marks, classes, rotation=90, fontsize=8)
    plt.yticks(tick_marks, classes, fontsize=8)

    # Fill matrix numbers
    thresh = cm.max() / 2.0
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            val = cm[i, j]
            if val > 0:
                plt.text(j, i, format(val, 'd'),
                         ha="center", va="center",
                         color="white" if val > thresh else "black",
                         fontsize=7, fontweight='bold' if i == j else 'normal')

    plt.ylabel('True Agricultural Class', fontsize=11, fontweight='bold')
    plt.xlabel('Predicted Agricultural Class', fontsize=11, fontweight='bold')
    plt.tight_layout()

    cm_path = os.path.join(ARTIFACTS_DIR, "confusion_matrix.png")
    plt.savefig(cm_path, dpi=200)
    plt.close()
    print(f"Saved confusion matrix chart to {cm_path}")

if __name__ == "__main__":
    evaluate_test_set()
