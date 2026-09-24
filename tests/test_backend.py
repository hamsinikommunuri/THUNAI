"""
THUNAI Automated Test Suite
Uses FastAPI TestClient context manager to trigger lifespan and test all endpoints.
"""

import os
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SAMPLES_DIR = os.path.join(BASE_DIR, "datasets", "samples")

@pytest.fixture(scope="session")
def client():
    with TestClient(app) as c:
        yield c

def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["features"]["crop_vision_ml"] is True
    assert data["features"]["dose_lock_safety"] is True

def test_location_reverse_geocode(client):
    response = client.post("/api/location/reverse-geocode", json={
        "latitude": 11.0168,
        "longitude": 76.9558
    })
    assert response.status_code == 200
    data = response.json()
    assert "district" in data
    assert "Tamil Nadu" in data["state"] or "Tamil Nadu" in data["display_name"]
    assert "timestamp" in data

def test_location_manual_search(client):
    response = client.get("/api/location/search?query=Coimbatore")
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert len(data["results"]) > 0
    assert any("Coimbatore" in r["district"] for r in data["results"])

def test_weather_and_spray_safety(client):
    response = client.get("/api/weather?lat=11.0168&lon=76.9558&district=Coimbatore")
    assert response.status_code == 200
    data = response.json()
    assert "current" in data
    assert "temperature_c" in data["current"]
    assert "spray_safety" in data
    assert data["spray_safety"]["decision"] in ["SPRAY NOW", "WAIT", "NOT RECOMMENDED"]
    assert "recommended_window" in data["spray_safety"]
    assert len(data["hourly_forecast"]) > 0

def test_soil_regional_estimate(client):
    response = client.get("/api/soil?district=Coimbatore")
    assert response.status_code == 200
    data = response.json()
    assert data["data_type"] == "REGIONAL_ESTIMATE"
    assert "Regional soil estimate" in data["warning_notice"]
    assert "Red Loam" in data["dominant_soil_type"]
    assert "ph_range" in data

def test_soil_user_lab_measurement_override(client):
    payload = {
        "district": "Coimbatore",
        "measurements": {
            "ph": 6.8,
            "nitrogen_kg_ha": 310.5,
            "phosphorus_kg_ha": 24.0,
            "potassium_kg_ha": 290.0,
            "organic_carbon_percent": 0.72,
            "soil_type": "Clay Loam"
        }
    }
    response = client.post("/api/soil/evaluate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["data_type"] == "USER_MEASUREMENT"
    assert "Verified User Soil Test" in data["warning_notice"]
    assert data["ph_range"] == "6.8"
    assert "310.5 kg/ha" in data["nitrogen_condition"]

def test_crop_suitability_recommendations(client):
    response = client.get("/api/crops/recommend?location=Coimbatore&temperature=27.5&rainfall=720&soil_type=Red+Loam&soil_ph=7.2")
    assert response.status_code == 200
    data = response.json()
    assert data["engine_type"] == "AGRONOMIC_RULE_ENGINE"
    assert len(data["recommended_crops"]) >= 4
    top_crop = data["recommended_crops"][0]
    assert top_crop["suitability"] in ["High", "Moderate"]
    assert len(top_crop["reasons"]) > 0

def test_valid_image_diagnosis(client):
    sample_file = os.path.join(SAMPLES_DIR, "sample_tomato__early_blight_1.jpg")
    assert os.path.exists(sample_file), f"Test sample missing: {sample_file}"

    with open(sample_file, "rb") as f:
        file_bytes = f.read()

    files = {"file": ("sample_tomato__early_blight_1.jpg", file_bytes, "image/jpeg")}
    data = {
        "crop": "tomato",
        "district": "Coimbatore",
        "latitude": "11.0168",
        "longitude": "76.9558"
    }

    response = client.post("/api/diagnosis/predict", files=files, data=data)
    assert response.status_code == 200
    res = response.json()
    assert res["crop"] == "tomato"
    assert "Early Blight" in res["predicted_disease"]
    assert res["scientific_name"] == "Alternaria solani"
    assert res["confidence"] > 0.80
    assert res["confidence_tier"] == "High"
    assert res["gradcam_available"] is True
    assert res["gradcam_image_base64"] is not None
    assert len(res["symptoms"]) > 0
    assert len(res["immediate_actions"]) > 0
    assert res["dose_lock"]["is_available"] is True
    assert "Mancozeb" in res["dose_lock"]["active_ingredient"]
    assert len(res["evidence_trace"]) >= 5

def test_invalid_image_upload(client):
    fake_txt_bytes = b"This is not a real image file content."
    files = {"file": ("malicious.txt", fake_txt_bytes, "text/plain")}
    data = {"crop": "tomato"}

    response = client.post("/api/diagnosis/predict", files=files, data=data)
    assert response.status_code == 400
    assert "Invalid file format" in response.json()["detail"]

def test_dose_lock_statutory_protection(client):
    # 1. Allowed registered pesticide
    resp1 = client.get("/api/treatments/tomato/early_blight")
    assert resp1.status_code == 200
    d1 = resp1.json()
    assert d1["is_available"] is True
    assert "2.0 g/L" in d1["dosage_per_liter"]
    assert d1["regulatory_status"] == "CIB&RC Registered"

    # 2. Blocked / Unverified case (Banana bacterial wilt has no registered foliar cure)
    resp2 = client.get("/api/treatments/banana/bacterial_wilt")
    assert resp2.status_code == 200
    d2 = resp2.json()
    assert d2["is_available"] is False
    assert "Consult an agricultural extension officer" in d2["status_text"]

def test_expert_escalation_flow(client):
    payload = {
        "crop": "Tomato",
        "district": "Coimbatore",
        "reason": "Farmer observed atypical concentric rings with chlorosis.",
        "farmer_phone": "+91 98765 43210"
    }
    response = client.post("/api/expert/escalation", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "DOS-COI-" in data["dossier_id"]
    assert data["status"] == "DISPATCH_READY"
    assert "ICAR-KVK" in data["kvk_center"]["name"]
    assert "1800-180-1551" in data["helpline"]

def test_diagnosis_history(client):
    response = client.get("/api/history")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    recent = data[0]
    assert "crop" in recent
    assert "disease_name" in recent
    assert "confidence" in recent
