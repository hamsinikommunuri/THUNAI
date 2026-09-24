"""
THUNAI Data Preparation & Deduplication Pipeline
=================================================
Processes raw downloaded agricultural datasets across 5 crops:
- Tomato
- Potato
- Pepper / Chilli
- Rice / Paddy
- Banana

Features:
- File integrity checks (detect and discard corrupted/truncated images)
- MD5 hash deduplication (prevent duplicate images within and across splits)
- Class balancing (prevents severe class imbalance)
- Stratified Train (70%), Validation (15%), Test (15%) leak-free splits
- Extraction of benchmark sample test images for evaluation and manual testing
- Manifest generation and distribution chart generation
"""

import os
import glob
import hashlib
import json
import shutil
import random
from collections import defaultdict
from PIL import Image
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# Fixed random seed for reproducibility
RANDOM_SEED = 42
random.seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RAW_PV_DIR = os.path.join(BASE_DIR, "ml", "data", "plantvillage_repo", "raw", "color")
RAW_RICE_DIR = os.path.join(BASE_DIR, "ml", "data", "rice_repo", "Dataset")
RAW_BANANA_DIR = os.path.join(BASE_DIR, "ml", "data", "banana_dataset", "training")
PROCESSED_DIR = os.path.join(BASE_DIR, "ml", "data", "processed")
ARTIFACTS_DIR = os.path.join(BASE_DIR, "ml", "artifacts")
SAMPLES_DIR = os.path.join(BASE_DIR, "datasets", "samples")

os.makedirs(PROCESSED_DIR, exist_ok=True)
os.makedirs(ARTIFACTS_DIR, exist_ok=True)
os.makedirs(SAMPLES_DIR, exist_ok=True)

# Standardized class definitions across crops
CLASS_MAPPING = {
    # Tomato
    "Tomato___Early_blight": ("tomato", "early_blight", "Tomato Early Blight", "Alternaria solani"),
    "Tomato___Late_blight": ("tomato", "late_blight", "Tomato Late Blight", "Phytophthora infestans"),
    "Tomato___Bacterial_spot": ("tomato", "bacterial_spot", "Tomato Bacterial Spot", "Xanthomonas perforans"),
    "Tomato___Septoria_leaf_spot": ("tomato", "septoria_leaf_spot", "Tomato Septoria Leaf Spot", "Septoria lycopersici"),
    "Tomato___Leaf_Mold": ("tomato", "leaf_mold", "Tomato Leaf Mold", "Passalora fulva"),
    "Tomato___Tomato_Yellow_Leaf_Curl_Virus": ("tomato", "yellow_leaf_curl", "Tomato Yellow Leaf Curl Virus", "Tomato yellow leaf curl virus"),
    "Tomato___healthy": ("tomato", "healthy", "Tomato Healthy", "Healthy Plant"),

    # Potato
    "Potato___Early_blight": ("potato", "early_blight", "Potato Early Blight", "Alternaria solani"),
    "Potato___Late_blight": ("potato", "late_blight", "Potato Late Blight", "Phytophthora infestans"),
    "Potato___healthy": ("potato", "healthy", "Potato Healthy", "Healthy Plant"),

    # Pepper / Chilli
    "Pepper,_bell___Bacterial_spot": ("chilli", "bacterial_spot", "Chilli Bacterial Spot", "Xanthomonas euvesicatoria"),
    "Pepper,_bell___healthy": ("chilli", "healthy", "Chilli Healthy", "Healthy Plant"),

    # Rice
    "Bacterial leaf blight": ("rice", "bacterial_blight", "Rice Bacterial Leaf Blight", "Xanthomonas oryzae"),
    "Brown spot": ("rice", "brown_spot", "Rice Brown Spot", "Bipolaris oryzae"),
    "Leaf smut": ("rice", "leaf_smut", "Rice Leaf Smut", "Entyloma oryzae"),

    # Banana
    "bbs": ("banana", "black_sigatoka", "Banana Black Sigatoka", "Pseudocercospora fijiensis"),
    "bbw": ("banana", "bacterial_wilt", "Banana Bacterial Wilt", "Xanthomonas vasicola"),
    "healthy": ("banana", "healthy", "Banana Healthy", "Healthy Plant"),
}

# Target max images per class to prevent class imbalance and ensure fast, robust CPU training
MAX_PER_CLASS = 200

def get_file_hash(filepath: str) -> str:
    hasher = hashlib.md5()
    with open(filepath, 'rb') as f:
        buf = f.read(65536)
        while len(buf) > 0:
            hasher.update(buf)
            buf = f.read(65536)
    return hasher.hexdigest()

def verify_and_collect_images():
    print("Collecting and verifying raw dataset files...")
    sources = [
        (RAW_PV_DIR, "PlantVillage"),
        (RAW_RICE_DIR, "RiceLeafDisease"),
        (RAW_BANANA_DIR, "BananaLeafDisease"),
    ]

    seen_hashes = set()
    cleaned_data = defaultdict(list)
    total_raw = 0
    corrupted_count = 0
    duplicate_count = 0

    for source_dir, source_name in sources:
        if not os.path.exists(source_dir):
            print(f"Warning: Directory not found: {source_dir}")
            continue

        for folder_name in os.listdir(source_dir):
            folder_path = os.path.join(source_dir, folder_name)
            if not os.path.isdir(folder_path):
                continue

            if folder_name not in CLASS_MAPPING:
                continue

            crop, disease_id, display_name, pathogen = CLASS_MAPPING[folder_name]
            class_key = f"{crop}__{disease_id}"

            files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) 
                     if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))]
            
            # Shuffle files deterministically before sampling
            random.seed(RANDOM_SEED)
            random.shuffle(files)

            valid_for_class = []
            for fpath in files:
                total_raw += 1
                try:
                    # Check PIL readability & dimensions
                    with Image.open(fpath) as img:
                        img.verify()
                    with Image.open(fpath) as img:
                        w, h = img.size
                        if w < 32 or h < 32:
                            corrupted_count += 1
                            continue
                except Exception:
                    corrupted_count += 1
                    continue

                # Hash deduplication
                fhash = get_file_hash(fpath)
                if fhash in seen_hashes:
                    duplicate_count += 1
                    continue

                seen_hashes.add(fhash)
                valid_for_class.append((fpath, fhash, source_name))

                if len(valid_for_class) >= MAX_PER_CLASS:
                    break

            cleaned_data[class_key].extend(valid_for_class)
            print(f"  Processed {folder_name} -> {class_key}: {len(valid_for_class)} clean images (Source: {source_name})")

    print(f"\nVerification Complete:")
    print(f"  Total raw files inspected: {total_raw}")
    print(f"  Corrupted / invalid removed: {corrupted_count}")
    print(f"  Exact duplicates removed: {duplicate_count}")
    print(f"  Total unique clean images: {sum(len(v) for v in cleaned_data.values())}")
    return cleaned_data

def create_splits_and_manifest(cleaned_data):
    print("\nCreating stratified Train (70%), Validation (15%), Test (15%) splits...")
    splits = {"train": [], "val": [], "test": []}
    class_stats = {}
    test_sample_metadata = []

    # Clear processed dir
    for split in ["train", "val", "test"]:
        split_dir = os.path.join(PROCESSED_DIR, split)
        if os.path.exists(split_dir):
            shutil.rmtree(split_dir)
        os.makedirs(split_dir, exist_ok=True)

    sorted_classes = sorted(cleaned_data.keys())
    class_to_idx = {cls: idx for idx, cls in enumerate(sorted_classes)}

    for class_key in sorted_classes:
        items = cleaned_data[class_key]
        random.seed(RANDOM_SEED)
        random.shuffle(items)
        n = len(items)
        n_train = int(n * 0.70)
        n_val = int(n * 0.15)
        # Remaining goes to test
        train_items = items[:n_train]
        val_items = items[n_train:n_train + n_val]
        test_items = items[n_train + n_val:]

        split_dict = {
            "train": train_items,
            "val": val_items,
            "test": test_items
        }

        class_stats[class_key] = {
            "total": n,
            "train": len(train_items),
            "val": len(val_items),
            "test": len(test_items),
            "class_idx": class_to_idx[class_key]
        }

        for split_name, split_files in split_dict.items():
            target_class_dir = os.path.join(PROCESSED_DIR, split_name, class_key)
            os.makedirs(target_class_dir, exist_ok=True)

            for idx, (src_path, fhash, source_name) in enumerate(split_files):
                ext = os.path.splitext(src_path)[1].lower()
                dest_filename = f"{class_key}_{idx:04d}{ext}"
                dest_path = os.path.join(target_class_dir, dest_filename)
                shutil.copy2(src_path, dest_path)

                record = {
                    "filename": dest_filename,
                    "class": class_key,
                    "class_idx": class_to_idx[class_key],
                    "crop": class_key.split("__")[0],
                    "disease": class_key.split("__")[1],
                    "hash": fhash,
                    "source": source_name,
                    "rel_path": os.path.relpath(dest_path, BASE_DIR)
                }
                splits[split_name].append(record)

                # Save up to 2 test samples per class into datasets/samples for verification testing
                if split_name == "test" and idx < 2:
                    sample_dest = os.path.join(SAMPLES_DIR, f"sample_{class_key}_{idx+1}{ext}")
                    shutil.copy2(src_path, sample_dest)
                    test_sample_metadata.append({
                        "sample_file": os.path.basename(sample_dest),
                        "crop": class_key.split("__")[0],
                        "true_disease": class_key.split("__")[1],
                        "class_key": class_key,
                        "path": os.path.relpath(sample_dest, BASE_DIR)
                    })

    # Save manifest
    manifest = {
        "random_seed": RANDOM_SEED,
        "num_classes": len(sorted_classes),
        "class_to_idx": class_to_idx,
        "classes": sorted_classes,
        "class_stats": class_stats,
        "splits_count": {k: len(v) for k, v in splits.items()},
        "test_samples": test_sample_metadata
    }

    manifest_path = os.path.join(ARTIFACTS_DIR, "dataset_manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    print(f"Saved dataset manifest to {manifest_path}")

    # Plot dataset distribution chart
    plot_distribution(class_stats)

    return manifest

def plot_distribution(class_stats):
    classes = list(class_stats.keys())
    train_counts = [class_stats[c]["train"] for c in classes]
    val_counts = [class_stats[c]["val"] for c in classes]
    test_counts = [class_stats[c]["test"] for c in classes]

    x = np.arange(len(classes))
    width = 0.55

    fig, ax = plt.subplots(figsize=(14, 7))
    ax.bar(x, train_counts, width, label='Train (70%)', color='#2E7D32')
    ax.bar(x, val_counts, width, bottom=train_counts, label='Validation (15%)', color='#81C784')
    bottom_val = [t + v for t, v in zip(train_counts, val_counts)]
    ax.bar(x, test_counts, width, bottom=bottom_val, label='Test (15%)', color='#C8E6C9')

    ax.set_ylabel('Number of Images', fontsize=12, fontweight='bold')
    ax.set_title('THUNAI Agricultural Dataset Distribution Across Classes & Splits', fontsize=14, fontweight='bold', pad=15)
    ax.set_xticks(x)
    ax.set_xticklabels(classes, rotation=45, ha='right', fontsize=9)
    ax.legend(loc='upper right', frameon=True)
    ax.grid(axis='y', linestyle='--', alpha=0.3)
    plt.tight_layout()

    dist_chart_path = os.path.join(ARTIFACTS_DIR, "dataset_distribution.png")
    plt.savefig(dist_chart_path, dpi=200)
    plt.close()
    print(f"Saved distribution plot to {dist_chart_path}")

if __name__ == "__main__":
    cleaned = verify_and_collect_images()
    manifest = create_splits_and_manifest(cleaned)
    print("Data preparation complete!")
