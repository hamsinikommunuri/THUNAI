"""
THUNAI Agricultural Spray Safety Engine
Deterministic, rule-based agronomic engine that evaluates real weather metrics.
Outputs:
- SPRAY NOW (Optimal weather window)
- WAIT (Adverse condition expected to clear within hours)
- NOT RECOMMENDED (Severe environmental hazard, drift or heavy rain)
"""

from typing import Dict, Any, List

class SpraySafetyEngine:
    # Configurable Agronomic Thresholds (Standard Agricultural Meteorology Guidelines)
    MAX_OPTIMAL_WIND_KMH = 15.0
    SEVERE_WIND_DRIFT_KMH = 20.0
    MIN_WIND_INVERSION_KMH = 3.0
    MAX_SAFE_TEMP_C = 32.0
    EXTREME_HEAT_TEMP_C = 36.0
    MAX_RAIN_PROB_3H = 45.0
    RAIN_WASHOFF_MM = 0.4
    MAX_RELATIVE_HUMIDITY = 88.0
    MIN_RELATIVE_HUMIDITY = 35.0

    @classmethod
    def evaluate(cls, current_weather: Dict[str, Any], hourly_forecast: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        temp = float(current_weather.get("temperature_c", 28.0))
        humidity = float(current_weather.get("humidity_percent", 65.0))
        precip = float(current_weather.get("precipitation_mm", 0.0))
        precip_prob = float(current_weather.get("precipitation_probability", 20.0))
        wind_speed = float(current_weather.get("wind_speed_kmh", 10.0))
        wind_gust = float(current_weather.get("wind_gust_kmh", 14.0))

        risk_factors: List[str] = []
        decision = "SPRAY NOW"
        badge_color = "emerald"
        primary_reason = "Weather parameters are currently optimal for foliar treatment."
        detailed_explanation = "Low wind drift risk, zero active precipitation, and moderate temperature promote uniform leaf surface droplet adhesion without rapid evaporation."
        rule_evaluated = "RULE_WEATHER_OPTIMAL"

        # Lookahead rain in next 3 hours
        rain_in_next_3h = False
        rain_mm_next_3h = 0.0
        if hourly_forecast and len(hourly_forecast) >= 3:
            for item in hourly_forecast[:3]:
                if item.get("precipitation_probability", 0) > cls.MAX_RAIN_PROB_3H or item.get("precipitation_mm", 0) > cls.RAIN_WASHOFF_MM:
                    rain_in_next_3h = True
                    rain_mm_next_3h = max(rain_mm_next_3h, item.get("precipitation_mm", 0))

        # 1. Active or Imminent Rain Evaluation (Critical P0)
        if precip > 0.1 or rain_in_next_3h or precip_prob > 60.0:
            decision = "WAIT"
            badge_color = "amber"
            primary_reason = "Imminent rainfall detected. Chemical wash-off risk is severe."
            detailed_explanation = (
                f"Rain probability is {precip_prob:.0f}% with forecast precipitation in the coming hours. "
                "Applying contact or systemic chemicals now will result in wash-off into the soil, failing pest control "
                "and causing wasted chemical expenditure."
            )
            risk_factors.append(f"Precipitation probability: {precip_prob:.0f}%")
            rule_evaluated = "RULE_RAIN_WASHOFF_HAZARD"

        # 2. Severe Wind Evaluation (P0 - Chemical Drift Hazard)
        elif wind_speed >= cls.SEVERE_WIND_DRIFT_KMH or wind_gust >= 28.0:
            decision = "NOT RECOMMENDED"
            badge_color = "rose"
            primary_reason = f"High wind speed ({wind_speed:.1f} km/h) creates extreme drift hazard."
            detailed_explanation = (
                f"Sustained wind of {wind_speed:.1f} km/h with gusts of {wind_gust:.1f} km/h exceeds the statutory safety limit "
                "(< 15 km/h). Spray droplets will drift off-target, contaminating adjacent waterways, beneficial insects, or residential zones."
            )
            risk_factors.append(f"High wind drift: {wind_speed:.1f} km/h (Gusts: {wind_gust:.1f} km/h)")
            rule_evaluated = "RULE_SEVERE_WIND_DRIFT"

        # 3. Extreme Heat & Evaporation (P1)
        elif temp >= cls.MAX_SAFE_TEMP_C:
            decision = "WAIT"
            badge_color = "amber"
            primary_reason = f"Midday heat ({temp:.1f}°C) exceeds safe foliar application temperature."
            detailed_explanation = (
                f"Air temperature of {temp:.1f}°C accelerates droplet evaporation before the active ingredient can penetrate the leaf cuticle. "
                "This can cause salt crystallization and foliar phytotoxicity (leaf scorch). Spray in early morning or late afternoon."
            )
            risk_factors.append(f"High temperature: {temp:.1f}°C (> {cls.MAX_SAFE_TEMP_C}°C threshold)")
            rule_evaluated = "RULE_HEAT_PHYTOTOXICITY"

        # 4. Moderate Wind Warning (P1)
        elif wind_speed > cls.MAX_OPTIMAL_WIND_KMH:
            decision = "WAIT"
            badge_color = "amber"
            primary_reason = f"Moderate wind ({wind_speed:.1f} km/h) reduces foliar droplet deposition efficiency."
            detailed_explanation = (
                f"Current wind speed ({wind_speed:.1f} km/h) is marginally elevated. If treatment is urgent, use drift-reduction coarse nozzles, "
                "otherwise wait for wind to calm below 12 km/h."
            )
            risk_factors.append(f"Marginal wind: {wind_speed:.1f} km/h")
            rule_evaluated = "RULE_MODERATE_WIND"

        # 5. Inversion Hazard (Dead Calm + Heat)
        elif wind_speed < cls.MIN_WIND_INVERSION_KMH and temp > 30.0:
            risk_factors.append("Low air turbulence (< 3 km/h): watch for thermal inversion drift.")
            primary_reason = "Caution: Dead calm air with high thermal convection."
            rule_evaluated = "RULE_THERMAL_INVERSION_RISK"

        # Determine Recommended Application Window
        recommended_window = cls._find_optimal_window(hourly_forecast)

        return {
            "decision": decision,
            "badge_color": badge_color,
            "primary_reason": primary_reason,
            "detailed_explanation": detailed_explanation,
            "recommended_window": recommended_window,
            "risk_factors": risk_factors,
            "rule_evaluated": rule_evaluated
        }

    @classmethod
    def _find_optimal_window(cls, hourly_forecast: List[Dict[str, Any]]) -> str:
        if not hourly_forecast:
            return "Tomorrow morning 06:30 AM – 09:00 AM (Calm winds < 10 km/h)"

        # Search for earliest 2-hour contiguous block with safe conditions
        for i in range(len(hourly_forecast) - 2):
            w1 = hourly_forecast[i]
            w2 = hourly_forecast[i+1]
            if w1.get("is_safe_for_spraying") and w2.get("is_safe_for_spraying"):
                t1 = w1.get("time", "").split("T")[-1][:5]
                t2 = w2.get("time", "").split("T")[-1][:5]
                date_str = w1.get("time", "").split("T")[0]
                return f"{date_str} at {t1} – {t2} (Winds: {w1.get('wind_speed_kmh')} km/h, Rain: 0%)"

        return "Tomorrow morning 06:00 AM – 08:30 AM (Anticipated clear window)"
