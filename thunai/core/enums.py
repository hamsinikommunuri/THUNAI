"""Core enumeration types for the THUNAI deterministic safety engine.

Distinguishes between legal/regulatory blocking, evidence mismatch,
product-safety policy, weather gating, uncertainty, and verified approvals.
"""

from enum import Enum


class DecisionType(str, Enum):
    """Decision outcome of the deterministic safety gate."""
    ALLOW = "ALLOW"
    BLOCK = "BLOCK"
    ESCALATE = "ESCALATE"


class ReasonCategory(str, Enum):
    """Broad categorization of safety determinations.

    Ensures legal prohibitions, evidence mismatches, safety policies,
    weather gates, and uncertainty are not collapsed into a single generic flag.
    """
    LEGAL_REGULATORY = "LEGAL_REGULATORY"
    EVIDENCE_MISMATCH = "EVIDENCE_MISMATCH"
    PRODUCT_SAFETY_POLICY = "PRODUCT_SAFETY_POLICY"
    WEATHER_GATE = "WEATHER_GATE"
    UNCERTAINTY = "UNCERTAINTY"
    VALID_VERIFIED = "VALID_VERIFIED"


class ReasonCode(str, Enum):
    """Granular machine-readable reason codes explaining every decision."""
    # Legal & Regulatory
    BANNED_CHEMICAL = "BANNED_CHEMICAL"
    RESTRICTED_CHEMICAL = "RESTRICTED_CHEMICAL"
    UNREGISTERED_LABEL_CLAIM = "UNREGISTERED_LABEL_CLAIM"

    # Evidence & Agricultural Context Mismatches
    CROP_MISMATCH = "CROP_MISMATCH"
    PROBLEM_MISMATCH = "PROBLEM_MISMATCH"
    CHEMICAL_MISMATCH = "CHEMICAL_MISMATCH"
    CROSS_CROP_LEAKAGE = "CROSS_CROP_LEAKAGE"

    # THUNAI Product-Safety Policy
    HIGH_TOXICITY_RESTRICTION = "HIGH_TOXICITY_RESTRICTION"
    PRE_HARVEST_INTERVAL_VIOLATION = "PRE_HARVEST_INTERVAL_VIOLATION"
    HAZARDOUS_TANK_MIX = "HAZARDOUS_TANK_MIX"

    # Weather Gates
    RAIN_GATED = "RAIN_GATED"
    WIND_GATED = "WIND_GATED"
    TEMPERATURE_GATED = "TEMPERATURE_GATED"

    # Uncertainty & Incompleteness
    AMBIGUOUS_CROP = "AMBIGUOUS_CROP"
    AMBIGUOUS_PROBLEM = "AMBIGUOUS_PROBLEM"
    UNKNOWN_CROP = "UNKNOWN_CROP"
    MISSING_EVIDENCE = "MISSING_EVIDENCE"
    MISSING_EXPLICIT_DOSE = "MISSING_EXPLICIT_DOSE"
    INVALID_DOSE_VALUE = "INVALID_DOSE_VALUE"
    INCOMPLETE_METADATA = "INCOMPLETE_METADATA"
    UNVERIFIED_SOURCE = "UNVERIFIED_SOURCE"
    UNVERIFIED_STATUS = "UNVERIFIED_STATUS"
    CONFLICTING_EVIDENCE = "CONFLICTING_EVIDENCE"
    PROMPT_INJECTION_DETECTED = "PROMPT_INJECTION_DETECTED"

    # Valid & Verified
    VERIFIED_AND_ALLOWED = "VERIFIED_AND_ALLOWED"


class ActionStatus(str, Enum):
    """Operational advisory status presented to the farmer."""
    ALLOW_RECOMMENDATION = "ALLOW_RECOMMENDATION"
    BLOCK_AND_EXPLAIN = "BLOCK_AND_EXPLAIN"
    ESCALATE_TO_EXPERT = "ESCALATE_TO_EXPERT"
    REQUEST_CLARIFICATION = "REQUEST_CLARIFICATION"


class CropId(str, Enum):
    """Phase 1 Target Crops."""
    PADDY = "paddy"
    TOMATO = "tomato"
    BANANA = "banana"
    CHILLI = "chilli"


class EvidenceStatus(str, Enum):
    """Validation lifecycle status of an evidence record."""
    VERIFIED = "VERIFIED"
    PROVISIONAL = "PROVISIONAL"
    EXPIRED = "EXPIRED"
    UNVERIFIED = "UNVERIFIED"
    DEPRECATED = "DEPRECATED"


class SourceTier(str, Enum):
    """Credibility tier of evidence source."""
    REGULATORY = "REGULATORY"                    # CIBRC, Central Govt gazette
    TRUSTED_GOV_ACADEMIC = "TRUSTED_GOV_ACADEMIC"  # TNAU, ICAR, State Agri Univ
    COMMERCIAL = "COMMERCIAL"                    # Manufacturer brochure/commercial site
    UNVERIFIED = "UNVERIFIED"                    # Blogs, forum posts, uncurated web


class RecommendationType(str, Enum):
    """Methodological type of agricultural recommendation."""
    CHEMICAL = "chemical"
    BIOLOGICAL = "biological"
    CULTURAL = "cultural"
    MECHANICAL = "mechanical"
