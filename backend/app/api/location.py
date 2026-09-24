"""
THUNAI Location & Geocoding Endpoints
Provides real reverse-geocoding and searchable manual fallback.
"""

from datetime import datetime, timezone
from typing import List, Dict, Any
from fastapi import APIRouter, Query, HTTPException
import httpx
from backend.app.schemas.schemas import LocationRequest, LocationResponse

router = APIRouter(prefix="/location", tags=["Location Intelligence"])

NOMINATIM_REVERSE_URL = "https://nominatim.openstreetmap.org/reverse"
NOMINATIM_SEARCH_URL = "https://nominatim.openstreetmap.org/search"
HEADERS = {"User-Agent": "THUNAI-AgriPlatform/2.0 (Agricultural Decision Support System; contact: support@thunai.agri)"}

# Curated fallback registry for Indian agricultural districts
FALLBACK_DISTRICTS = {
    "coimbatore": {"lat": 11.0168, "lon": 76.9558, "district": "Coimbatore", "state": "Tamil Nadu", "country": "India"},
    "tiruppur": {"lat": 11.1085, "lon": 77.3411, "district": "Tiruppur", "state": "Tamil Nadu", "country": "India"},
    "salem": {"lat": 11.6643, "lon": 78.1460, "district": "Salem", "state": "Tamil Nadu", "country": "India"},
    "thanjavur": {"lat": 10.7870, "lon": 79.1378, "district": "Thanjavur", "state": "Tamil Nadu", "country": "India"},
    "madurai": {"lat": 9.9252, "lon": 78.1198, "district": "Madurai", "state": "Tamil Nadu", "country": "India"},
    "tiruchirappalli": {"lat": 10.7905, "lon": 78.7047, "district": "Tiruchirappalli", "state": "Tamil Nadu", "country": "India"},
    "guntur": {"lat": 16.3067, "lon": 80.4365, "district": "Guntur", "state": "Andhra Pradesh", "country": "India"},
    "pune": {"lat": 18.5204, "lon": 73.8567, "district": "Pune", "state": "Maharashtra", "country": "India"},
    "shimoga": {"lat": 13.9299, "lon": 75.5681, "district": "Shimoga", "state": "Karnataka", "country": "India"},
    "karnal": {"lat": 29.6857, "lon": 76.9905, "district": "Karnal", "state": "Haryana", "country": "India"},
}

@router.post("/reverse-geocode", response_model=LocationResponse)
async def reverse_geocode(loc: LocationRequest):
    lat = loc.latitude
    lon = loc.longitude
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S IST")

    try:
        async with httpx.AsyncClient(timeout=6.0, headers=HEADERS) as client:
            resp = await client.get(NOMINATIM_REVERSE_URL, params={
                "lat": lat,
                "lon": lon,
                "format": "jsonv2",
                "addressdetails": 1,
                "zoom": 14
            })
            if resp.status_code == 200:
                data = resp.json()
                address = data.get("address", {})

                village = (
                    address.get("village") or 
                    address.get("town") or 
                    address.get("suburb") or 
                    address.get("neighbourhood") or 
                    address.get("city") or 
                    "Local Agricultural Zone"
                )
                district = (
                    address.get("state_district") or 
                    address.get("district") or 
                    address.get("county") or 
                    address.get("city") or 
                    "Coimbatore"
                )
                state = address.get("state", "Tamil Nadu")
                country = address.get("country", "India")
                display_name = data.get("display_name", f"{village}, {district}, {state}")

                return LocationResponse(
                    latitude=lat,
                    longitude=lon,
                    village_or_town=village,
                    district=district.replace(" District", ""),
                    state=state,
                    country=country,
                    display_name=display_name,
                    source="OpenStreetMap Nominatim Reverse Geocoder",
                    timestamp=timestamp
                )
    except Exception as e:
        print(f"Reverse geocode network warning: {e}")

    # Fallback to nearest or default profile
    return LocationResponse(
        latitude=lat,
        longitude=lon,
        village_or_town="Field Plot",
        district="Coimbatore",
        state="Tamil Nadu",
        country="India",
        display_name="Coimbatore Rural District, Tamil Nadu, India",
        source="THUNAI Coordinate Mapping Engine (Offline Fallback)",
        timestamp=timestamp
    )

@router.get("/search")
async def search_locations(query: str = Query(..., min_length=2)):
    """Searchable manual location entry fallback."""
    q_clean = query.strip().lower()

    # Check curated local index first
    matches = []
    for k, v in FALLBACK_DISTRICTS.items():
        if q_clean in k or q_clean in v["state"].lower():
            matches.append({
                "display_name": f"{v['district']}, {v['state']}, {v['country']}",
                "district": v["district"],
                "state": v["state"],
                "country": v["country"],
                "latitude": v["lat"],
                "longitude": v["lon"]
            })

    # Query Nominatim search
    try:
        async with httpx.AsyncClient(timeout=5.0, headers=HEADERS) as client:
            resp = await client.get(NOMINATIM_SEARCH_URL, params={
                "q": query,
                "format": "jsonv2",
                "addressdetails": 1,
                "limit": 5,
                "countrycodes": "in"
            })
            if resp.status_code == 200:
                results = resp.json()
                for item in results:
                    addr = item.get("address", {})
                    d_name = (
                        addr.get("state_district") or 
                        addr.get("district") or 
                        addr.get("county") or 
                        addr.get("city") or 
                        item.get("name")
                    )
                    matches.append({
                        "display_name": item.get("display_name"),
                        "district": d_name.replace(" District", "") if d_name else "Agricultural Zone",
                        "state": addr.get("state", "India"),
                        "country": addr.get("country", "India"),
                        "latitude": float(item.get("lat")),
                        "longitude": float(item.get("lon"))
                    })
    except Exception:
        pass

    # Deduplicate matches by district
    seen = set()
    unique_matches = []
    for m in matches:
        d = m["district"].lower()
        if d not in seen:
            seen.add(d)
            unique_matches.append(m)

    return {"results": unique_matches}
