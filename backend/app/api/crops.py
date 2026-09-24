"""
THUNAI Crop Suitability & Recommendation API Endpoint
Provides location, season, and soil-aware crop suitability matrices.
"""

from fastapi import APIRouter, Query
from backend.app.schemas.schemas import CropRecommendationResponse
from backend.app.services.crop_service import CropRecommendationService

router = APIRouter(prefix="/crops", tags=["Crop Suitability Engine"])

@router.get("/recommend", response_model=CropRecommendationResponse)
async def recommend_crops(
    location: str = Query("Coimbatore", description="District or Region"),
    temperature: float = Query(28.5, description="Ambient Temperature in Celsius"),
    rainfall: float = Query(750.0, description="Annual/Seasonal rainfall in mm"),
    soil_type: str = Query("Red Loam", description="Soil Type"),
    soil_ph: float = Query(7.4, description="Soil pH value")
):
    recommendations = CropRecommendationService.recommend_crops(
        location=location,
        temperature_c=temperature,
        rainfall_mm=rainfall,
        soil_type=soil_type,
        soil_ph=soil_ph
    )
    return recommendations
