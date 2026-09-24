# MODEL CARD: THUNAI MobileNetV3 Crop Pathology Classifier

## Model Overview
- **Model Name**: THUNAI Deep Agricultural Vision Classifier (`best_model.pth`)
- **Version**: 2.0.0
- **Model Date**: September 2026
- **Architecture**: MobileNetV3-Small with Transfer Learning (ImageNet weights)
- **Model Size**: 4.82 MB (Checkpoint: 5,058,565 bytes)
- **Primary Task**: Multi-class foliar pathology and health state classification across 5 commercial crops.
- **Inference Runtime**: ~18 ms per image on standard CPU (PyTorch).
- **Explainability**: Integrated Grad-CAM (Gradient-Weighted Class Activation Mapping) on feature stage `features[-1]`.

---

## Intended Use
- **Primary Use Case**: Point-of-care disease screening for smallholder farmers and extension officers.
- **Conditional Hierarchy**: Evaluates probabilities conditioned on farmer's selected crop (`tomato`, `potato`, `chilli`, `rice`, `banana`), eliminating cross-crop confusion.
- **Uncertainty Calibration**: Explicitly separates predictions into:
  - **High Confidence (>= 80%)**: Full automated treatment pathway unlocked.
  - **Moderate Confidence (60% - 80%)**: Cultural and biological controls prioritized.
  - **Low Confidence (< 60%)**: Triggers statutory lock and automated referral to Krishi Vigyan Kendra (KVK) Expert Second Opinion.

---

## Training Data & Methodology

### Data Preprocessing & Leakage Prevention
- **Deduplication**: MD5 hash-level screening across all raw source images before splitting. Zero exact duplicates exist within or across splits.
- **Split Ratio**: Stratified 70% Training, 15% Validation, 15% Strictly Held-Out Test.
- **Data Augmentation**:
  - `RandomHorizontalFlip(p=0.5)`
  - `RandomVerticalFlip(p=0.2)`
  - `RandomRotation(degrees=15)`
  - `ColorJitter(brightness=0.15, contrast=0.15, saturation=0.15)`
  - `Resize(224, 224)` + Standard ImageNet Normalization

### Training Hyperparameters
- **Optimizer**: AdamW (`lr=1e-3`, `weight_decay=1e-4`)
- **Loss Function**: Cross-Entropy with Label Smoothing (`epsilon=0.05`)
- **LR Scheduler**: CosineAnnealingLR (`eta_min=1e-5`, `T_max=10`)
- **Early Stopping**: Patience = 4 epochs based on Validation Macro-F1.
- **Hardware**: CPU-native training and inference.
- **Selected Checkpoint**: Epoch 8 (Best Validation Macro-F1 = 0.9011).

---

## Evaluation Metrics (Held-Out Test Set: 436 Samples)

| Metric | Score | Target Requirement | Status |
| :--- | :--- | :--- | :--- |
| **Held-Out Test Accuracy** | **96.56%** | >= 95.0% | **EXCEEDED** |
| **Crop-Conditioned Accuracy** | **96.79%** | >= 95.0% | **EXCEEDED** |
| **Macro Precision** | **96.01%** | >= 92.0% | **EXCEEDED** |
| **Macro Recall** | **94.26%** | >= 90.0% | **EXCEEDED** |
| **Macro F1-Score** | **0.9439** | >= 0.930 | **EXCEEDED** |
| **Training Accuracy** | 98.12% | — | Baseline |
| **Validation Accuracy** | 94.21% | — | Baseline |
| **Generalization Gap (Train - Val)** | **+3.91%** | < 8.0% | **HEALTHY** |
| **Validation - Test Gap** | **-2.35%** | Small | **BALANCED** |

---

## Per-Class Performance Breakdown

| Agricultural Class | Precision | Recall | F1-Score | Support |
| :--- | :---: | :---: | :---: | :---: |
| `banana__bacterial_wilt` | 0.9655 | 1.0000 | **0.9825** | 28 |
| `banana__black_sigatoka` | 1.0000 | 0.8333 | **0.9091** | 6 |
| `banana__healthy` | 1.0000 | 1.0000 | **1.0000** | 30 |
| `chilli__bacterial_spot` | 1.0000 | 1.0000 | **1.0000** | 30 |
| `chilli__healthy` | 1.0000 | 1.0000 | **1.0000** | 30 |
| `potato__early_blight` | 1.0000 | 1.0000 | **1.0000** | 30 |
| `potato__healthy` | 1.0000 | 1.0000 | **1.0000** | 24 |
| `potato__late_blight` | 1.0000 | 0.9667 | **0.9831** | 30 |
| `rice__bacterial_blight` | 1.0000 | 1.0000 | **1.0000** | 6 |
| `rice__brown_spot` | 1.0000 | 0.5000 | **0.6667** | 6 |
| `rice__leaf_smut` | 0.6667 | 1.0000 | **0.8000** | 6 |
| `tomato__bacterial_spot` | 0.9310 | 0.9000 | **0.9153** | 30 |
| `tomato__early_blight` | 0.9333 | 0.9333 | **0.9333** | 30 |
| `tomato__healthy` | 1.0000 | 1.0000 | **1.0000** | 30 |
| `tomato__late_blight` | 0.8824 | 1.0000 | **0.9375** | 30 |
| `tomato__leaf_mold` | 0.9677 | 1.0000 | **0.9836** | 30 |
| `tomato__septoria_leaf_spot` | 1.0000 | 0.8667 | **0.9286** | 30 |
| `tomato__yellow_leaf_curl` | 0.9355 | 0.9667 | **0.9508** | 30 |

---

## Known Confusion Pairs & Failure Modes
1. **Early Blight vs. Septoria Leaf Spot (Tomato)**: In early infection stages, pinhead necrotic lesions of Septoria can be confused with incipient Alternaria lesions before concentric rings become pronounced. Grad-CAM visualizes whether the model focuses on diffuse halos or target-board center rings.
2. **Rice Brown Spot vs. Leaf Smut**: Under low lighting or camera blur, minute dark spots on rice can exhibit shared visual features; THUNAI's confidence thresholding flags low-confidence images (<60%) for human expert review.
3. **Severe Glare & Direct Flash**: Direct flash photography washes out subtle chlorotic halos and produces false reflections. Farmers are advised to photograph under diffuse daylight.

---

## Safety Controls & Ethical Governance
- **Zero Dose Hallucination**: The vision classifier only outputs the pathology classification and confidence. Chemical treatment recommendations are strictly decoupled from model inference and routed through the **Dose Lock Safety Engine**, which looks up verified CIB&RC records.
- **Refusal on Low Quality**: Images smaller than 32x32 or non-standard encodings are rejected with HTTP 400.
