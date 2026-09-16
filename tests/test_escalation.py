"""Unit tests for escalation and operational action decisions."""

import pytest
from thunai.core.enums import ActionStatus, DecisionType, ReasonCategory, ReasonCode
from thunai.core.models import EvidenceRecord, FarmerContext, SafetyDecision
from thunai.safety.escalation import build_action_decision


class TestEscalation:
    def test_allow_action_decision(self, verified_tomato_fruit_borer: EvidenceRecord):
        dose = verified_tomato_fruit_borer.to_dose_evidence()
        safety_dec = SafetyDecision(
            decision=DecisionType.ALLOW,
            reason_code=ReasonCode.VERIFIED_AND_ALLOWED,
            reason_category=ReasonCategory.VALID_VERIFIED,
            human_reason="Verified recommendation allowed.",
            allowed_dose=dose,
        )
        ctx = FarmerContext(crop="Tomato", target_problem="Fruit Borer")
        action = build_action_decision(safety_dec, ctx)

        assert action.status == ActionStatus.ALLOW_RECOMMENDATION
        assert action.can_recommend_chemical is True
        assert action.can_recommend_dose is True
        assert action.escalation_needed is False
        assert "0.3 ml/l" in action.farmer_message
        assert action.farmer_message_ta is not None
        assert "0.3 ml/l" in action.farmer_message_ta

    def test_banned_chemical_action_decision(self):
        safety_dec = SafetyDecision(
            decision=DecisionType.BLOCK,
            reason_code=ReasonCode.BANNED_FOR_CROP,
            reason_category=ReasonCategory.LEGAL_REGULATORY,
            human_reason="Monocrotophos is banned on vegetables.",
            human_reason_ta="காய்கறிப் பயிர்களில் மோனோகுரோட்டோபாஸ் தடை செய்யப்பட்டுள்ளது.",
        )
        ctx = FarmerContext(crop="Tomato", target_problem="Fruit Borer", requested_chemical="Monocil")
        action = build_action_decision(safety_dec, ctx)

        assert action.status == ActionStatus.BLOCK_AND_EXPLAIN
        assert action.can_recommend_chemical is False
        assert action.can_recommend_dose is False
        assert action.escalation_needed is True
        assert "banned" in action.farmer_message.lower()

    def test_clarification_action_decision(self):
        safety_dec = SafetyDecision(
            decision=DecisionType.BLOCK,
            reason_code=ReasonCode.AMBIGUOUS_CROP,
            reason_category=ReasonCategory.UNCERTAINTY,
            human_reason="Farmer query does not specify a crop.",
            human_reason_ta="பயிர் குறிப்பிடப்படவில்லை.",
        )
        ctx = FarmerContext(raw_query="give me a spray")
        action = build_action_decision(safety_dec, ctx)

        assert action.status == ActionStatus.REQUEST_CLARIFICATION
        assert action.can_recommend_dose is False
        assert "which crop" in action.farmer_message.lower()

    def test_conflicting_evidence_action_decision(self):
        safety_dec = SafetyDecision(
            decision=DecisionType.BLOCK,
            reason_code=ReasonCode.CONFLICTING_EVIDENCE,
            reason_category=ReasonCategory.UNCERTAINTY,
            human_reason="Divergent dosages in database.",
        )
        ctx = FarmerContext(crop="Tomato", target_problem="Early Blight")
        action = build_action_decision(safety_dec, ctx)

        assert action.status == ActionStatus.ESCALATE_TO_EXPERT
        assert action.can_recommend_dose is False
        assert action.escalation_needed is True

    def test_pre_harvest_interval_violation_action_decision(self):
        safety_dec = SafetyDecision(
            decision=DecisionType.BLOCK,
            reason_code=ReasonCode.PRE_HARVEST_INTERVAL_VIOLATION,
            reason_category=ReasonCategory.PRODUCT_SAFETY_POLICY,
            human_reason="Crop is 2 days from harvest, but waiting period is 7 days.",
            human_reason_ta="அறுவடைக்கு 2 நாட்களே உள்ள நிலையில், இந்த மருந்துக்கு 7 நாட்கள் இடைவெளி தேவை.",
        )
        ctx = FarmerContext(crop="Tomato", target_problem="Fruit Borer", days_to_harvest=2)
        action = build_action_decision(safety_dec, ctx)

        assert action.status == ActionStatus.BLOCK_AND_EXPLAIN
        assert action.can_recommend_chemical is False
        assert action.can_recommend_dose is False
        assert action.escalation_needed is True
        assert "pre-harvest" in action.escalation_reason.lower()
        assert "residue" in action.farmer_message.lower()
        assert action.farmer_message_ta is not None
        assert "நச்சு எச்ச" in action.farmer_message_ta

    def test_hazardous_tank_mix_action_decision(self):
        safety_dec = SafetyDecision(
            decision=DecisionType.BLOCK,
            reason_code=ReasonCode.HAZARDOUS_TANK_MIX,
            reason_category=ReasonCategory.PRODUCT_SAFETY_POLICY,
            human_reason="Copper fungicides must not be mixed with organophosphates.",
            human_reason_ta="தாமிர பூஞ்சாணக் கொல்லிகளை ஆர்கனோபாஸ்பேட் பூச்சிக்கொல்லிகளுடன் கலக்கக் கூடாது.",
        )
        ctx = FarmerContext(crop="Banana", target_problem="Sigatoka Leaf Spot", requested_chemical="Blitox + Rogor")
        action = build_action_decision(safety_dec, ctx)

        assert action.status == ActionStatus.BLOCK_AND_EXPLAIN
        assert action.can_recommend_chemical is False
        assert action.can_recommend_dose is False
        assert action.escalation_needed is True
        assert "tank mix" in action.farmer_message.lower()
        assert "phytotoxicity" in action.farmer_message.lower()
        assert "கருகலை" in action.farmer_message_ta
        assert "கலவை" in action.farmer_message_ta

    def test_allow_action_decision_with_none_formulation(self, verified_tomato_fruit_borer: EvidenceRecord):
        rec_data = verified_tomato_fruit_borer.model_dump()
        rec_data["formulation"] = None
        rec_no_form = EvidenceRecord(**rec_data)
        dose = rec_no_form.to_dose_evidence()

        safety_dec = SafetyDecision(
            decision=DecisionType.ALLOW,
            reason_code=ReasonCode.VERIFIED_AND_ALLOWED,
            reason_category=ReasonCategory.VALID_VERIFIED,
            human_reason="Verified recommendation allowed.",
            allowed_dose=dose,
        )
        ctx = FarmerContext(crop="Tomato", target_problem="Fruit Borer")
        action = build_action_decision(safety_dec, ctx)

        assert action.status == ActionStatus.ALLOW_RECOMMENDATION
        assert "(None)" not in action.farmer_message
        assert "(None)" not in (action.farmer_message_ta or "")
        assert "0.3 ml/l" in action.farmer_message

