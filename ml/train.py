"""
THUNAI Crop Disease Classification Model Training
==================================================
Architecture: Pretrained MobileNetV3-Small with Transfer Learning
Optimization: AdamW + CosineAnnealingLR + Label Smoothing Cross-Entropy
Regularization: Data Augmentation, Dropout, Weight Decay, Early Stopping
Metrics: Train/Val Loss, Train/Val Accuracy, Macro-F1, Generalization Gap
"""

import os
import sys
import json
import time
import random
import copy
from typing import Dict, List, Tuple

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset
import torchvision.models as models
import torchvision.transforms as transforms
from PIL import Image
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# Set deterministic random seed
SEED = 42
random.seed(SEED)
np.random.seed(SEED)
torch.manual_seed(SEED)
if torch.cuda.is_available():
    torch.cuda.manual_seed_all(SEED)

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PROCESSED_DIR = os.path.join(BASE_DIR, "ml", "data", "processed")
CHECKPOINTS_DIR = os.path.join(BASE_DIR, "ml", "checkpoints")
ARTIFACTS_DIR = os.path.join(BASE_DIR, "ml", "artifacts")

os.makedirs(CHECKPOINTS_DIR, exist_ok=True)
os.makedirs(ARTIFACTS_DIR, exist_ok=True)

# Device configuration (CPU or CUDA)
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Dataset class
class ThunaiDataset(Dataset):
    def __init__(self, root_dir: str, transform=None):
        self.root_dir = root_dir
        self.transform = transform
        self.samples: List[Tuple[str, int, str]] = []
        self.classes = sorted(os.listdir(root_dir))
        self.class_to_idx = {cls_name: idx for idx, cls_name in enumerate(self.classes)}

        for cls_name in self.classes:
            cls_path = os.path.join(root_dir, cls_name)
            if not os.path.isdir(cls_path):
                continue
            for fname in os.listdir(cls_path):
                if fname.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                    self.samples.append((os.path.join(cls_path, fname), self.class_to_idx[cls_name], cls_name))

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        fpath, label, cls_name = self.samples[idx]
        image = Image.open(fpath).convert("RGB")
        if self.transform:
            image = self.transform(image)
        return image, label

def compute_metrics(y_true: np.ndarray, y_pred: np.ndarray, num_classes: int) -> Dict[str, float]:
    """
    Computes accuracy, macro precision, macro recall, and macro F1 purely using NumPy.
    Avoids external C-extension/DLL dependencies.
    """
    acc = float(np.mean(y_true == y_pred))
    precisions = []
    recalls = []
    f1s = []

    for c in range(num_classes):
        tp = np.sum((y_pred == c) & (y_true == c))
        fp = np.sum((y_pred == c) & (y_true != c))
        fn = np.sum((y_pred != c) & (y_true == c))

        prec = float(tp / (tp + fp)) if (tp + fp) > 0 else 0.0
        rec = float(tp / (tp + fn)) if (tp + fn) > 0 else 0.0
        f1 = float(2 * prec * rec / (prec + rec)) if (prec + rec) > 0 else 0.0

        precisions.append(prec)
        recalls.append(rec)
        f1s.append(f1)

    macro_precision = float(np.mean(precisions))
    macro_recall = float(np.mean(recalls))
    macro_f1 = float(np.mean(f1s))

    return {
        "accuracy": acc,
        "macro_precision": macro_precision,
        "macro_recall": macro_recall,
        "macro_f1": macro_f1,
        "per_class_f1": f1s,
        "per_class_recall": recalls,
        "per_class_precision": precisions
    }

def get_data_loaders(batch_size: int = 32):
    train_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.RandomHorizontalFlip(p=0.5),
        transforms.RandomVerticalFlip(p=0.2),
        transforms.RandomRotation(degrees=15),
        transforms.ColorJitter(brightness=0.15, contrast=0.15, saturation=0.15),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])

    eval_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])

    train_dataset = ThunaiDataset(os.path.join(PROCESSED_DIR, "train"), transform=train_transform)
    val_dataset = ThunaiDataset(os.path.join(PROCESSED_DIR, "val"), transform=eval_transform)
    test_dataset = ThunaiDataset(os.path.join(PROCESSED_DIR, "test"), transform=eval_transform)

    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, num_workers=0)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False, num_workers=0)
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False, num_workers=0)

    return train_loader, val_loader, test_loader, train_dataset.classes

def build_model(num_classes: int) -> nn.Module:
    """
    Constructs MobileNetV3-Small with pretrained ImageNet weights.
    Replaces classifier head with custom dropout and linear classification head.
    """
    model = models.mobilenet_v3_small(weights=models.MobileNet_V3_Small_Weights.DEFAULT)
    
    # Fine-tuning: Freeze early feature layers, keep last conv block and classifier head trainable
    for param in model.features[:-3].parameters():
        param.requires_grad = False
    for param in model.features[-3:].parameters():
        param.requires_grad = True

    in_features = model.classifier[0].in_features
    model.classifier = nn.Sequential(
        nn.Linear(in_features, 512),
        nn.Hardswish(),
        nn.Dropout(p=0.3),
        nn.Linear(512, num_classes)
    )
    return model

def train_model(epochs: int = 12, batch_size: int = 32, lr: float = 1e-3):
    print(f"Starting THUNAI Model Training on device: {DEVICE}")
    train_loader, val_loader, test_loader, classes = get_data_loaders(batch_size=batch_size)
    num_classes = len(classes)
    print(f"Loaded {len(train_loader.dataset)} training, {len(val_loader.dataset)} validation, {len(test_loader.dataset)} test samples across {num_classes} classes.")

    model = build_model(num_classes).to(DEVICE)

    # Label smoothing cross entropy prevents overconfidence and sharpens calibration
    criterion = nn.CrossEntropyLoss(label_smoothing=0.05)
    optimizer = optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-4)
    scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs, eta_min=1e-5)

    history = {
        "train_loss": [], "val_loss": [],
        "train_acc": [], "val_acc": [],
        "val_macro_f1": [],
        "epochs": []
    }

    best_val_f1 = 0.0
    best_model_weights = None
    best_epoch = 0
    patience = 4
    no_improve_count = 0

    start_time = time.time()

    for epoch in range(1, epochs + 1):
        epoch_start = time.time()
        # Training Phase
        model.train()
        running_loss = 0.0
        train_preds, train_targets = [], []

        for images, targets in train_loader:
            images, targets = images.to(DEVICE), targets.to(DEVICE)
            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, targets)
            loss.backward()
            optimizer.step()

            running_loss += loss.item() * images.size(0)
            preds = torch.argmax(outputs, dim=1)
            train_preds.extend(preds.cpu().numpy())
            train_targets.extend(targets.cpu().numpy())

        scheduler.step()
        epoch_train_loss = running_loss / len(train_loader.dataset)
        train_metrics = compute_metrics(np.array(train_targets), np.array(train_preds), num_classes)
        epoch_train_acc = train_metrics["accuracy"]

        # Validation Phase
        model.eval()
        val_running_loss = 0.0
        val_preds, val_targets = [], []

        with torch.no_grad():
            for images, targets in val_loader:
                images, targets = images.to(DEVICE), targets.to(DEVICE)
                outputs = model(images)
                loss = criterion(outputs, targets)
                val_running_loss += loss.item() * images.size(0)
                preds = torch.argmax(outputs, dim=1)
                val_preds.extend(preds.cpu().numpy())
                val_targets.extend(targets.cpu().numpy())

        epoch_val_loss = val_running_loss / len(val_loader.dataset)
        val_metrics = compute_metrics(np.array(val_targets), np.array(val_preds), num_classes)
        epoch_val_acc = val_metrics["accuracy"]
        epoch_val_f1 = val_metrics["macro_f1"]

        gen_gap = (epoch_train_acc - epoch_val_acc) * 100
        epoch_time = time.time() - epoch_start

        history["train_loss"].append(epoch_train_loss)
        history["val_loss"].append(epoch_val_loss)
        history["train_acc"].append(epoch_train_acc)
        history["val_acc"].append(epoch_val_acc)
        history["val_macro_f1"].append(epoch_val_f1)
        history["epochs"].append(epoch)

        print(f"Epoch [{epoch:02d}/{epochs:02d}] ({epoch_time:.1f}s) - "
              f"Train Loss: {epoch_train_loss:.4f}, Acc: {epoch_train_acc*100:.2f}% | "
              f"Val Loss: {epoch_val_loss:.4f}, Acc: {epoch_val_acc*100:.2f}%, Macro-F1: {epoch_val_f1:.4f} | "
              f"Gap: {gen_gap:+.2f}%")

        # Save best checkpoint
        if epoch_val_f1 > best_val_f1:
            best_val_f1 = epoch_val_f1
            best_epoch = epoch
            best_model_weights = copy.deepcopy(model.state_dict())
            no_improve_count = 0
            
            # Save checkpoint to disk
            checkpoint_path = os.path.join(CHECKPOINTS_DIR, "best_model.pth")
            torch.save({
                "epoch": epoch,
                "model_state_dict": best_model_weights,
                "val_accuracy": epoch_val_acc,
                "val_macro_f1": epoch_val_f1,
                "classes": classes,
                "architecture": "mobilenet_v3_small",
            }, checkpoint_path)
            print(f"  --> Checkpoint saved at epoch {epoch} (Val Macro-F1: {epoch_val_f1:.4f})")
        else:
            no_improve_count += 1
            if no_improve_count >= patience:
                print(f"Early stopping triggered at epoch {epoch} (no improvement for {patience} epochs).")
                break

    total_time = time.time() - start_time
    print(f"\nTraining completed in {total_time/60:.2f} minutes. Best epoch: {best_epoch} with Val Macro-F1: {best_val_f1:.4f}")

    # Plot training and validation curves
    plot_training_curves(history)

    # Save training history JSON
    history_path = os.path.join(ARTIFACTS_DIR, "training_history.json")
    with open(history_path, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2)

    return classes

def plot_training_curves(history: Dict):
    epochs = history["epochs"]
    plt.figure(figsize=(12, 5))

    # Loss curve
    plt.subplot(1, 2, 1)
    plt.plot(epochs, history["train_loss"], label='Train Loss', color='#1B5E20', linewidth=2)
    plt.plot(epochs, history["val_loss"], label='Val Loss', color='#F57C00', linewidth=2, linestyle='--')
    plt.title('Loss Trajectory (Cross-Entropy with Label Smoothing)', fontsize=12, fontweight='bold')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.legend()
    plt.grid(True, linestyle=':', alpha=0.6)

    # Accuracy & Macro-F1 curve
    plt.subplot(1, 2, 2)
    plt.plot(epochs, [a * 100 for a in history["train_acc"]], label='Train Acc %', color='#1B5E20', linewidth=2)
    plt.plot(epochs, [a * 100 for a in history["val_acc"]], label='Val Acc %', color='#2E7D32', linewidth=2, linestyle='--')
    plt.plot(epochs, [f * 100 for f in history["val_macro_f1"]], label='Val Macro-F1 %', color='#388E3C', linewidth=2, linestyle=':')
    plt.title('Accuracy & Macro-F1 Trajectory', fontsize=12, fontweight='bold')
    plt.xlabel('Epoch')
    plt.ylabel('Percentage (%)')
    plt.legend()
    plt.grid(True, linestyle=':', alpha=0.6)

    plt.tight_layout()
    curves_path = os.path.join(ARTIFACTS_DIR, "training_curves.png")
    plt.savefig(curves_path, dpi=200)
    plt.close()
    print(f"Saved training curves to {curves_path}")

if __name__ == "__main__":
    train_model(epochs=10, batch_size=32, lr=1e-3)
