# THUNAI Dataset Sources & Data Provenance Register

This document provides a complete, auditable registry of all biological image datasets, meteorological feeds, pedological databases, and statutory pesticide repositories integrated into the **THUNAI Agricultural Decision Support Platform**.

---

## 1. Plant Pathology Datasets

### A. PlantVillage Dataset
- **Dataset Name**: PlantVillage (Open Access Crop Pathology Repository)
- **Source / Repository**: [spMohanty/PlantVillage-Dataset](https://github.com/spMohanty/PlantVillage-Dataset)
- **License**: Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)
- **Primary Publication**: Hughes, D., & Salathé, M. (2015). *An open access repository of images on plant health to enable the development of mobile disease diagnostics*. arXiv:1511.08060.
- **Crops Included**: Tomato (*Solanum lycopersicum*), Potato (*Solanum tuberosum*), Pepper/Chilli (*Capsicum annuum*)
- **Diseases & Classes Covered**:
  1. `tomato__early_blight` (*Alternaria solani*)
  2. `tomato__late_blight` (*Phytophthora infestans*)
  3. `tomato__bacterial_spot` (*Xanthomonas perforans*)
  4. `tomato__septoria_leaf_spot` (*Septoria lycopersici*)
  5. `tomato__leaf_mold` (*Passalora fulva*)
  6. `tomato__yellow_leaf_curl` (TYLCV Begomovirus)
  7. `tomato__healthy`
  8. `potato__early_blight` (*Alternaria solani*)
  9. `potato__late_blight` (*Phytophthora infestans*)
  10. `potato__healthy`
  11. `chilli__bacterial_spot` (*Xanthomonas euvesicatoria*)
  12. `chilli__healthy`
- **Total Images Sampled & Cleaned**: 2,352 images (balanced and deduplicated)
- **Preprocessing Pipeline**:
  - Image integrity verification via PIL `verify()`
  - MD5 hash computation for strict duplicate removal
  - Stratified 70% Train, 15% Validation, 15% Held-Out Test split
  - Resolution normalization to 224x224 RGB
  - Data augmentation (RandomHorizontalFlip, RandomVerticalFlip, RandomRotation(15°), ColorJitter)

---

### B. Rice Leaf Disease Dataset
- **Dataset Name**: Rice Leaf Disease Classification Dataset
- **Source / Repository**: [MHassaanButt/Rice-Disease-Classfication](https://github.com/MHassaanButt/Rice-Disease-Classfication)
- **License**: Open Academic / Research Use
- **Primary Institution**: Agricultural University Research Repository
- **Crop**: Rice / Paddy (*Oryza sativa*)
- **Diseases & Classes Covered**:
  1. `rice__bacterial_blight` (*Xanthomonas oryzae pv. oryzae*)
  2. `rice__brown_spot` (*Bipolaris oryzae*)
  3. `rice__leaf_smut` (*Entyloma oryzae*)
- **Total Clean Images**: 120 images
- **Preprocessing Pipeline**:
  - Verification of RGB channels and aspect ratio
  - Stratified Train/Val/Test allocation (seed=42)
  - Resize to 224x224 with ImageNet normalization

---

### C. Banana Leaf Disease Dataset
- **Dataset Name**: Banana Leaf Disease Classification Dataset
- **Source / Repository**: [apatawari/BananaLeafDiseaseClassification](https://github.com/apatawari/BananaLeafDiseaseClassification)
- **License**: Open Source / Academic Research
- **Crop**: Banana (*Musa paradisiaca*)
- **Diseases & Classes Covered**:
  1. `banana__black_sigatoka` (*Pseudocercospora fijiensis*)
  2. `banana__bacterial_wilt` (*Xanthomonas vasicola*)
  3. `banana__healthy`
- **Total Clean Images**: 415 images
- **Preprocessing Pipeline**:
  - Deduplication via MD5 hash comparison
  - Uniform 224x224 interpolation
  - Stratified 70/15/15 split

---

## 2. Weather & Agro-Meteorological Data Source

### Open-Meteo Weather API
- **Provider**: Open-Meteo GmbH
- **Endpoint**: `https://api.open-meteo.com/v1/forecast`
- **License**: Non-commercial / Attribution Open Access (CC BY 4.0)
- **Underlying Models**: Seamless blending of ECMWF IFS (Integrated Forecasting System), NOAA GFS, and DWD ICON.
- **Variables Retrieved**:
  - 2m Ambient Temperature (°C)
  - Relative Humidity (%)
  - Precipitation (mm) & Precipitation Probability (%)
  - 10m Wind Speed & Gusts (km/h)
  - WMO Weather Codes (0-99)
- **Update Frequency**: Hourly rolling forecasts up to 7 days ahead.

---

## 3. Pedological & Soil Intelligence Sources

### ICAR - National Bureau of Soil Survey and Land Use Planning (NBSS&LUP)
- **Provider**: Indian Council of Agricultural Research (ICAR), Department of Agricultural Research and Education (DARE).
- **Portal**: [Soil Health Card Portal (Government of India)](https://soilhealth.dac.gov.in)
- **Coverage**: District-wise soil resource mapping for Indian agro-ecological sub-regions.
- **Attributes Mapped**:
  - Dominant soil taxonomy (Vertisols, Inceptisols, Alfisols, Entisols)
  - Typical pH ranges and calcareous nodule horizons
  - Organic carbon brackets (Low < 0.5%, Medium 0.5-0.75%, High > 0.75%)
  - Available macro-nutrients (N, P, K)

---

## 4. Pesticide Statutory & Safety References ("Dose Lock")

### A. Central Insecticides Board & Registration Committee (CIB&RC)
- **Authority**: Directorate of Plant Protection, Quarantine & Storage, Ministry of Agriculture & Farmers Welfare, Government of India.
- **Statutory Act**: Insecticides Act, 1968.
- **Reference**: *Major Uses of Pesticides (Registered Fungicides & Insecticides in India)*.
- **Portal**: [https://cibrc.gov.in](https://cibrc.gov.in)
- **Function in THUNAI**: Source of truth for registered formulations, maximum label dosages, and pre-harvest intervals (PHI).

### B. Tamil Nadu Agricultural University (TNAU) Agritech Portal
- **Authority**: TNAU Directorate of Extension Education, Coimbatore.
- **Reference**: *TNAU Crop Protection Guide (CPG) - Agriculture & Horticulture*.
- **Portal**: [https://agritech.tnau.ac.in](https://agritech.tnau.ac.in)
- **Function in THUNAI**: Immediate cultural practices, bio-agent thresholds (e.g. *Trichoderma*, *Pseudomonas*), and spray volumes (L/ha).

---

## 5. Agricultural Extension & Expert Helpline Directory

- **National Kisan Call Center (KCC)**: 1800-180-1551 (All India, Toll-Free, 22 Languages)
- **TNAU Agritech Helpline**: 1800-425-1660 (Tamil Nadu, Toll-Free)
- **District Krishi Vigyan Kendras (KVK)**: Direct contact records for Coimbatore, Tiruppur, Salem, Thanjavur, Madurai, Guntur, Pune, Shimoga, Karnal.
