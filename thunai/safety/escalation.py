"""Escalation and Action Decision module.

Maps SafetyDecisions into operational ActionDecisions for farmers:
- Provides clear, actionable explanations in English and farmer-friendly Tamil.
- Flags when human extension officer (KVK / Agronomist) escalation is mandatory.
- Requests clarification for ambiguous queries with targeted questions.
- Guarantees zero invented doses in all non-allowed paths.
"""

from typing import Optional

from thunai.core.enums import (
    ActionStatus,
    DecisionType,
    ReasonCategory,
    ReasonCode,
)
from thunai.core.models import (
    ActionDecision,
    FarmerContext,
    SafetyDecision,
)


def build_action_decision(
    safety_decision: SafetyDecision,
    context: FarmerContext,
) -> ActionDecision:
    """Constructs an ActionDecision from a SafetyDecision.

    Determines if human escalation is required, crafts clear farmer messages,
    and guarantees that no dosage is recommended unless safety_decision is ALLOW.
    """
    if safety_decision.is_allowed:
        dose = safety_decision.allowed_dose
        dose_str = dose.formatted_dose if dose else ""
        form_str = f" ({dose.formulation})" if (dose and dose.formulation) else ""
        ai_str = dose.active_ingredient if dose else ""
        app_method = (dose.application_method if dose and dose.application_method else "foliar spray")
        app_method_ta = (dose.application_method if dose and dose.application_method else "இலை வழியாகத் தெளிக்கவும்")
        farmer_msg = (
            f"Recommended treatment: {ai_str}{form_str}. "
            f"Apply {dose_str} as {app_method}. "
            f"Always wear protective gloves and mask while spraying."
        )
        farmer_msg_ta = (
            f"பரிந்துரைக்கப்படும் மருந்து: {ai_str}{form_str}. "
            f"தெளிக்கும் அளவு: {dose_str} ({app_method_ta}). "
            f"தெளிக்கும்போது முகக்கவசம் மற்றும் கையுறைகளை அணியவும்."
        )
        return ActionDecision(
            status=ActionStatus.ALLOW_RECOMMENDATION,
            safety_decision=safety_decision,
            can_recommend_chemical=True,
            can_recommend_dose=True,
            recommended_action=f"Apply {dose_str} of {ai_str}".strip(),
            farmer_message=farmer_msg,
            farmer_message_ta=farmer_msg_ta,
            escalation_needed=False,
            escalation_reason=None,
            next_step="Apply at recommended dosage using proper PPE.",
        )

    # 2. BLOCK / ESCALATION PATHS (LOCKED BY DEFAULT - ZERO INVENTED DOSES)
    reason_code = safety_decision.reason_code

    # A. Legal / Regulatory Bans & Restrictions
    if safety_decision.reason_category == ReasonCategory.LEGAL_REGULATORY:
        if reason_code == ReasonCode.BANNED_CHEMICAL:
            return ActionDecision(
                status=ActionStatus.BLOCK_AND_EXPLAIN,
                safety_decision=safety_decision,
                can_recommend_chemical=False,
                can_recommend_dose=False,
                farmer_message=(
                    f"Action Blocked: {safety_decision.human_reason} "
                    f"THUNAI cannot provide any dosage for banned chemicals. "
                    f"Please contact your local Agricultural Officer or KVK for safe, legal alternatives."
                ),
                farmer_message_ta=(
                    f"நடவடிக்கை தடுக்கப்பட்டது: {safety_decision.human_reason_ta} "
                    f"தடை செய்யப்பட்ட மருந்துகளுக்கு எந்த அளவும் வழங்கப்படாது. "
                    f"பாதுகாப்பான மாற்று மருந்துகளுக்கு உங்கள் வட்டார வேளாண்மை அலுவலர் அல்லது கே.வி.கே-ஐ அணுகவும்."
                ),
                escalation_needed=True,
                escalation_reason="Banned chemical requested; regulatory advisory required.",
                next_step="Consult local KVK or agricultural extension officer for approved bio/chemical alternatives.",
            )

        if reason_code == ReasonCode.RESTRICTED_CHEMICAL:
            return ActionDecision(
                status=ActionStatus.BLOCK_AND_EXPLAIN,
                safety_decision=safety_decision,
                can_recommend_chemical=False,
                can_recommend_dose=False,
                farmer_message=(
                    f"Action Blocked: {safety_decision.human_reason} "
                    f"This chemical has statutory use restrictions and cannot be sprayed on food crops."
                ),
                farmer_message_ta=(
                    f"நடவடிக்கை தடுக்கப்பட்டது: {safety_decision.human_reason_ta} "
                    f"இந்த மருந்து குறிப்பிட்ட பயன்பாடுகளுக்கு மட்டுமே அனுமதிக்கப்பட்டது."
                ),
                escalation_needed=True,
                escalation_reason="Statutory chemical restriction violated.",
                next_step="Use only approved crop-specific management practices.",
            )

        # Unregistered label claim
        return ActionDecision(
            status=ActionStatus.BLOCK_AND_EXPLAIN,
            safety_decision=safety_decision,
            can_recommend_chemical=False,
            can_recommend_dose=False,
            farmer_message=(
                f"Action Blocked: {safety_decision.human_reason} "
                f"Off-label pesticide usage is unapproved and unsafe. No dosage will be provided."
            ),
            farmer_message_ta=(
                f"நடவடிக்கை தடுக்கப்பட்டது: {safety_decision.human_reason_ta} "
                f"அங்கீகரிக்கப்படாத பயன்பாட்டுக்கு மருந்து அளவு வழங்கப்படாது."
            ),
            escalation_needed=False,
            next_step="Select a CIBRC approved chemical for this crop.",
        )

    # B. Weather-Gated Spraying
    if safety_decision.reason_category == ReasonCategory.WEATHER_GATE:
        return ActionDecision(
            status=ActionStatus.BLOCK_AND_EXPLAIN,
            safety_decision=safety_decision,
            can_recommend_chemical=False,
            can_recommend_dose=False,
            farmer_message=(
                f"Spraying Temporarily Suspended: {safety_decision.human_reason} "
                f"Postpone spraying until weather conditions improve."
            ),
            farmer_message_ta=(
                f"தெளிப்பு தற்காலிகமாக ஒத்திவைக்கப்பட்டுள்ளது: {safety_decision.human_reason_ta} "
                f"வானிலை சீரடையும் வரை மருந்து தெளிப்பதைத் தவிர்க்கவும்."
            ),
            escalation_needed=False,
            next_step="Check weather forecast and spray in calm, clear weather (early morning or late afternoon).",
        )

    # C. THUNAI Product-Safety Policy (PHI, Toxicity, Tank Mix)
    if safety_decision.reason_category == ReasonCategory.PRODUCT_SAFETY_POLICY:
        if reason_code == ReasonCode.PRE_HARVEST_INTERVAL_VIOLATION:
            return ActionDecision(
                status=ActionStatus.BLOCK_AND_EXPLAIN,
                safety_decision=safety_decision,
                can_recommend_chemical=False,
                can_recommend_dose=False,
                farmer_message=(
                    f"Action Blocked: {safety_decision.human_reason} "
                    f"Spraying so close to harvest poses chemical residue hazards for consumers. "
                    f"Please consult your local KVK or agricultural officer for safe non-chemical management."
                ),
                farmer_message_ta=(
                    f"நடவடிக்கை தடுக்கப்பட்டது: {safety_decision.human_reason_ta} "
                    f"அறுவடைக்கு மிக அருகில் மருந்து தெளிப்பது நச்சு எச்ச அபாயத்தை உருவாக்கும். "
                    f"பாதுகாப்பான மாற்று வழிகளுக்கு கே.வி.கே அல்லது வேளாண்மை அலுவலரை அணுகவும்."
                ),
                escalation_needed=True,
                escalation_reason="Pre-harvest interval (PHI) constraint violated; residue risk.",
                next_step="Wait until post-harvest or use non-chemical pest management.",
            )

        if reason_code == ReasonCode.HAZARDOUS_TANK_MIX:
            return ActionDecision(
                status=ActionStatus.BLOCK_AND_EXPLAIN,
                safety_decision=safety_decision,
                can_recommend_chemical=False,
                can_recommend_dose=False,
                farmer_message=(
                    f"Hazardous Tank Mix Blocked: {safety_decision.human_reason} "
                    f"Tank-mixing chemically incompatible pesticides causes rapid chemical breakdown, "
                    f"reduced efficacy, and severe crop burning (phytotoxicity). "
                    f"Never combine these chemicals in the same spray tank."
                ),
                farmer_message_ta=(
                    f"ஆபத்தான மருந்து கலவை தடுக்கப்பட்டது: {safety_decision.human_reason_ta} "
                    f"ஒன்றோடொன்று பொருந்தாத மருந்துகளைக் கலப்பது மருந்தின் வீரியத்தை இழக்கச் செய்து "
                    f"பயிர் கருகலை ஏற்படுத்தும். இவற்றை ஒன்றாகக் கலந்து தெளிக்கக் கூடாது."
                ),
                escalation_needed=True,
                escalation_reason="Chemical incompatibility and phytotoxicity risk.",
                next_step="Apply products individually with a minimum 3-5 day gap.",
            )

        return ActionDecision(
            status=ActionStatus.BLOCK_AND_EXPLAIN,
            safety_decision=safety_decision,
            can_recommend_chemical=False,
            can_recommend_dose=False,
            farmer_message=f"Safety Policy Block: {safety_decision.human_reason}",
            farmer_message_ta=f"பாதுகாப்புக் கொள்கை கட்டுப்பாடு: {safety_decision.human_reason_ta or ''}",
            escalation_needed=True,
            escalation_reason="THUNAI product-safety policy gate engaged.",
            next_step="Consult local agricultural extension officer for approved alternatives.",
        )

    # D. Ambiguous Query / Unknown Crop
    if reason_code in (ReasonCode.AMBIGUOUS_CROP, ReasonCode.AMBIGUOUS_PROBLEM):
        clarification_q = (
            "Please specify: 1) Which crop (Paddy, Tomato, Banana, or Chilli)? "
            "2) What specific symptoms or pest are you observing on the leaves/stem/fruit?"
        )
        clarification_q_ta = (
            "தயவுசெய்து தெளிவுபடுத்தவும்: 1) எந்த பயிர் (நெல், தக்காளி, வாழை, மிளகாய்)? "
            "2) இலை, தண்டு அல்லது காய்களில் என்ன வகையான அறிகுறிகள் அல்லது பூச்சிகள் காணப்படுகின்றன?"
        )
        return ActionDecision(
            status=ActionStatus.REQUEST_CLARIFICATION,
            safety_decision=safety_decision,
            can_recommend_chemical=False,
            can_recommend_dose=False,
            farmer_message=f"{safety_decision.human_reason} {clarification_q}",
            farmer_message_ta=f"{safety_decision.human_reason_ta} {clarification_q_ta}",
            escalation_needed=False,
            next_step="Clarify crop and symptom details.",
        )

    if reason_code == ReasonCode.UNKNOWN_CROP:
        return ActionDecision(
            status=ActionStatus.BLOCK_AND_EXPLAIN,
            safety_decision=safety_decision,
            can_recommend_chemical=False,
            can_recommend_dose=False,
            farmer_message=(
                f"{safety_decision.human_reason} "
                f"THUNAI Phase 1 currently verifies recommendations only for Paddy, Tomato, Banana, and Chilli."
            ),
            farmer_message_ta=(
                f"{safety_decision.human_reason_ta} "
                f"துணை முதற்கட்டமாக நெல், தக்காளி, வாழை மற்றும் மிளகாய் பயிர்களுக்கு மட்டுமே சரிபார்க்கப்பட்ட தகவல்களை வழங்குகிறது."
            ),
            escalation_needed=True,
            escalation_reason="Crop outside Phase 1 coverage.",
            next_step="Contact district agricultural department for other crops.",
        )

    # D. Conflicting Evidence
    if reason_code == ReasonCode.CONFLICTING_EVIDENCE:
        return ActionDecision(
            status=ActionStatus.ESCALATE_TO_EXPERT,
            safety_decision=safety_decision,
            can_recommend_chemical=False,
            can_recommend_dose=False,
            farmer_message=(
                f"Safety Alert: {safety_decision.human_reason} "
                f"THUNAI has locked dosage to prevent potentially unsafe or inconsistent application. "
                f"This case has been escalated to an agronomist for review."
            ),
            farmer_message_ta=(
                f"பாதுகாப்பு எச்சரிக்கை: {safety_decision.human_reason_ta} "
                f"தவறான அளவைத் தவிர்க்க மருந்து அளவு பூட்டப்பட்டுள்ளது. "
                f"இது வேளாண்மை வல்லுநரின் ஆய்வுக்கு அனுப்பப்பட்டுள்ளது."
            ),
            escalation_needed=True,
            escalation_reason="Contradictory dosage data across sources.",
            next_step="Await agronomist resolution before spraying.",
        )

    # E. Missing Evidence / Explicit Dose Missing
    if reason_code in (
        ReasonCode.MISSING_EVIDENCE,
        ReasonCode.MISSING_EXPLICIT_DOSE,
        ReasonCode.INVALID_DOSE_VALUE,
        ReasonCode.INCOMPLETE_METADATA,
        ReasonCode.UNVERIFIED_SOURCE,
        ReasonCode.UNVERIFIED_STATUS,
    ):
        return ActionDecision(
            status=ActionStatus.BLOCK_AND_EXPLAIN,
            safety_decision=safety_decision,
            can_recommend_chemical=False,
            can_recommend_dose=False,
            farmer_message=(
                f"Dose Locked: {safety_decision.human_reason} "
                f"THUNAI does not have enough verified institutional evidence to safely provide a dosage. "
                f"No dosage will be invented."
            ),
            farmer_message_ta=(
                f"மருந்து அளவு பூட்டப்பட்டது: {safety_decision.human_reason_ta} "
                f"துணை தளத்தில் போதுமான சரிபார்க்கப்பட்ட அரசு ஆதாரங்கள் இல்லாததால் மருந்து அளவு வழங்கப்படாது. "
                f"யூகம் சார்ந்த அளவுகள் வழங்கப்பட மாட்டாது."
            ),
            escalation_needed=True,
            escalation_reason="Missing verified evidence or dosage.",
            next_step="Refer to TNAU AgriTech Portal or visit local agriculture office.",
        )

    # F. Cross-Crop Leakage & Evidence Mismatches
    if reason_code in (
        ReasonCode.CROSS_CROP_LEAKAGE,
        ReasonCode.CROP_MISMATCH,
        ReasonCode.PROBLEM_MISMATCH,
        ReasonCode.CHEMICAL_MISMATCH,
    ):
        return ActionDecision(
            status=ActionStatus.BLOCK_AND_EXPLAIN,
            safety_decision=safety_decision,
            can_recommend_chemical=False,
            can_recommend_dose=False,
            farmer_message=(
                f"Context Isolation Block: {safety_decision.human_reason} "
                f"Pesticide dosage from one crop or problem can never be applied to another."
            ),
            farmer_message_ta=(
                f"பயிர் பாதுகாப்பு கட்டுப்பாடு: {safety_decision.human_reason_ta} "
                f"ஒரு பயிருக்கான மருந்து அளவை மற்றொரு பயிருக்கு ஒருபோதும் பயன்படுத்தக் கூடாது."
            ),
            escalation_needed=False,
            next_step="Ensure recommendations are strictly matched to the intended crop.",
        )

    # G. Prompt Injection Detected
    if reason_code == ReasonCode.PROMPT_INJECTION_DETECTED:
        return ActionDecision(
            status=ActionStatus.BLOCK_AND_EXPLAIN,
            safety_decision=safety_decision,
            can_recommend_chemical=False,
            can_recommend_dose=False,
            farmer_message=(
                "Security Alert: Safety bypass attempt detected. "
                "THUNAI operates strictly on verified agricultural safety rules. Dose lock remains engaged."
            ),
            farmer_message_ta=(
                "பாதுகாப்பு எச்சரிக்கை: பாதுகாப்பு விதிகளை மீறும் முயற்சி கண்டறியப்பட்டது. "
                "துணை எப்போதும் சரிபார்க்கப்பட்ட வேளாண் பாதுகாப்பு விதிகளின்படியே செயல்படும்."
            ),
            escalation_needed=False,
            next_step="Submit a valid agricultural query.",
        )

    # Fallback Default: Block and explain
    return ActionDecision(
        status=ActionStatus.BLOCK_AND_EXPLAIN,
        safety_decision=safety_decision,
        can_recommend_chemical=False,
        can_recommend_dose=False,
        farmer_message=f"Dose Locked: {safety_decision.human_reason}",
        farmer_message_ta=f"மருந்து அளவு பூட்டப்பட்டது: {safety_decision.human_reason_ta or ''}",
        escalation_needed=False,
        next_step="Consult an agricultural expert.",
    )
