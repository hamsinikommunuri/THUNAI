"""
THUNAI Dose Lock Statutory Treatment API Endpoint
Allows direct querying of registered chemical and biological formulations.
"""

from fastapi import APIRouter, Path
from backend.app.schemas.schemas import DoseLockTreatment
from backend.app.services.dose_lock import DoseLockEngine

router = APIRouter(prefix="/treatments", tags=["Dose Lock Statutory Verification"])

@router.get("/{crop}/{disease_id}", response_model=DoseLockTreatment)
async def get_verified_treatment(
    crop: str = Path(..., description="Crop name (e.g. tomato, potato, chilli, rice, banana)"),
    disease_id: str = Path(..., description="Pathology identifier (e.g. early_blight, late_blight)")
):
    treatment = DoseLockEngine.lookup_treatment(crop=crop, disease_id=disease_id)
    return treatment
