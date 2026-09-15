"""Evidence validation module for agricultural recommendations.

Enforces:
1. Source verification (TNAU, ICAR, CIBRC vs unverified commercial/blogs)
2. Evidence lifecycle status (VERIFIED vs PROVISIONAL/EXPIRED/DEPRECATED)
3. Metadata completeness (crop, problem, active ingredient, formulation, basis)
4. Explicit numerical dose existence (no vague text, zero, or negative doses)
5. Detection of conflicting evidence across candidate records
"""

from typing import List, Optional, Tuple

from thunai.core.enums import (
    EvidenceStatus,
    ReasonCategory,
    ReasonCode,
    RecommendationType,
    SourceTier,
)
from thunai.core.models import DoseEvidence, EvidenceRecord

# Recognized valid dosage units in Indian agriculture
VALID_DOSE_UNITS = {
    "ml/l",
    "g/l",
    "ml/acre",
    "g/acre",
    "kg/ha",
    "l/ha",
    "kg/acre",
    "l/acre",
    "ppm",
    "%",
}


def validate_evidence_record(
    evidence: Optional[EvidenceRecord],
) -> Tuple[bool, Optional[ReasonCode], Optional[str], Optional[str]]:
    """Validates an evidence record for completeness, source credibility, and explicit dose.

    Returns:
        (is_valid, reason_code, english_explanation, tamil_explanation)
    """
    if evidence is None:
        return (
            False,
            ReasonCode.MISSING_EVIDENCE,
            "No agricultural evidence record was provided.",
            "பரிந்துரைக்கான எந்தவொரு சான்றாதாரமும் கிடைக்கவில்லை.",
        )

    # 1. Source Credibility Check
    if evidence.source_tier not in (SourceTier.REGULATORY, SourceTier.TRUSTED_GOV_ACADEMIC):
        return (
            False,
            ReasonCode.UNVERIFIED_SOURCE,
            (
                f"Evidence source '{evidence.source}' (tier: {evidence.source_tier.value}) "
                f"is not an approved institutional agricultural authority (TNAU, CIBRC, ICAR)."
            ),
            f"தகவல் மூலம் '{evidence.source}' அங்கீகரிக்கப்பட்ட அரசு அல்லது பல்கலைக்கழக ஆய்வு ஆதாரம் அல்ல.",
        )

    # 2. Evidence Status Check
    if evidence.evidence_status != EvidenceStatus.VERIFIED:
        return (
            False,
            ReasonCode.UNVERIFIED_STATUS,
            (
                f"Evidence record '{evidence.evidence_id}' has status '{evidence.evidence_status.value}' "
                f"(expected VERIFIED)."
            ),
            f"சான்றாதாரப் பதிவு '{evidence.evidence_id}' இன்னும் முழுமையாக சரிபார்க்கப்படவில்லை ({evidence.evidence_status.value}).",
        )

    # 3. Core Metadata Completeness
    missing_fields = []
    if not evidence.crop or not evidence.crop_id:
        missing_fields.append("crop")
    if not evidence.problem or not evidence.problem_id:
        missing_fields.append("problem")
    if not evidence.source:
        missing_fields.append("source")

    # If chemical or biological recommendation, check metadata
    if evidence.recommendation_type in (RecommendationType.CHEMICAL, RecommendationType.BIOLOGICAL):
        if not evidence.active_ingredient or not evidence.active_ingredient.strip():
            missing_fields.append("active_ingredient")
        if evidence.recommendation_type == RecommendationType.CHEMICAL and (not evidence.formulation or not evidence.formulation.strip()):
            missing_fields.append("formulation")
        if not evidence.application_basis or not evidence.application_basis.strip():
            missing_fields.append("application_basis")

    if missing_fields:
        return (
            False,
            ReasonCode.INCOMPLETE_METADATA,
            f"Evidence record '{evidence.evidence_id}' is missing required metadata fields: {', '.join(missing_fields)}.",
            f"சான்றாதாரப் பதிவில் முழுமையான தகவல்கள் இல்லை (விடுபட்டவை: {', '.join(missing_fields)}).",
        )

    # 4. Explicit Dose Existence and Validity
    if evidence.recommendation_type in (RecommendationType.CHEMICAL, RecommendationType.BIOLOGICAL):
        if evidence.dose is None:
            return (
                False,
                ReasonCode.MISSING_EXPLICIT_DOSE,
                f"Evidence record '{evidence.evidence_id}' contains no explicit numerical dose.",
                "சான்றாதாரப் பதிவில் தெளிவான மருந்து அளவு (dosage) குறிப்பிடப்படவில்லை.",
            )

        if evidence.dose <= 0:
            return (
                False,
                ReasonCode.INVALID_DOSE_VALUE,
                f"Evidence record '{evidence.evidence_id}' has an invalid non-positive dose ({evidence.dose}).",
                f"சான்றாதாரப் பதிவில் குறிப்பிடப்பட்டுள்ள மருந்து அளவு செல்லுபடியாகாது ({evidence.dose}).",
            )

        if not evidence.dose_unit or evidence.dose_unit.strip().lower() not in VALID_DOSE_UNITS:
            return (
                False,
                ReasonCode.MISSING_EXPLICIT_DOSE,
                f"Evidence record '{evidence.evidence_id}' has missing or unrecognized dose unit '{evidence.dose_unit}'.",
                f"சான்றாதாரப் பதிவில் மருந்து அளவு அலகு (unit) தவறாக உள்ளது: '{evidence.dose_unit}'.",
            )

    return (True, None, "Evidence verified successfully.", "சான்றாதாரம் வெற்றிகரமாக சரிபார்க்கப்பட்டது.")


def detect_conflicting_evidence(
    candidates: List[EvidenceRecord],
) -> Tuple[bool, Optional[str], Optional[str]]:
    """Detects irreconcilable conflicts among candidate evidence records for the same target.

    For example, if two records for the exact same active ingredient prescribe
    drastically divergent dosages (e.g. > 3x variation) or contradictory instructions.
    """
    if len(candidates) < 2:
        return False, None, None

    # Group by active ingredient
    ai_doses: dict[str, list[Tuple[EvidenceRecord, float, str]]] = {}
    for cand in candidates:
        if cand.active_ingredient and cand.dose is not None and cand.dose_unit:
            key = cand.active_ingredient.lower().strip()
            ai_doses.setdefault(key, []).append((cand, cand.dose, cand.dose_unit.lower().strip()))

    for ai, dose_list in ai_doses.items():
        if len(dose_list) >= 2:
            # Check if same unit but wide discrepancy (> 2.5x spread)
            units = {d[2] for d in dose_list}
            if len(units) == 1:
                vals = [d[1] for d in dose_list]
                min_val = min(vals)
                max_val = max(vals)
                if min_val > 0 and (max_val / min_val) >= 2.5:
                    rec_ids = [d[0].evidence_id for d in dose_list]
                    return (
                        True,
                        (
                            f"Conflicting dosage evidence detected for {ai.title()}: "
                            f"records {rec_ids} specify divergent dosages ({min_val} vs {max_val} {list(units)[0]})."
                        ),
                        (
                            f"{ai.title()} மருந்துக்கான சான்றாதாரங்களில் ஒன்றுக்கொன்று முரண்பாடான அளவுகள் "
                            f"உள்ளன ({min_val} vs {max_val} {list(units)[0]})."
                        ),
                    )

    return False, None, None


def validate_dose_evidence(dose_evidence: Optional[DoseEvidence]) -> Tuple[bool, Optional[ReasonCode], Optional[str]]:
    """Validates a DoseEvidence object for explicit positive dosage."""
    if dose_evidence is None:
        return False, ReasonCode.MISSING_EXPLICIT_DOSE, "Dose evidence object is missing."
    if not dose_evidence.has_explicit_dose or dose_evidence.dose_amount is None:
        return False, ReasonCode.MISSING_EXPLICIT_DOSE, "Dose evidence does not have an explicit numerical dosage."
    if dose_evidence.dose_amount <= 0:
        return False, ReasonCode.INVALID_DOSE_VALUE, f"Invalid dosage value ({dose_evidence.dose_amount})."
    if not dose_evidence.dose_unit or dose_evidence.dose_unit.lower() not in VALID_DOSE_UNITS:
        return False, ReasonCode.MISSING_EXPLICIT_DOSE, f"Invalid or missing dose unit ({dose_evidence.dose_unit})."
    return True, None, "Dose evidence is valid."
