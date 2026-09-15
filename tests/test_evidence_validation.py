"""Unit tests for evidence validation and integrity checking."""

import pytest
from thunai.core.enums import EvidenceStatus, ReasonCode, RecommendationType, SourceTier
from thunai.core.models import EvidenceRecord
from thunai.safety.evidence_validation import (
    detect_conflicting_evidence,
    validate_dose_evidence,
    validate_evidence_record,
)


class TestEvidenceValidation:
    def test_valid_evidence_passes(self, verified_tomato_fruit_borer: EvidenceRecord):
        is_valid, reason, eng_msg, ta_msg = validate_evidence_record(verified_tomato_fruit_borer)
        assert is_valid is True
        assert reason is None
        assert "verified successfully" in eng_msg.lower()

    def test_none_evidence_fails(self):
        is_valid, reason, _, _ = validate_evidence_record(None)
        assert is_valid is False
        assert reason == ReasonCode.MISSING_EVIDENCE

    def test_unverified_source_tier_fails(self, verified_tomato_fruit_borer: EvidenceRecord):
        rec_data = verified_tomato_fruit_borer.model_dump()
        rec_data["source_tier"] = SourceTier.COMMERCIAL
        rec = EvidenceRecord(**rec_data)
        is_valid, reason, _, _ = validate_evidence_record(rec)
        assert is_valid is False
        assert reason == ReasonCode.UNVERIFIED_SOURCE

    def test_expired_or_provisional_status_fails(self, verified_tomato_fruit_borer: EvidenceRecord):
        rec_data = verified_tomato_fruit_borer.model_dump()
        rec_data["evidence_status"] = EvidenceStatus.EXPIRED
        rec = EvidenceRecord(**rec_data)
        is_valid, reason, _, _ = validate_evidence_record(rec)
        assert is_valid is False
        assert reason == ReasonCode.UNVERIFIED_STATUS

    def test_missing_active_ingredient_fails(self, verified_tomato_fruit_borer: EvidenceRecord):
        rec_data = verified_tomato_fruit_borer.model_dump()
        rec_data["active_ingredient"] = None
        rec = EvidenceRecord(**rec_data)
        is_valid, reason, _, _ = validate_evidence_record(rec)
        assert is_valid is False
        assert reason == ReasonCode.INCOMPLETE_METADATA

    def test_missing_formulation_fails(self, verified_tomato_fruit_borer: EvidenceRecord):
        rec_data = verified_tomato_fruit_borer.model_dump()
        rec_data["formulation"] = ""
        rec = EvidenceRecord(**rec_data)
        is_valid, reason, _, _ = validate_evidence_record(rec)
        assert is_valid is False
        assert reason == ReasonCode.INCOMPLETE_METADATA

    def test_missing_dose_fails(self, verified_tomato_fruit_borer: EvidenceRecord):
        rec_data = verified_tomato_fruit_borer.model_dump()
        rec_data["dose"] = None
        rec = EvidenceRecord(**rec_data)
        is_valid, reason, _, _ = validate_evidence_record(rec)
        assert is_valid is False
        assert reason == ReasonCode.MISSING_EXPLICIT_DOSE

    def test_negative_or_zero_dose_fails(self, verified_tomato_fruit_borer: EvidenceRecord):
        rec_data = verified_tomato_fruit_borer.model_dump()
        rec_data["dose"] = -2.0
        rec = EvidenceRecord(**rec_data)
        is_valid, reason, _, _ = validate_evidence_record(rec)
        assert is_valid is False
        assert reason == ReasonCode.INVALID_DOSE_VALUE

    def test_detect_conflicting_evidence(self, verified_tomato_early_blight: EvidenceRecord):
        # Candidate 1: dose 2.0 g/l
        cand1 = verified_tomato_early_blight
        # Candidate 2: dose 10.0 g/l (5x difference)
        cand2_data = cand1.model_dump()
        cand2_data["evidence_id"] = "EV-TOM-002B"
        cand2_data["dose"] = 10.0
        cand2 = EvidenceRecord(**cand2_data)

        has_conflict, msg, msg_ta = detect_conflicting_evidence([cand1, cand2])
        assert has_conflict is True
        assert "Conflicting dosage" in msg

    def test_biological_missing_dose_fails_validation(self):
        rec = EvidenceRecord(
            evidence_id="EV-BIO-001",
            crop="Banana",
            crop_id="banana",
            problem="Panama Wilt",
            problem_id="banana_panama_wilt",
            recommendation_type=RecommendationType.BIOLOGICAL,
            active_ingredient="Pseudomonas fluorescens",
            application_basis="root dipping",
            dose=None,
            dose_unit=None,
            source="TNAU Package of Practices",
            source_tier=SourceTier.TRUSTED_GOV_ACADEMIC,
            evidence_status=EvidenceStatus.VERIFIED,
        )
        is_valid, reason, _, _ = validate_evidence_record(rec)
        assert is_valid is False
        assert reason == ReasonCode.MISSING_EXPLICIT_DOSE

    def test_biological_negative_dose_fails_validation(self):
        rec = EvidenceRecord(
            evidence_id="EV-BIO-002",
            crop="Banana",
            crop_id="banana",
            problem="Panama Wilt",
            problem_id="banana_panama_wilt",
            recommendation_type=RecommendationType.BIOLOGICAL,
            active_ingredient="Pseudomonas fluorescens",
            application_basis="root dipping",
            dose=-2.5,
            dose_unit="g/l",
            source="TNAU Package of Practices",
            source_tier=SourceTier.TRUSTED_GOV_ACADEMIC,
            evidence_status=EvidenceStatus.VERIFIED,
        )
        is_valid, reason, _, _ = validate_evidence_record(rec)
        assert is_valid is False
        assert reason == ReasonCode.INVALID_DOSE_VALUE

    def test_biological_missing_active_ingredient_fails_validation(self):
        rec = EvidenceRecord(
            evidence_id="EV-BIO-003",
            crop="Banana",
            crop_id="banana",
            problem="Panama Wilt",
            problem_id="banana_panama_wilt",
            recommendation_type=RecommendationType.BIOLOGICAL,
            active_ingredient="",
            application_basis="root dipping",
            dose=5.0,
            dose_unit="g/l",
            source="TNAU Package of Practices",
            source_tier=SourceTier.TRUSTED_GOV_ACADEMIC,
            evidence_status=EvidenceStatus.VERIFIED,
        )
        is_valid, reason, _, _ = validate_evidence_record(rec)
        assert is_valid is False
        assert reason == ReasonCode.INCOMPLETE_METADATA

    def test_validate_dose_evidence_helper(self):
        # None
        ok, reason, _ = validate_dose_evidence(None)
        assert not ok
        assert reason == ReasonCode.MISSING_EXPLICIT_DOSE

        # Negative dose
        from thunai.core.models import DoseEvidence
        dose_neg = DoseEvidence(
            evidence_id="EV-01",
            active_ingredient="Test",
            dose_amount=-1.0,
            dose_unit="ml/l",
            has_explicit_dose=True,
        )
        ok, reason, _ = validate_dose_evidence(dose_neg)
        assert not ok
        assert reason == ReasonCode.INVALID_DOSE_VALUE

        # Invalid unit
        dose_bad_unit = DoseEvidence(
            evidence_id="EV-02",
            active_ingredient="Test",
            dose_amount=1.0,
            dose_unit="bottles",
            has_explicit_dose=True,
        )
        ok, reason, _ = validate_dose_evidence(dose_bad_unit)
        assert not ok
        assert reason == ReasonCode.MISSING_EXPLICIT_DOSE

