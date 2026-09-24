"""
THUNAI Weather API Endpoint
Combines real Open-Meteo forecasts with deterministic spray safety evaluations.
"""

from fastapi import APIRouter, Query
from backend.app.schemas.schemas import WeatherResponse, SpraySafetyDecision
from backend.app.services.weather_service import WeatherService
from backend.app.services.spray_safety import SpraySafetyEngine

router = APIRouter(prefix="/weather", tags=["Weather Intelligence"])

@router.get("", response_model=WeatherResponse)
async def get_weather(
    lat: float = Query(11.0168, description="Latitude"),
    lon: float = Query(76.9558, description="Longitude"),
    district: str = Query("Coimbatore", description="District or Village Name")
):
    raw_data = await WeatherService.fetch_weather_data(lat, lon)
    parsed = WeatherService.parse_weather_response(raw_data, district=district)
    
    # Evaluate Spray Safety
    spray_decision = SpraySafetyEngine.evaluate(
        current_weather=parsed["current"],
        hourly_forecast=parsed["hourly_forecast"]
    )
    
    parsed["spray_safety"] = spray_decision
    return parsed
