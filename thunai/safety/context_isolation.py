"""Context isolation and agricultural filtering module.

Enforces strict isolation between crops to prevent cross-crop dosage leakage.
Applies hard agricultural filters before any downstream processing.
Detects prompt injection, ambiguous queries, and unsupported crops.
"""

import re
from typing import List, Optional, Tuple

from thunai.core.enums import (
    DecisionType,
    ReasonCategory,
    ReasonCode,
)
from thunai.core.models import EvidenceRecord, FarmerContext, SafetyDecision
from thunai.core.normalizer import (
    SUPPORTED_CROPS,
    normalize_crop,
    normalize_problem,
)

# Known prompt injection / safety bypass phrases
INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?safety",
    r"override\s+(dose\s+lock|safety|restrictions)",
    r"bypass\s+(dose\s+lock|safety|checks)",
    r"forget\s+(previous\s+instructions|rules|safety)",
    r"disregard\s+(all\s+)?(rules|restrictions|safety)",
    r"developer\s+mode",
    r"dan\s+mode",
    r"jailbreak",
    r"pretend\s+you\s+are\s+unrestricted",
    r"system\s+prompt\s+override",
    r"admin\s+override",
    r"unlocked\s+mode",
]

# Vague or ambiguous symptom descriptions
AMBIGUOUS_SYMPTOM_PATTERNS = [
    r"(my\s+)?(plant|crop|field)\s+(has\s+bugs|is\s+sick|has\s+disease|has\s+problem)",
    r"leaves\s+turn\s+yellow|yellow\s+leaves|ilai\s+manjal",
    r"give\s+(me\s+)?(a\s+|some\s+)?(spray|medicine|chemical)|suggest\s+medicine|marundhu\s+kudu",
    r"some\s+(pest|bug)|poochi\s+irukku",
    r"what\s+to\s+spray|edhavadhu\s+thelikkavum",
    r"poo\s+(koriyudhu|kottudhu|udhirudhu)|flower\s+drop",
    r"ilai\s+(kaayudhu|vadudhu)",
    r"kutti\s+puzhu|chinna\s+puzhu",
]


def detect_prompt_injection(text: str) -> bool:
    """Detects whether text contains prompt injection or safety bypass patterns."""
    if not text:
        return False
    lower_text = text.lower()
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, lower_text):
            return True
    return False


def is_ambiguous_query(text: str) -> bool:
    """Detects whether query is too vague to identify crop or specific pest."""
    if not text or len(text.strip()) < 3:
        return True
    lower_text = text.lower()
    for pattern in AMBIGUOUS_SYMPTOM_PATTERNS:
        if re.search(pattern, lower_text):
            return True
    return False


def isolate_crop_context(context: FarmerContext) -> FarmerContext:
    """Normalizes and isolates crop context from farmer input.

    Identifies crop, problem, prompt injection, and ambiguity.
    Guarantees that context.crop_id is set only if cleanly matched
    to one of the 4 supported crops.
    """
    query = context.raw_query or ""

    # Check for prompt injection
    if detect_prompt_injection(query):
        context.is_prompt_injection = True

    # Check for multi-crop mentions in query
    from thunai.core.normalizer import CROP_ALIASES, BRAND_REGISTRY
    from thunai.safety.chemical_safety import REGULATORY_DATABASE

    detected_crops = set()
    cleaned_query = query.strip().lower()
    for alias, c_id in CROP_ALIASES.items():
        if any(ord(c) > 127 for c in alias):
            if alias in cleaned_query:
                detected_crops.add(c_id)
        else:
            if re.search(rf"\b{re.escape(alias)}\b", cleaned_query):
                detected_crops.add(c_id)

    # Normalize crop if not already cleanly set
    if not context.crop_id:
        if context.crop:
            norm_c = normalize_crop(context.crop)
            if norm_c:
                context.crop_id = norm_c.crop_id
                context.crop = norm_c.canonical_name
                context.crop_scientific_name = norm_c.scientific_name
        elif len(detected_crops) > 1:
            # Multi-crop collision in query (e.g. intercropping)
            # Try to disambiguate by checking if problem matches only one crop
            prob_matches = {}
            for c_id in detected_crops:
                p = normalize_problem(context.target_problem, c_id) or normalize_problem(query, c_id)
                if p:
                    prob_matches[c_id] = p
            if len(prob_matches) == 1:
                resolved_crop_id = list(prob_matches.keys())[0]
                norm_c = SUPPORTED_CROPS.get(resolved_crop_id)
                if norm_c:
                    context.crop_id = norm_c.crop_id
                    context.crop = norm_c.canonical_name
                    context.crop_scientific_name = norm_c.scientific_name
                    context.problem_id = prob_matches[resolved_crop_id].problem_id
                    context.target_problem = prob_matches[resolved_crop_id].canonical_name
            else:
                context.is_ambiguous = True
        elif len(detected_crops) == 1:
            c_id = list(detected_crops)[0]
            norm_c = SUPPORTED_CROPS.get(c_id)
            if norm_c:
                context.crop_id = norm_c.crop_id
                context.crop = norm_c.canonical_name
                context.crop_scientific_name = norm_c.scientific_name
        else:
            # Check for known unsupported crops outside Phase 1
            unsupported_crops = [
                "wheat", "cotton", "sugarcane", "maize", "corn",
                "apple", "mango", "groundnut", "tea", "coffee", "sorghum"
            ]
            for uncrop in unsupported_crops:
                if re.search(rf"\b{uncrop}\b", cleaned_query):
                    context.crop = uncrop.title()
                    break

            # Check if query is ambiguous
            if not context.crop and (is_ambiguous_query(query) or not query.strip()):
                context.is_ambiguous = True

    # Normalize problem if not already cleanly set
    if not context.problem_id and context.crop_id:
        normalized_p = normalize_problem(context.target_problem, context.crop_id) or \
                       normalize_problem(query, context.crop_id)
        if normalized_p:
            context.problem_id = normalized_p.problem_id
            context.target_problem = normalized_p.canonical_name

    # If crop is present but problem is completely ambiguous or missing
    if context.crop_id and not context.problem_id and (is_ambiguous_query(query) or not context.target_problem):
        if not context.target_problem:
            context.is_ambiguous = True

    # Extract requested chemical from query if not already set (using word boundaries)
    if not context.requested_chemical and query:
        # Check brands
        for brand in BRAND_REGISTRY:
            if any(ord(c) > 127 for c in brand):
                if brand in cleaned_query:
                    context.requested_chemical = brand
                    break
            else:
                if re.search(rf"\b{re.escape(brand)}\b", cleaned_query):
                    context.requested_chemical = brand
                    break

        # Check regulatory chemicals
        if not context.requested_chemical:
            for reg_ai in REGULATORY_DATABASE:
                if any(ord(c) > 127 for c in reg_ai):
                    if reg_ai in cleaned_query:
                        context.requested_chemical = reg_ai
                        break
                else:
                    if re.search(rf"\b{re.escape(reg_ai)}\b", cleaned_query):
                        context.requested_chemical = reg_ai
                        break

        # Check common off-label chemicals
        if not context.requested_chemical:
            for off_label in ["atrazine", "2,4-d", "paclobutrazol"]:
                if re.search(rf"\b{re.escape(off_label)}\b", cleaned_query):
                    context.requested_chemical = off_label
                    break

    return context


def apply_hard_agricultural_filter(
    context: FarmerContext,
    candidates: List[EvidenceRecord],
) -> List[EvidenceRecord]:
    """Applies strict agricultural filters to evidence candidates.

    Hard rule: A candidate MUST match the farmer's crop_id.
    Cross-crop records are instantly filtered out.
    If target problem is specified, problem_id must also match.
    """
    if not context.crop_id:
        return []

    filtered: List[EvidenceRecord] = []
    for cand in candidates:
        # Strict crop match
        if cand.crop_id.lower() != context.crop_id.lower():
            continue
        # Strict problem match
        if context.problem_id:
            if cand.problem_id.lower() != context.problem_id.lower():
                continue
        elif context.target_problem:
            target_lower = context.target_problem.lower()
            if target_lower != cand.problem.lower() and target_lower != cand.problem_id.lower():
                continue
        filtered.append(cand)
    return filtered


def check_context_leakage(
    context: FarmerContext,
    evidence: EvidenceRecord,
) -> Optional[SafetyDecision]:
    """Explicitly checks if an evidence record leaks across crops or problems.

    Returns a SafetyDecision BLOCK if a collision or mismatch is detected,
    or None if the evidence matches the context crop and problem.
    """
    # 1. Unknown or missing farmer crop
    if not context.crop_id:
        if context.is_ambiguous:
            return SafetyDecision(
                decision=DecisionType.BLOCK,
                reason_code=ReasonCode.AMBIGUOUS_CROP,
                reason_category=ReasonCategory.UNCERTAINTY,
                human_reason="Farmer query does not specify a clear crop context.",
                human_reason_ta="விவசாயியின் கோரிக்கையில் பயிர் தெளிவாகக் குறிப்பிடப்படவில்லை.",
                context_crop=None,
                evidence_crop=evidence.crop,
                evidence_id=evidence.evidence_id,
                trace=["context_isolation:AMBIGUOUS_CROP"],
            )
        return SafetyDecision(
            decision=DecisionType.BLOCK,
            reason_code=ReasonCode.UNKNOWN_CROP,
            reason_category=ReasonCategory.UNCERTAINTY,
            human_reason=f"Crop '{context.crop or 'unknown'}' is not among Phase 1 supported crops (Paddy, Tomato, Banana, Chilli).",
            human_reason_ta="குறிப்பிடப்பட்ட பயிர் ஆதரிக்கப்படும் 4 பயிர்களில் (நெல், தக்காளி, வாழை, மிளகாய்) இல்லை.",
            context_crop=context.crop,
            evidence_crop=evidence.crop,
            evidence_id=evidence.evidence_id,
            trace=["context_isolation:UNKNOWN_CROP"],
        )

    # 2. Crop Mismatch (Single evidence record mismatch)
    if context.crop_id.lower() != evidence.crop_id.lower():
        return SafetyDecision(
            decision=DecisionType.BLOCK,
            reason_code=ReasonCode.CROP_MISMATCH,
            reason_category=ReasonCategory.EVIDENCE_MISMATCH,
            human_reason=(
                f"Retrieved dosage belongs to {evidence.crop.lower()}, "
                f"while farmer context is {context.crop.lower()}."
            ),
            human_reason_ta=(
                f"பயிர் முரண்பாடு: பெறப்பட்ட தகவல் {evidence.crop} பயிருக்குரியது, "
                f"ஆனால் விவசாயியின் பயிர் {context.crop}."
            ),
            context_crop=context.crop_id,
            evidence_crop=evidence.crop_id,
            evidence_id=evidence.evidence_id,
            trace=["context_isolation:CROP_MISMATCH"],
        )

    # 3. Problem Mismatch
    if context.problem_id:
        if evidence.problem_id.lower() != context.problem_id.lower():
            return SafetyDecision(
                decision=DecisionType.BLOCK,
                reason_code=ReasonCode.PROBLEM_MISMATCH,
                reason_category=ReasonCategory.EVIDENCE_MISMATCH,
                human_reason=(
                    f"Problem mismatch: Retrieved evidence targets {evidence.problem} "
                    f"({evidence.problem_id}), while farmer context targets "
                    f"{context.target_problem or context.problem_id}."
                ),
                human_reason_ta=(
                    f"பாதிப்பு முரண்பாடு: பெறப்பட்ட மருந்து {evidence.problem} பாதிப்புக்கானது, "
                    f"ஆனால் தேவைப்படுவது {context.target_problem or context.problem_id}."
                ),
                context_crop=context.crop_id,
                evidence_crop=evidence.crop_id,
                evidence_id=evidence.evidence_id,
                trace=["context_isolation:PROBLEM_MISMATCH"],
            )
    elif context.target_problem:
        target_lower = context.target_problem.lower()
        if target_lower != evidence.problem.lower() and target_lower != evidence.problem_id.lower():
            return SafetyDecision(
                decision=DecisionType.BLOCK,
                reason_code=ReasonCode.PROBLEM_MISMATCH,
                reason_category=ReasonCategory.EVIDENCE_MISMATCH,
                human_reason=(
                    f"Problem mismatch: Retrieved evidence targets {evidence.problem} "
                    f"({evidence.problem_id}), while farmer context targets "
                    f"{context.target_problem}."
                ),
                human_reason_ta=(
                    f"பாதிப்பு முரண்பாடு: பெறப்பட்ட மருந்து {evidence.problem} பாதிப்புக்கானது, "
                    f"ஆனால் தேவைப்படுவது {context.target_problem}."
                ),
                context_crop=context.crop_id,
                evidence_crop=evidence.crop_id,
                evidence_id=evidence.evidence_id,
                trace=["context_isolation:PROBLEM_MISMATCH"],
            )

    return None
