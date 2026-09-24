"""
THUNAI Core Crop Disease Diagnosis API Endpoint
Processes real image uploads, runs deep learning inference with Grad-CAM,
validates Dose Lock safety, integrates live weather, and constructs Evidence Trace.
"""

import os
import io
import uuid
from datetime import datetime, timezone
from typing import Optional
from PIL import Image

from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.config import settings
from backend.app.db.database import get_db
from backend.app.db.models import DiagnosisRecord
from backend.app.schemas.schemas import DiagnosisResponse
from backend.app.services.weather_service import WeatherService
from backend.app.services.spray_safety import SpraySafetyEngine
from backend.app.services.dose_lock import DoseLockEngine
from backend.app.services.evidence_service import EvidenceTraceService
from ml.inference import run_diagnosis

router = APIRouter(prefix="/diagnosis", tags=["Crop Disease Vision & Diagnosis"])

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
MAX_FILE_SIZE = 15 * 1024 * 1024  # 15 MB

@router.post("/predict", response_model=DiagnosisResponse)
async def predict_disease(
    file: UploadFile = File(..., description="Uploaded crop leaf image"),
    crop: str = Form("tomato", description="Farmer-selected crop (tomato, potato, chilli, rice, banana)"),
    district: Optional[str] = Form("Coimbatore", description="Current district name"),
    latitude: Optional[float] = Form(11.0168, description="Latitude"),
    longitude: Optional[float] = Form(76.9558, description="Longitude"),
    db: AsyncSession = Depends(get_db)
):
    # 1. File Validation
    filename = file.filename or "upload.jpg"
    ext = os.path.splitext(filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file format '{ext}'. Accepted formats: JPEG, PNG, WEBP."
        )

    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File exceeds maximum permissible size of 15MB (Received {len(content)/(1024*1024):.1f}MB)."
        )

    # 2. Image Corruption & Dimensions Check
    try:
        image = Image.open(io.BytesIO(content)).convert("RGB")
        w, h = image.size
        if w < 32 or h < 32:
            raise ValueError("Image dimensions too small for optical feature extraction.")
    except Exception as img_err:
        raise HTTPException(
            status_code=400,
            detail=f"Corrupted or unreadable image file: {str(img_err)}"
        )

    # Save uploaded image locally for audit / dossier reference
    diag_id = str(uuid.uuid4())
    save_filename = f"{diag_id}_{crop}{ext}"
    save_path = os.path.join(settings.UPLOAD_DIR, save_filename)
    try:
        with open(save_path, "wb") as f:
            f.write(content)
        image_url = f"/uploads/{save_filename}"
    except Exception:
        image_url = None

    # 3. Deep Learning Vision Inference with Grad-CAM
    ml_result = run_diagnosis(image, crop_selected=crop)

    predicted_disease = ml_result["common_name"]
    scientific_name = ml_result["scientific_name"]
    pathogen_type = ml_result["pathogen_type"]
    confidence = ml_result["confidence"]
    confidence_tier = ml_result["confidence_tier"]
    top_predictions = ml_result["top_predictions"]
    disease_id = ml_result["disease_id"]
    disease_meta = ml_result["disease_metadata"]
    gradcam_b64 = ml_result["gradcam_base64"]

    # 4. Dose Lock Statutory Verification
    treatment_data = DoseLockEngine.lookup_treatment(crop, disease_id)

    # 5. Live Weather Integration & Spray Safety
    raw_weather = await WeatherService.fetch_weather_data(latitude, longitude)
    parsed_weather = WeatherService.parse_weather_response(raw_weather, district=district)
    spray_decision = SpraySafetyEngine.evaluate(
        current_weather=parsed_weather["current"],
        hourly_forecast=parsed_weather["hourly_forecast"]
    )

    # 6. Verifiable Evidence Trace Construction
    symptoms = disease_meta.get("symptoms", [
        "Foliar necrotic lesions identified across leaf surface.",
        "Chlorotic ring surrounding infected target zones."
    ])
    immediate_actions = disease_meta.get("immediate_actions", [
        "Prune and safely discard heavily spotted lower leaves.",
        "Avoid overhead sprinkler irrigation to keep foliar canopy dry.",
        "Disinfect pruning shears between plants."
    ])
    cultural_control = disease_meta.get("cultural_control", [
        "Ensure wide plant spacing for canopy ventilation.",
        "Adopt drip irrigation at root zone."
    ])
    biological_control = disease_meta.get("biological_control", [
        "Foliar spray of Trichoderma or Pseudomonas bio-agents."
    ])
    monitoring_guidance = disease_meta.get("monitoring_guidance", "Scout twice weekly during early morning.")

    evidence_trace = EvidenceTraceService.build_trace(
        crop=crop,
        predicted_disease=predicted_disease,
        scientific_name=scientific_name,
        confidence=confidence,
        symptoms=symptoms,
        disease_info=disease_meta,
        treatment_info=treatment_data,
        spray_decision=spray_decision
    )

    # 7. Persist Diagnosis Record to Database
    record = DiagnosisRecord(
        id=diag_id,
        crop=crop,
        disease_id=disease_id,
        disease_name=predicted_disease,
        scientific_name=scientific_name,
        confidence=confidence,
        confidence_tier=confidence_tier,
        top_predictions=top_predictions,
        image_url=image_url,
        gradcam_url=None,
        location_district=district,
        location_state="Tamil Nadu",
        latitude=latitude,
        longitude=longitude,
        weather_snapshot=parsed_weather["current"],
        soil_snapshot=None,
        spray_recommendation=spray_decision["decision"],
        spray_reason=spray_decision["primary_reason"],
        treatment_recommended=treatment_data,
        dose_locked=True
    )
    db.add(record)
    await db.commit()

    timestamp_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    return DiagnosisResponse(
        diagnosis_id=diag_id,
        crop=crop,
        crop_display=crop.title(),
        predicted_disease=predicted_disease,
        scientific_name=scientific_name,
        pathogen_type=pathogen_type,
        confidence=confidence,
        confidence_tier=confidence_tier,
        top_predictions=top_predictions,
        gradcam_available=(gradcam_b64 is not None),
        gradcam_image_base64=gradcam_b64,
        original_image_url=image_url,
        symptoms=symptoms,
        immediate_actions=immediate_actions,
        cultural_control=cultural_control,
        biological_control=biological_control,
        monitoring_guidance=monitoring_guidance,
        dose_lock=treatment_data,
        spray_safety=spray_decision,
        evidence_trace=evidence_trace,
        requires_second_opinion=ml_result["requires_escalation"],
        escalation_reason=ml_result["escalation_reason"],
        timestamp=timestamp_str
    )
