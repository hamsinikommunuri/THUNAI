"""Core models, enums, and normalization utilities for THUNAI."""

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
from thunai.core.models import (
    ActionDecision,
    DoseEvidence,
    EvidenceRecord,
    FarmerContext,
    SafetyDecision,
)
from thunai.core.normalizer import (
    BRAND_REGISTRY,
    CROP_ALIASES,
    PROBLEM_ALIASES,
    PROBLEM_REGISTRY,
    SUPPORTED_CROPS,
    NormalizedChemical,
    NormalizedCrop,
    NormalizedProblem,
    normalize_chemical,
    normalize_crop,
    normalize_problem,
)

__all__ = [
    "ActionStatus",
    "CropId",
    "DecisionType",
    "EvidenceStatus",
    "ReasonCategory",
    "ReasonCode",
    "RecommendationType",
    "SourceTier",
    "ActionDecision",
    "DoseEvidence",
    "EvidenceRecord",
    "FarmerContext",
    "SafetyDecision",
    "NormalizedChemical",
    "NormalizedCrop",
    "NormalizedProblem",
    "normalize_chemical",
    "normalize_crop",
    "normalize_problem",
    "SUPPORTED_CROPS",
    "CROP_ALIASES",
    "PROBLEM_REGISTRY",
    "PROBLEM_ALIASES",
    "BRAND_REGISTRY",
]
