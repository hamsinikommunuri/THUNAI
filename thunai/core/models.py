"""Data models for THUNAI deterministic safety engine.

Includes:
- FarmerContext: farmer query and identified agricultural parameters
- DoseEvidence: explicit dosage parameters attached to evidence
- EvidenceRecord: structured agricultural knowledge with full traceability
- SafetyDecision: explainable deterministic decision
- ActionDecision: actionable advisory outcome for the farmer
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field

from thunai.core.enums import (
    ActionStatus,
    CropId,
    DecisionType,
    EvidenceStatus,
    ReasonCategory,
    ReasonCode,
    RecommendationType,
    SourceTier,
)


class DoseEvidence(BaseModel):
    """Structured dosage information extracted from verified evidence."""
    model_config = ConfigDict(frozen=True)

    evidence_id: str
    active_ingredient: str
    formulation: Optional[str] = None
    concentration: Optional[str] = None
    dose_amount: Optional[float] = None
    dose_unit: Optional[str] = None
    application_method: Optional[str] = None
    dilution_rate: Optional[str] = None
    water_volume_l_per_acre: Optional[float] = None
    waiting_period_days: Optional[int] = None
    max_applications: Optional[int] = None
    has_explicit_dose: bool = False

    @property
    def formatted_dose(self) -> Optional[str]:
        """Returns readable dose string e.g. '2.0 ml/l'."""
        if self.has_explicit_dose and self.dose_amount is not None and self.dose_unit:
            return f"{self.dose_amount} {self.dose_unit}"
        return None


class EvidenceRecord(BaseModel):
    """Structured metadata record for agricultural recommendation evidence."""
    model_config = ConfigDict(frozen=True)

    evidence_id: str
    crop: str
    crop_id: str
    crop_scientific_name: Optional[str] = None
    problem: str
    problem_id: str
    recommendation_type: RecommendationType = RecommendationType.CHEMICAL
    active_ingredient: Optional[str] = None
    formulation: Optional[str] = None
    concentration: Optional[str] = None
    brand_names: List[str] = Field(default_factory=list)
    dose: Optional[float] = None
    dose_unit: Optional[str] = None
    application_basis: Optional[str] = None
    water_volume_l_per_acre: Optional[float] = None
    waiting_period_days: Optional[int] = None
    source: str
    source_reference: Optional[str] = None
    source_tier: SourceTier = SourceTier.TRUSTED_GOV_ACADEMIC
    geography: Optional[str] = "Tamil Nadu"
    evidence_status: EvidenceStatus = EvidenceStatus.VERIFIED
    created_at: Optional[str] = None
    notes: Optional[str] = None

    def to_dose_evidence(self) -> DoseEvidence:
        """Converts evidence record into a DoseEvidence structure."""
        has_dose = bool(self.dose is not None and self.dose > 0 and self.dose_unit)
        return DoseEvidence(
            evidence_id=self.evidence_id,
            active_ingredient=self.active_ingredient or "",
            formulation=self.formulation,
            concentration=self.concentration,
            dose_amount=self.dose,
            dose_unit=self.dose_unit,
            application_method=self.application_basis,
            dilution_rate=f"{self.dose} {self.dose_unit}" if has_dose else None,
            water_volume_l_per_acre=self.water_volume_l_per_acre,
            waiting_period_days=self.waiting_period_days,
            has_explicit_dose=has_dose,
        )


class FarmerContext(BaseModel):
    """Farmer's agricultural context extracted from natural query or structured input."""
    model_config = ConfigDict(arbitrary_types_allowed=True)

    farmer_id: Optional[str] = None
    raw_query: str = ""
    crop: Optional[str] = None
    crop_id: Optional[str] = None
    crop_scientific_name: Optional[str] = None
    target_problem: Optional[str] = None
    problem_id: Optional[str] = None
    growth_stage: Optional[str] = None
    location: Optional[str] = None
    geography: Optional[str] = "Tamil Nadu"
    days_to_harvest: Optional[int] = None
    weather_condition: Optional[Dict[str, Any]] = None
    is_prompt_injection: bool = False
    is_ambiguous: bool = False
    requested_chemical: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class SafetyDecision(BaseModel):
    """Explainable deterministic safety gate decision."""
    model_config = ConfigDict(frozen=True)

    decision: DecisionType
    reason_code: ReasonCode
    reason_category: ReasonCategory
    human_reason: str
    human_reason_ta: Optional[str] = None
    evidence_id: Optional[str] = None
    allowed_dose: Optional[DoseEvidence] = None
    context_crop: Optional[str] = None
    evidence_crop: Optional[str] = None
    regulatory_status: Optional[str] = None
    trace: List[str] = Field(default_factory=list)

    @property
    def is_allowed(self) -> bool:
        return self.decision == DecisionType.ALLOW

    @property
    def is_blocked(self) -> bool:
        return self.decision == DecisionType.BLOCK

    @property
    def is_escalated(self) -> bool:
        return self.decision == DecisionType.ESCALATE


class ActionDecision(BaseModel):
    """Operational action and farmer-facing advisory outcome."""
    model_config = ConfigDict(frozen=True)

    status: ActionStatus
    safety_decision: SafetyDecision
    can_recommend_chemical: bool
    can_recommend_dose: bool
    recommended_action: Optional[str] = None
    farmer_message: str
    farmer_message_ta: Optional[str] = None
    escalation_needed: bool = False
    escalation_reason: Optional[str] = None
    next_step: Optional[str] = None
