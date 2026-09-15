"""Unit tests for the Dose Lock Engine."""

import pytest
from thunai.core.enums import (
    DecisionType,
    EvidenceStatus,
    ReasonCategory,
    ReasonCode,
    RecommendationType,
    SourceTier,
)
from thunai.core.models import EvidenceRecord, FarmerContext
from thunai.safety.dose_lock import DoseLockEngine


class TestDoseLockEngine:
    def test_locked_by_default_without_evidence(self, engine: DoseLockEngine):
        ctx = FarmerContext(crop="Tomato", target_problem="Fruit Borer")
        decision = engine.evaluate(ctx, evidence=None)
        assert decision.is_blocked
        assert decision.decision == DecisionType.BLOCK
        assert decision.reason_code == ReasonCode.MISSING_EVIDENCE
        assert decision.reason_category == ReasonCategory.UNCERTAINTY
        assert decision.allowed_dose is None

    def test_unlocked_when_all_conditions_satisfied(
        self, engine: DoseLockEngine, verified_tomato_fruit_borer: EvidenceRecord
    ):
        ctx = FarmerContext(crop="Tomato", target_problem="Fruit Borer")
        decision = engine.evaluate(ctx, evidence=verified_tomato_fruit_borer)
        assert decision.is_allowed
        assert decision.decision == DecisionType.ALLOW
        assert decision.reason_code == ReasonCode.VERIFIED_AND_ALLOWED
        assert decision.reason_category == ReasonCategory.VALID_VERIFIED
        assert decision.allowed_dose is not None
        assert decision.allowed_dose.dose_amount == 0.3
        assert decision.allowed_dose.dose_unit == "ml/l"
        assert decision.allowed_dose.active_ingredient == "Chlorantraniliprole"
        assert "DOSE_UNLOCKED" in decision.trace

    def test_locked_when_crop_mismatch(
        self, engine: DoseLockEngine, verified_banana_sigatoka: EvidenceRecord
    ):
        ctx = FarmerContext(crop="Tomato", target_problem="Early Blight")
        decision = engine.evaluate(ctx, evidence=verified_banana_sigatoka)
        assert decision.is_blocked
        assert decision.reason_code in (ReasonCode.CROSS_CROP_LEAKAGE, ReasonCode.CROP_MISMATCH)
        assert decision.reason_category == ReasonCategory.EVIDENCE_MISMATCH
        assert decision.allowed_dose is None
        assert "banana" in decision.human_reason.lower()

    def test_locked_when_problem_mismatch(
        self, engine: DoseLockEngine, verified_tomato_fruit_borer: EvidenceRecord
    ):
        ctx = FarmerContext(crop="Tomato", target_problem="Early Blight")
        decision = engine.evaluate(ctx, evidence=verified_tomato_fruit_borer)
        assert decision.is_blocked
        assert decision.reason_code == ReasonCode.PROBLEM_MISMATCH
        assert decision.reason_category == ReasonCategory.EVIDENCE_MISMATCH
        assert decision.allowed_dose is None

    def test_locked_when_missing_explicit_dose(
        self, engine: DoseLockEngine, verified_tomato_fruit_borer: EvidenceRecord
    ):
        # Create record with dose=None
        rec_dict = verified_tomato_fruit_borer.model_dump()
        rec_dict["dose"] = None
        record_no_dose = EvidenceRecord(**rec_dict)

        ctx = FarmerContext(crop="Tomato", target_problem="Fruit Borer")
        decision = engine.evaluate(ctx, evidence=record_no_dose)
        assert decision.is_blocked
        assert decision.reason_code == ReasonCode.MISSING_EXPLICIT_DOSE
        assert decision.allowed_dose is None

    def test_locked_when_dose_is_zero_or_negative(
        self, engine: DoseLockEngine, verified_tomato_fruit_borer: EvidenceRecord
    ):
        rec_dict = verified_tomato_fruit_borer.model_dump()
        rec_dict["dose"] = 0.0
        rec_zero = EvidenceRecord(**rec_dict)

        ctx = FarmerContext(crop="Tomato", target_problem="Fruit Borer")
        decision = engine.evaluate(ctx, evidence=rec_zero)
        assert decision.is_blocked
        assert decision.reason_code == ReasonCode.INVALID_DOSE_VALUE
        assert decision.allowed_dose is None

    def test_locked_when_source_is_unverified(
        self, engine: DoseLockEngine, verified_tomato_fruit_borer: EvidenceRecord
    ):
        rec_dict = verified_tomato_fruit_borer.model_dump()
        rec_dict["source_tier"] = SourceTier.UNVERIFIED
        rec_dict["source"] = "Random Gardening Blog"
        rec_unverified = EvidenceRecord(**rec_dict)

        ctx = FarmerContext(crop="Tomato", target_problem="Fruit Borer")
        decision = engine.evaluate(ctx, evidence=rec_unverified)
        assert decision.is_blocked
        assert decision.reason_code == ReasonCode.UNVERIFIED_SOURCE
        assert decision.allowed_dose is None

    def test_locked_when_status_is_provisional(
        self, engine: DoseLockEngine, verified_tomato_fruit_borer: EvidenceRecord
    ):
        rec_dict = verified_tomato_fruit_borer.model_dump()
        rec_dict["evidence_status"] = EvidenceStatus.PROVISIONAL
        rec_prov = EvidenceRecord(**rec_dict)

        ctx = FarmerContext(crop="Tomato", target_problem="Fruit Borer")
        decision = engine.evaluate(ctx, evidence=rec_prov)
        assert decision.is_blocked
        assert decision.reason_code == ReasonCode.UNVERIFIED_STATUS
        assert decision.allowed_dose is None

    def test_rain_gated_weather(
        self, engine: DoseLockEngine, verified_tomato_fruit_borer: EvidenceRecord
    ):
        ctx = FarmerContext(
            crop="Tomato",
            target_problem="Fruit Borer",
            weather_condition={"rain_forecast_hours": 2, "rainfall_mm": 12.0},
        )
        decision = engine.evaluate(ctx, evidence=verified_tomato_fruit_borer)
        assert decision.is_blocked
        assert decision.reason_code == ReasonCode.RAIN_GATED
        assert decision.reason_category == ReasonCategory.WEATHER_GATE
        assert decision.allowed_dose is None

    def test_wind_gated_weather(
        self, engine: DoseLockEngine, verified_tomato_fruit_borer: EvidenceRecord
    ):
        ctx = FarmerContext(
            crop="Tomato",
            target_problem="Fruit Borer",
            weather_condition={"wind_speed_kmh": 22.0},
        )
        decision = engine.evaluate(ctx, evidence=verified_tomato_fruit_borer)
        assert decision.is_blocked
        assert decision.reason_code == ReasonCode.WIND_GATED
        assert decision.reason_category == ReasonCategory.WEATHER_GATE
        assert decision.allowed_dose is None

    def test_high_temp_gated_weather(
        self, engine: DoseLockEngine, verified_tomato_fruit_borer: EvidenceRecord
    ):
        ctx = FarmerContext(
            crop="Tomato",
            target_problem="Fruit Borer",
            weather_condition={"temperature_c": 41.0},
        )
        decision = engine.evaluate(ctx, evidence=verified_tomato_fruit_borer)
        assert decision.is_blocked
        assert decision.reason_code == ReasonCode.TEMPERATURE_GATED
        assert decision.reason_category == ReasonCategory.WEATHER_GATE
        assert decision.allowed_dose is None

    def test_unrecognized_problem_blocks_dose_with_candidate_evidence(
        self, engine: DoseLockEngine, verified_tomato_fruit_borer: EvidenceRecord
    ):
        # Farmer specifies root rot (unrecognized/unregistered tomato problem)
        ctx = FarmerContext(
            crop="Tomato",
            target_problem="root rot",
            raw_query="I have tomato plants suffering from severe root rot",
        )
        decision = engine.evaluate(ctx, evidence=verified_tomato_fruit_borer)
        assert decision.is_blocked
        assert decision.reason_code == ReasonCode.PROBLEM_MISMATCH
        assert decision.reason_category == ReasonCategory.EVIDENCE_MISMATCH
        assert decision.allowed_dose is None

    def test_ferterra_requested_chemical_unlocks_paddy_stem_borer(
        self, engine: DoseLockEngine, verified_paddy_stem_borer: EvidenceRecord
    ):
        ctx = FarmerContext(
            crop="Paddy",
            target_problem="Yellow Stem Borer",
            requested_chemical="Ferterra",
        )
        decision = engine.evaluate(ctx, evidence=verified_paddy_stem_borer)
        assert decision.is_allowed
        assert decision.reason_code == ReasonCode.VERIFIED_AND_ALLOWED
        assert decision.allowed_dose is not None
        assert decision.allowed_dose.formatted_dose == "4.0 kg/acre"

    def test_durmet_requested_chemical_unlocks_banana_pseudostem_borer(
        self, engine: DoseLockEngine, verified_banana_pseudostem_borer: EvidenceRecord
    ):
        ctx = FarmerContext(
            crop="Banana",
            target_problem="Pseudostem Borer",
            requested_chemical="Durmet",
        )
        decision = engine.evaluate(ctx, evidence=verified_banana_pseudostem_borer)
        assert decision.is_allowed
        assert decision.reason_code == ReasonCode.VERIFIED_AND_ALLOWED
        assert decision.allowed_dose is not None
        assert decision.allowed_dose.formatted_dose == "2.5 ml/l"

    def test_phi_violation_in_dose_lock_engine(
        self, engine: DoseLockEngine, verified_tomato_fruit_borer: EvidenceRecord
    ):
        rec_data = verified_tomato_fruit_borer.model_dump()
        rec_data["waiting_period_days"] = 7
        rec_with_phi = EvidenceRecord(**rec_data)

        ctx = FarmerContext(
            crop="Tomato",
            target_problem="Fruit Borer",
            days_to_harvest=2,
        )
        decision = engine.evaluate(ctx, evidence=rec_with_phi)
        assert decision.is_blocked
        assert decision.reason_code == ReasonCode.PRE_HARVEST_INTERVAL_VIOLATION
        assert decision.reason_category == ReasonCategory.PRODUCT_SAFETY_POLICY
        assert decision.allowed_dose is None

    def test_crop_mismatch_single_evidence_returns_crop_mismatch(
        self, engine: DoseLockEngine, verified_banana_sigatoka: EvidenceRecord
    ):
        ctx = FarmerContext(crop="Tomato", target_problem="Early Blight")
        decision = engine.evaluate(ctx, evidence=verified_banana_sigatoka)
        assert decision.is_blocked
        assert decision.reason_code == ReasonCode.CROP_MISMATCH
        assert decision.reason_category == ReasonCategory.EVIDENCE_MISMATCH
        assert "banana" in decision.human_reason.lower()
        assert "tomato" in decision.human_reason.lower()

    def test_biological_without_explicit_dose_is_blocked(self, engine: DoseLockEngine):
        bio_rec = EvidenceRecord(
            evidence_id="EV-BAN-BIO-001",
            crop="Banana",
            crop_id="banana",
            problem="Panama Wilt",
            problem_id="banana_panama_wilt",
            recommendation_type=RecommendationType.BIOLOGICAL,
            active_ingredient="Pseudomonas fluorescens",
            application_basis="soil application / drenching",
            dose=None,
            dose_unit=None,
            source="TNAU Package of Practices",
            source_tier=SourceTier.TRUSTED_GOV_ACADEMIC,
            evidence_status=EvidenceStatus.VERIFIED,
        )
        ctx = FarmerContext(crop="Banana", target_problem="Panama Wilt")
        decision = engine.evaluate(ctx, evidence=bio_rec)
        assert decision.is_blocked
        assert decision.reason_code == ReasonCode.MISSING_EXPLICIT_DOSE
        assert decision.reason_category == ReasonCategory.UNCERTAINTY
        assert decision.allowed_dose is None

    def test_biological_with_negative_dose_is_blocked(self, engine: DoseLockEngine):
        bio_rec = EvidenceRecord(
            evidence_id="EV-BAN-BIO-002",
            crop="Banana",
            crop_id="banana",
            problem="Panama Wilt",
            problem_id="banana_panama_wilt",
            recommendation_type=RecommendationType.BIOLOGICAL,
            active_ingredient="Pseudomonas fluorescens",
            application_basis="soil application / drenching",
            dose=-5.0,
            dose_unit="g/l",
            source="TNAU Package of Practices",
            source_tier=SourceTier.TRUSTED_GOV_ACADEMIC,
            evidence_status=EvidenceStatus.VERIFIED,
        )
        ctx = FarmerContext(crop="Banana", target_problem="Panama Wilt")
        decision = engine.evaluate(ctx, evidence=bio_rec)
        assert decision.is_blocked
        assert decision.reason_code == ReasonCode.INVALID_DOSE_VALUE
        assert decision.allowed_dose is None

    def test_weather_condition_with_none_values_does_not_crash(
        self, engine: DoseLockEngine, verified_tomato_fruit_borer: EvidenceRecord
    ):
        ctx = FarmerContext(
            crop="Tomato",
            target_problem="Fruit Borer",
            weather_condition={
                "rain_forecast_hours": None,
                "rainfall_mm": None,
                "wind_speed_kmh": None,
                "temperature_c": None,
            },
        )
        decision = engine.evaluate(ctx, evidence=verified_tomato_fruit_borer)
        assert decision.is_allowed
        assert decision.reason_code == ReasonCode.VERIFIED_AND_ALLOWED

    def test_hazardous_tank_mix_blocked_in_engine(
        self, engine: DoseLockEngine, verified_banana_sigatoka: EvidenceRecord
    ):
        ctx = FarmerContext(
            crop="Banana",
            target_problem="Sigatoka Leaf Spot",
            requested_chemical="Blitox + Rogor",
        )
        decision = engine.evaluate(ctx, evidence=verified_banana_sigatoka)
        assert decision.is_blocked
        assert decision.reason_code == ReasonCode.HAZARDOUS_TANK_MIX
        assert decision.reason_category == ReasonCategory.PRODUCT_SAFETY_POLICY

