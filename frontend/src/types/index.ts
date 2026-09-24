/**
 * THUNAI TypeScript Types
 */

export interface LocationData {
  latitude: number;
  longitude: number;
  village_or_town: string;
  district: string;
  state: string;
  country: string;
  display_name: string;
  source: string;
  timestamp: string;
}

export interface WeatherCurrent {
  temperature_c: number;
  humidity_percent: number;
  precipitation_mm: number;
  precipitation_probability: number;
  wind_speed_kmh: number;
  wind_gust_kmh: number;
  weather_condition: string;
  weather_code: number;
}

export interface HourlyForecastItem {
  time: string;
  temperature_c: number;
  precipitation_probability: number;
  precipitation_mm: number;
  wind_speed_kmh: number;
  is_safe_for_spraying: boolean;
}

export interface DailyForecastItem {
  date: string;
  temp_max_c: number;
  temp_min_c: number;
  precipitation_sum_mm: number;
  precipitation_probability_max: number;
  weather_condition: string;
}

export interface SpraySafetyDecision {
  decision: 'SPRAY NOW' | 'WAIT' | 'NOT RECOMMENDED';
  badge_color: 'emerald' | 'amber' | 'rose';
  primary_reason: string;
  detailed_explanation: string;
  recommended_window: string;
  risk_factors: string[];
  rule_evaluated: string;
}

export interface WeatherData {
  district: string;
  latitude: number;
  longitude: number;
  current: WeatherCurrent;
  spray_safety: SpraySafetyDecision;
  hourly_forecast: HourlyForecastItem[];
  daily_forecast: DailyForecastItem[];
  source: string;
  updated_at: string;
}

export interface SoilProfile {
  data_type: 'REGIONAL_ESTIMATE' | 'USER_MEASUREMENT';
  warning_notice: string;
  district: string;
  state: string;
  dominant_soil_type: string;
  ph_range: string;
  ph_category: string;
  organic_carbon: string;
  nitrogen_condition: string;
  phosphorus_condition: string;
  potassium_condition: string;
  texture: string;
  drainage: string;
  regional_characteristics: string;
  management_advice: string;
  source: string;
  source_url: string;
}

export interface SoilLabInputs {
  ph?: number;
  nitrogen_kg_ha?: number;
  phosphorus_kg_ha?: number;
  potassium_kg_ha?: number;
  organic_carbon_percent?: number;
  soil_type?: string;
  soil_moisture_percent?: number;
}

export interface RecommendedCrop {
  crop_id: string;
  name_en: string;
  name_ta: string;
  scientific_name: string;
  suitability: 'High' | 'Moderate' | 'Low';
  suitability_score: number;
  reasons: string[];
  ideal_temperature_range: string;
  water_requirement: string;
  economic_importance: string;
  source: string;
}

export interface CropRecommendationData {
  location: string;
  current_season: string;
  temperature_c: number;
  rainfall_annual_mm: number;
  soil_type: string;
  engine_type: string;
  scientific_basis: string;
  recommended_crops: RecommendedCrop[];
}

export interface PredictionCandidate {
  crop: string;
  disease_id: string;
  common_name: string;
  scientific_name: string;
  confidence: number;
  confidence_percent: number;
}

export interface DoseLockTreatment {
  is_available: boolean;
  status_text: string;
  treatment_id?: string;
  active_ingredient?: string;
  formulation?: string;
  chemical_group?: string;
  dosage_per_liter?: string;
  dosage_per_hectare?: string;
  application_method?: string;
  waiting_period_days?: number;
  regulatory_status?: string;
  registration_certificate?: string;
  source?: string;
  source_url?: string;
  cautionary_notes?: string;
}

export interface EvidenceTraceStep {
  step_number: number;
  title: string;
  subtitle: string;
  description: string;
  badge: string;
  source_citation?: string;
  source_url?: string;
}

export interface DiagnosisResponse {
  diagnosis_id: string;
  crop: string;
  crop_display: string;
  predicted_disease: string;
  scientific_name: string;
  pathogen_type: string;
  confidence: number;
  confidence_tier: 'High' | 'Moderate' | 'Low';
  top_predictions: PredictionCandidate[];
  gradcam_available: boolean;
  gradcam_image_base64?: string;
  original_image_url?: string;
  symptoms: string[];
  immediate_actions: string[];
  cultural_control: string[];
  biological_control: string[];
  monitoring_guidance: string;
  dose_lock: DoseLockTreatment;
  spray_safety: SpraySafetyDecision;
  evidence_trace: EvidenceTraceStep[];
  requires_second_opinion: boolean;
  escalation_reason?: string;
  timestamp: string;
}

export interface HistoryItem {
  id: string;
  crop: string;
  disease_name: string;
  scientific_name?: string;
  confidence: number;
  confidence_tier: string;
  image_url?: string;
  location_district?: string;
  spray_recommendation?: string;
  created_at: string;
}

export interface ExpertDossierResponse {
  dossier_id: string;
  status: string;
  crop: string;
  district: string;
  timestamp: string;
  kvk_center: {
    name: string;
    district: string;
    state: string;
    address: string;
    phone: string;
    email: string;
    officer_in_charge: string;
    specialization: string[];
  };
  helpline: string;
  downloadable_dossier_summary: any;
  dispatch_message: string;
}
