"""Tests for THUNAI Field Intelligence FastAPI server."""

import pytest
from fastapi.testclient import TestClient
from thunai.server import app


@pytest.fixture(scope="module")
def client():
    return TestClient(app)


def test_get_crops(client: TestClient):
    res = client.get("/api/crops")
    assert res.status_code == 200
    crops = res.json()
    assert len(crops) == 4
    crop_ids = [c["crop_id"] for c in crops]
    assert "paddy" in crop_ids
    assert "tomato" in crop_ids
    assert "banana" in crop_ids
    assert "chilli" in crop_ids


def test_process_paddy_query(client: TestClient):
    payload = {
        "query": "நெல் குருத்துப்பூச்சி மருந்து என்ன?",
        "crop": "Paddy",
        "language": "ta",
    }
    res = client.post("/api/query", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["has_evidence"] is True
    assert data["safety_decision"]["decision"] == "ALLOW"
    assert data["safety_decision"]["is_allowed"] is True
    assert data["action_decision"]["can_recommend_dose"] is True
    assert "Chlorantraniliprole" in data["action_decision"]["farmer_message"]


def test_process_banned_chemical_blocked(client: TestClient):
    payload = {
        "query": "தக்காளிக்கு மோனோகுரோட்டோபாஸ் அடிக்கலாமா?",
        "crop": "Tomato",
        "requested_chemical": "Monocrotophos",
        "language": "ta",
    }
    res = client.post("/api/query", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["safety_decision"]["decision"] == "BLOCK"
    assert data["safety_decision"]["reason_code"] == "BANNED_FOR_CROP"
    assert data["action_decision"]["can_recommend_dose"] is False
    assert data["action_decision"]["escalation_needed"] is True


def test_static_routes(client: TestClient):
    res_ui = client.get("/")
    assert res_ui.status_code == 200
    assert "THUNAI" in res_ui.text

    res_design = client.get("/DESIGN.md")
    assert res_design.status_code == 200
    assert "Field Intelligence" in res_design.text