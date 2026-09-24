"""
THUNAI Soil Intelligence API Endpoint
Provides regional estimates and prioritized user lab measurement evaluations.
"""

from typing import Optional
from pydantic import BaseModel
from fastapi import APIRouter, Query, Body
from backend.app.schemas.schemas import SoilResponse, SoilLabMeasurementInput
from backend.app.services.soil_service import SoilService

router = APIRouter(prefix="/soil", tags=["Soil Intelligence"])

class SoilQueryRequest(BaseModel):
    district: Optional[str] = "Coimbatore"
    measurements: Optional[SoilLabMeasurementInput] = None

@router.get("", response_model=SoilResponse)
async def get_regional_soil(
    district: str = Query("Coimbatore", description="District name for regional pedological profile")
):
    profile = SoilService.get_soil_profile(district=district)
    return profile

@router.post("/evaluate", response_model=SoilResponse)
async def evaluate_soil_measurements(payload: SoilQueryRequest):
    measurements_dict = payload.measurements.model_dump(exclude_none=True) if payload.measurements else None
    profile = SoilService.get_soil_profile(
        district=payload.district or "Coimbatore",
        user_measurement=measurements_dict
    )
    return profile
