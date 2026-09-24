"""
THUNAI Soil Intelligence Service
Provides regional agro-pedological estimates and accepts user lab measurements.
Prioritizes user soil tests over regional estimates and clearly labels data provenance.
"""

import os
import json
from typing import Dict, Any, Optional
from backend.app.core.config import settings

class SoilService:
    _soils_data = None

    @classmethod
    def _load_data(cls):
        if cls._soils_data is None:
            path = os.path.join(settings.KNOWLEDGE_DIR, "soils.json")
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    cls._soils_data = json.load(f)
            else:
                cls._soils_data = {"regional_profiles": {}, "default_fallback": {}}
        return cls._soils_data

    @classmethod
    def get_soil_profile(
        cls, 
        district: str = "Coimbatore", 
        user_measurement: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        data = cls._load_data()
        district_key = district.strip().lower()

        profiles = data.get("regional_profiles", {})
        regional_profile = profiles.get(district_key)

        if not regional_profile:
            # Fuzzy match or fallback
            for k, v in profiles.items():
                if k in district_key or district_key in k:
                    regional_profile = v
                    break

        if not regional_profile:
            regional_profile = data.get("default_fallback", {})

        # If farmer entered real lab measurements, prioritize them
        if user_measurement and any(user_measurement.values()):
            user_ph = user_measurement.get("ph")
            user_n = user_measurement.get("nitrogen_kg_ha")
            user_p = user_measurement.get("phosphorus_kg_ha")
            user_k = user_measurement.get("potassium_kg_ha")
            user_oc = user_measurement.get("organic_carbon_percent")
            user_type = user_measurement.get("soil_type")

            # Determine pH category
            ph_cat = "Near Neutral (Optimal)"
            if user_ph:
                if user_ph < 6.0:
                    ph_cat = "Acidic (Lime treatment recommended)"
                elif user_ph > 8.0:
                    ph_cat = "Alkaline / Calcareous (Gypsum or sulfur recommended)"

            return {
                "data_type": "USER_MEASUREMENT",
                "warning_notice": "Verified User Soil Test. Recommendations are tailored directly to your lab measurements.",
                "district": district,
                "state": regional_profile.get("state", "India"),
                "dominant_soil_type": user_type or regional_profile.get("dominant_soil_type"),
                "ph_range": str(user_ph) if user_ph else regional_profile.get("ph_range"),
                "ph_category": ph_cat,
                "organic_carbon": f"{user_oc:.2f}%" if user_oc else regional_profile.get("organic_carbon_percent"),
                "nitrogen_condition": f"{user_n:.1f} kg/ha" if user_n else regional_profile.get("available_nitrogen"),
                "phosphorus_condition": f"{user_p:.1f} kg/ha" if user_p else regional_profile.get("available_phosphorus"),
                "potassium_condition": f"{user_k:.1f} kg/ha" if user_k else regional_profile.get("available_potassium"),
                "texture": regional_profile.get("texture", "Clay Loam"),
                "drainage": regional_profile.get("drainage", "Moderately well-drained"),
                "regional_characteristics": f"Custom Farmer Plot Test ({district})",
                "management_advice": "Apply tailored N-P-K based strictly on your Soil Health Card targets to optimize yield and prevent fertilizer excess.",
                "source": "Farmer Direct Lab Soil Health Card Entry",
                "source_url": "https://soilhealth.dac.gov.in"
            }

        # Otherwise return regional estimate with explicit warning notice
        return {
            "data_type": "REGIONAL_ESTIMATE",
            "warning_notice": "Regional soil estimate based on ICAR-NBSS&LUP district survey. For exact parcel nutrient recommendations, get a laboratory soil test.",
            "district": regional_profile.get("district", district),
            "state": regional_profile.get("state", "India"),
            "dominant_soil_type": regional_profile.get("dominant_soil_type"),
            "ph_range": regional_profile.get("ph_range"),
            "ph_category": regional_profile.get("ph_category"),
            "organic_carbon": regional_profile.get("organic_carbon_percent"),
            "nitrogen_condition": regional_profile.get("available_nitrogen"),
            "phosphorus_condition": regional_profile.get("available_phosphorus"),
            "potassium_condition": regional_profile.get("available_potassium"),
            "texture": regional_profile.get("texture"),
            "drainage": regional_profile.get("drainage"),
            "regional_characteristics": regional_profile.get("calcium_carbonate_content", "Standard regional horizon"),
            "management_advice": regional_profile.get("recommendations"),
            "source": regional_profile.get("source"),
            "source_url": regional_profile.get("source_url")
        }
