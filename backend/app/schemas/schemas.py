"""
THUNAI Pydantic Schemas for API Requests and Responses
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

# --- Location & Geocoding Schemas ---
class LocationRequest(BaseModel):
    latitude: float = Field(..., description="Latitude coordinate")
    longitude: float = Field(..., description="Longitude coordinate")

class LocationResponse(BaseModel):
    latitude: float
    longitude: float
    village_or_town: str
    district: str
    state: str
    country: str
    display_name: str
    source: str
    timestamp: str

# --- Weather Schemas ---
class WeatherCurrent(BaseModel):
    temperature_c: float
    humidity_percent: float
    precipitation_mm: float
    precipitation_probability: float
    wind_speed_kmh: float
    wind_gust_kmh: float
    weather_condition: str
    weather_code: int

class HourlyForecastItem(BaseModel):
    time: str
    temperature_c: float
    precipitation_probability: float
    precipitation_mm: float
    wind_speed_kmh: float
    is_safe_for_spraying: bool

class DailyForecastItem(BaseModel):
    date: str
    temp_max_c: float
    temp_min_c: float
    precipitation_sum_mm: float
    precipitation_probability_max: float
    weather_condition: str

class SpraySafetyDecision(BaseModel):
    decision: str  # SPRAY NOW, WAIT, NOT RECOMMENDED
    badge_color: str  # green, amber, red
    primary_reason: str
    detailed_explanation: str
    recommended_window: str
    risk_factors: List[str]
    rule_evaluated: str

class WeatherResponse(BaseModel):
    district: str
    latitude: float
    longitude: float
    current: WeatherCurrent
    spray_safety: SpraySafetyDecision
    hourly_forecast: List[HourlyForecastItem]
    daily_forecast: List[DailyForecastItem]
    source: str
    updated_at: str

# --- Soil Intelligence Schemas ---
class SoilLabMeasurementInput(BaseModel):
    ph: Optional[float] = None
    nitrogen_kg_ha: Optional[float] = None
    phosphorus_kg_ha: Optional[float] = None
    potassium_kg_ha: Optional[float] = None
    organic_carbon_percent: Optional[float] = None
    soil_type: Optional[str] = None
    soil_moisture_percent: Optional[float] = None

class SoilResponse(BaseModel):
    data_type: str  # REGIONAL_ESTIMATE or USER_MEASUREMENT
    warning_notice: str
    district: str
    state: str
    dominant_soil_type: str
    ph_range: str
    ph_category: str
    organic_carbon: str
    nitrogen_condition: str
    phosphorus_condition: str
    potassium_condition: str
    texture: str
    drainage: str
    regional_characteristics: str
    management_advice: str
    source: str
    source_url: str

# --- Crop Suitability Schemas ---
class CropSuitabilityItem(BaseModel):
    crop_id: str
    name_en: str
    name_ta: str
    scientific_name: str
    suitability: str  # High, Moderate, Low
    suitability_score: int  # 0 to 100
    reasons: List[str]
    ideal_temperature_range: str
    water_requirement: str
    economic_importance: str
    source: str

class CropRecommendationResponse(BaseModel):
    location: str
    current_season: str
    temperature_c: float
    rainfall_annual_mm: float
    soil_type: str
    engine_type: str  # AGRONOMIC_RULE_ENGINE
    scientific_basis: str
    recommended_crops: List[CropSuitabilityItem]

# --- ML Disease Diagnosis Schemas ---
class PredictionCandidate(BaseModel):
    crop: str
    disease_id: str
    common_name: str
    scientific_name: str
    confidence: float
    confidence_percent: float

class DoseLockTreatment(BaseModel):
    is_available: bool
    status_text: str
    treatment_id: Optional[str] = None
    active_ingredient: Optional[str] = None
    formulation: Optional[str] = None
    chemical_group: Optional[str] = None
    dosage_per_liter: Optional[str] = None
    dosage_per_hectare: Optional[str] = None
    application_method: Optional[str] = None
    waiting_period_days: Optional[int] = None
    regulatory_status: Optional[str] = None
    registration_certificate: Optional[str] = None
    source: Optional[str] = None
    source_url: Optional[str] = None
    cautionary_notes: Optional[str] = None

class EvidenceTraceStep(BaseModel):
    step_number: int
    title: str
    subtitle: str
    description: str
    badge: str
    source_citation: Optional[str] = None
    source_url: Optional[str] = None

class DiagnosisResponse(BaseModel):
    diagnosis_id: str
    crop: str
    crop_display: str
    predicted_disease: str
    scientific_name: str
    pathogen_type: str
    confidence: float
    confidence_tier: str  # High (>=0.80), Moderate (0.60-0.80), Low (<0.60)
    top_predictions: List[PredictionCandidate]
    gradcam_available: bool
    gradcam_image_base64: Optional[str] = None
    original_image_url: Optional[str] = None
    
    # Action Narrative
    symptoms: List[str]
    immediate_actions: List[str]
    cultural_control: List[str]
    biological_control: List[str]
    monitoring_guidance: str
    
    # Dose Lock
    dose_lock: DoseLockTreatment
    
    # Weather Shift & Spray Safety
    spray_safety: SpraySafetyDecision
    
    # Evidence Trace
    evidence_trace: List[EvidenceTraceStep]
    
    # Escalation trigger flag
    requires_second_opinion: bool
    escalation_reason: Optional[str] = None
    
    timestamp: str

# --- Expert Escalation Schemas ---
class ExpertEscalationRequest(BaseModel):
    diagnosis_id: Optional[str] = None
    crop: str
    district: str
    reason: str
    farmer_phone: Optional[str] = None
    additional_notes: Optional[str] = None

class ExpertEscalationResponse(BaseModel):
    dossier_id: str
    status: str
    crop: str
    district: str
    timestamp: str
    kvk_center: Dict[str, Any]
    helpline: str
    downloadable_dossier_summary: Dict[str, Any]
    dispatch_message: str

# --- History Schema ---
class HistoryItemResponse(BaseModel):
    id: str
    crop: str
    disease_name: str
    scientific_name: Optional[str]
    confidence: float
    confidence_tier: str
    image_url: Optional[str]
    location_district: Optional[str]
    spray_recommendation: Optional[str]
    created_at: str
