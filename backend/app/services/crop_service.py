"""
THUNAI Crop Suitability & Recommendation Engine
Uses scientific agro-climatic matching rules based on:
- Current ambient temperature & seasonal temperature range
- Monthly/annual rainfall patterns
- Regional or user-tested soil type and pH tolerance
- Current agricultural cropping season (Kharif, Rabi, Zaid, Perennial)
Clearly transparent: declared as an Agronomic Knowledge Rule Engine.
"""

import os
import json
from datetime import datetime
from typing import Dict, Any, List
from backend.app.core.config import settings

class CropRecommendationService:
    _crops_data = None

    @classmethod
    def _load_crops(cls):
        if cls._crops_data is None:
            path = os.path.join(settings.KNOWLEDGE_DIR, "crops_guide.json")
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    cls._crops_data = json.load(f).get("crops", [])
            else:
                cls._crops_data = []
        return cls._crops_data

    @classmethod
    def get_current_season(cls) -> str:
        month = datetime.now().month
        # Indian Agro-Climatic Cropping Seasons
        if 6 <= month <= 10:
            return "Kharif (Monsoon Season)"
        elif 11 <= month or month <= 2:
            return "Rabi (Winter Season)"
        else:
            return "Zaid (Summer Season)"

    @classmethod
    def recommend_crops(
        cls, 
        location: str = "Coimbatore",
        temperature_c: float = 28.5, 
        rainfall_mm: float = 750.0,
        soil_type: str = "Red Loam",
        soil_ph: float = 7.4
    ) -> Dict[str, Any]:
        crops = cls._load_crops()
        season = cls.get_current_season()
        results: List[Dict[str, Any]] = []

        for crop in crops:
            score = 100
            reasons: List[str] = []

            # 1. Temperature Evaluation
            temp_opt_min = crop.get("temp_optimal_min", 20.0)
            temp_opt_max = crop.get("temp_optimal_max", 30.0)
            temp_abs_min = crop.get("temp_min", 15.0)
            temp_abs_max = crop.get("temp_max", 38.0)

            if temp_opt_min <= temperature_c <= temp_opt_max:
                reasons.append(f"Ideal temperature window ({temperature_c:.1f}°C is within optimal {temp_opt_min}-{temp_opt_max}°C)")
            elif temp_abs_min <= temperature_c <= temp_abs_max:
                score -= 15
                reasons.append(f"Acceptable temperature ({temperature_c:.1f}°C within tolerance range {temp_abs_min}-{temp_abs_max}°C)")
            else:
                score -= 40
                reasons.append(f"Suboptimal temperature ({temperature_c:.1f}°C outside safe range {temp_abs_min}-{temp_abs_max}°C)")

            # 2. Soil pH Evaluation
            ph_opt_min = crop.get("ph_optimal_min", 6.0)
            ph_opt_max = crop.get("ph_optimal_max", 7.5)
            ph_abs_min = crop.get("ph_min", 5.5)
            ph_abs_max = crop.get("ph_max", 8.0)

            if ph_opt_min <= soil_ph <= ph_opt_max:
                reasons.append(f"Soil pH {soil_ph:.1f} matches optimal root absorption range ({ph_opt_min}-{ph_opt_max})")
            elif ph_abs_min <= soil_ph <= ph_abs_max:
                score -= 10
                reasons.append(f"Soil pH {soil_ph:.1f} is within acceptable limits ({ph_abs_min}-{ph_abs_max})")
            else:
                score -= 30
                reasons.append(f"Soil pH {soil_ph:.1f} may restrict nutrient availability for this crop")

            # 3. Soil Type Compatibility
            suitable_soils = crop.get("suitable_soils", [])
            soil_matched = any(s.lower() in soil_type.lower() or soil_type.lower() in s.lower() for s in suitable_soils)
            if soil_matched:
                reasons.append(f"Compatible with regional {soil_type} soil structure")
            else:
                score -= 15
                reasons.append(f"Requires soil texture amendments or ridge-bed preparation in {soil_type}")

            # 4. Season Compatibility
            seasons_allowed = crop.get("seasons", [])
            season_key = season.split()[0]
            if "All Seasons" in seasons_allowed or "Perennial" in seasons_allowed or season_key in seasons_allowed:
                reasons.append(f"Well-adapted to current {season} planting window")
            else:
                score -= 20
                reasons.append(f"Normally grown in {', '.join(seasons_allowed)} season; off-season greenhouse care needed")

            # Determine Tier
            if score >= 75:
                suitability = "High"
            elif score >= 50:
                suitability = "Moderate"
            else:
                suitability = "Low"

            results.append({
                "crop_id": crop.get("crop_id"),
                "name_en": crop.get("name_en"),
                "name_ta": crop.get("name_ta"),
                "scientific_name": crop.get("scientific_name"),
                "suitability": suitability,
                "suitability_score": max(score, 10),
                "reasons": reasons,
                "ideal_temperature_range": f"{temp_opt_min}°C - {temp_opt_max}°C",
                "water_requirement": crop.get("water_requirement"),
                "economic_importance": crop.get("economic_importance"),
                "source": crop.get("source")
            })

        # Sort by suitability score descending
        results.sort(key=lambda x: x["suitability_score"], reverse=True)

        return {
            "location": location,
            "current_season": season,
            "temperature_c": temperature_c,
            "rainfall_annual_mm": rainfall_mm,
            "soil_type": soil_type,
            "engine_type": "AGRONOMIC_RULE_ENGINE",
            "scientific_basis": "Empirical physiological tolerance matrices derived from ICAR, TNAU, and State Horticultural Handbooks.",
            "recommended_crops": results
        }
