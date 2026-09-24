/**
 * THUNAI API Client Service
 */

import {
  LocationData,
  WeatherData,
  SoilProfile,
  SoilLabInputs,
  CropRecommendationData,
  DiagnosisResponse,
  HistoryItem,
  ExpertDossierResponse,
  DoseLockTreatment
} from '../types';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export class ThunaiApiClient {
  static async reverseGeocode(latitude: number, longitude: number): Promise<LocationData> {
    const res = await fetch(`${API_BASE}/api/location/reverse-geocode`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ latitude, longitude })
    });
    if (!res.ok) throw new Error(`Geocoding failed: ${res.statusText}`);
    return res.json();
  }

  static async searchLocations(query: string): Promise<any[]> {
    const res = await fetch(`${API_BASE}/api/location/search?query=${encodeURIComponent(query)}`);
    if (!res.ok) throw new Error(`Search failed: ${res.statusText}`);
    const data = await res.json();
    return data.results || [];
  }

  static async getWeather(lat: number, lon: number, district: string): Promise<WeatherData> {
    const res = await fetch(`${API_BASE}/api/weather?lat=${lat}&lon=${lon}&district=${encodeURIComponent(district)}`);
    if (!res.ok) throw new Error(`Weather fetch failed: ${res.statusText}`);
    return res.json();
  }

  static async getRegionalSoil(district: string): Promise<SoilProfile> {
    const res = await fetch(`${API_BASE}/api/soil?district=${encodeURIComponent(district)}`);
    if (!res.ok) throw new Error(`Soil fetch failed: ${res.statusText}`);
    return res.json();
  }

  static async evaluateSoilMeasurements(district: string, measurements: SoilLabInputs): Promise<SoilProfile> {
    const res = await fetch(`${API_BASE}/api/soil/evaluate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ district, measurements })
    });
    if (!res.ok) throw new Error(`Soil evaluation failed: ${res.statusText}`);
    return res.json();
  }

  static async getCropRecommendations(
    location: string,
    temperature: number,
    rainfall: number,
    soilType: string,
    soilPh: number
  ): Promise<CropRecommendationData> {
    const params = new URLSearchParams({
      location,
      temperature: temperature.toString(),
      rainfall: rainfall.toString(),
      soil_type: soilType,
      soil_ph: soilPh.toString()
    });
    const res = await fetch(`${API_BASE}/api/crops/recommend?${params.toString()}`);
    if (!res.ok) throw new Error(`Crop recommendation failed: ${res.statusText}`);
    return res.json();
  }

  static async diagnoseCrop(
    imageFile: File,
    crop: string,
    district: string,
    latitude: number,
    longitude: number
  ): Promise<DiagnosisResponse> {
    const formData = new FormData();
    formData.append('file', imageFile);
    formData.append('crop', crop);
    formData.append('district', district);
    formData.append('latitude', latitude.toString());
    formData.append('longitude', longitude.toString());

    const res = await fetch(`${API_BASE}/api/diagnosis/predict`, {
      method: 'POST',
      body: formData
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(err.detail || 'Diagnosis failed');
    }
    return res.json();
  }

  static async getTreatment(crop: string, diseaseId: string): Promise<DoseLockTreatment> {
    const res = await fetch(`${API_BASE}/api/treatments/${encodeURIComponent(crop)}/${encodeURIComponent(diseaseId)}`);
    if (!res.ok) throw new Error(`Treatment lookup failed: ${res.statusText}`);
    return res.json();
  }

  static async requestSecondOpinion(payload: {
    crop: string;
    district: string;
    diagnosis_id?: string;
    reason: string;
    farmer_phone?: string;
  }): Promise<ExpertDossierResponse> {
    const res = await fetch(`${API_BASE}/api/expert/escalation`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    if (!res.ok) throw new Error(`Escalation request failed: ${res.statusText}`);
    return res.json();
  }

  static async getHistory(limit: number = 20): Promise<HistoryItem[]> {
    const res = await fetch(`${API_BASE}/api/history?limit=${limit}`);
    if (!res.ok) throw new Error(`History fetch failed: ${res.statusText}`);
    return res.json();
  }
}
