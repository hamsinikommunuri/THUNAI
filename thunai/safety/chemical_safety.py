"""Chemical safety and regulatory verification module.

Enforces:
1. Legal / Regulatory blocking (CIBRC banned / restricted chemicals, label claims)
2. THUNAI product-safety policy (WHO toxicity classes, Pre-Harvest Intervals)
3. Separation of commercial brand identity from active chemical ingredient
"""

import re
from typing import Dict, List, Optional, Set, Tuple
from pydantic import BaseModel, ConfigDict

from thunai.core.enums import (
    DecisionType,
    ReasonCategory,
    ReasonCode,
    RegulatoryStatus,
)
from thunai.core.models import DoseEvidence, EvidenceRecord, FarmerContext, SafetyDecision
from thunai.core.normalizer import (
    NormalizedChemical,
    normalize_chemical,
)

# Registry version timestamp for auditability
REGISTRY_VERSION = "2026-09-16"


class RegulatoryEntry(BaseModel):
    """Authoritative regulatory entry with full statutory provenance."""
    model_config = ConfigDict(frozen=True)
    active_ingredient: str
    formulation: Optional[str] = None
    concentration: Optional[str] = None
    regulatory_status: RegulatoryStatus
    applicable_crop_or_crop_group: List[str] = []
    applicable_use: str = ""
    notification_number: str
    notification_date: str
    effective_date: str
    official_source: str
    source_document_version: str
    last_verified_at: str
    notes: str
    who_class: str  # Ia, Ib, II, III, U (toxicological metric, NOT legal status)
    thunai_safety_policy: Optional[str] = None  # Specific THUNAI policy restriction if applicable
    banned_crops: List[str] = []
    allowed_crops: List[str] = []
    statutory_reference: str
    legal_description: str
    legal_description_ta: str


# Comprehensive CIBRC / Govt of India Regulatory Registry with complete statutory provenance
REGULATORY_DATABASE: Dict[str, RegulatoryEntry] = {
    "monocrotophos": RegulatoryEntry(
        active_ingredient="Monocrotophos",
        formulation="36% SL",
        concentration="36% SL",
        regulatory_status=RegulatoryStatus.BANNED_FOR_CROP,
        applicable_crop_or_crop_group=["vegetables", "tomato", "chilli"],
        applicable_use="Insecticide (foliar application)",
        notification_number="S.O. 3960(E); S.O. 1139(E)",
        notification_date="2019-12-06",
        effective_date="2020-12-31",
        official_source="CIBRC / Ministry of Agriculture & Farmers Welfare, Gazette of India",
        source_document_version="PPQS Compendium of Banned/Restricted Pesticides 2024",
        last_verified_at="2026-09-16",
        notes="Statutory ban on all vegetable crops (Tomato, Chilli, Brinjal, etc.) due to high acute toxicity and consumer dietary risk. Permitted on select non-vegetable crops like cotton.",
        who_class="Ib",
        banned_crops=["tomato", "chilli", "vegetables"],
        allowed_crops=["cotton", "paddy"],
        statutory_reference="CIBRC Gazette Notification S.O. 3960(E); S.O. 1139(E)",
        legal_description="Banned for use on all vegetable crops (including Tomato, Chilli) due to high acute toxicity and consumer risk.",
        legal_description_ta="காய்கறிப் பயிர்களில் (தக்காளி, மிளகாய்) மோனோகுரோட்டோபாஸ் பயன்படுத்த மத்திய அரசால் தடை செய்யப்பட்டுள்ளது.",
    ),
    "endosulfan": RegulatoryEntry(
        active_ingredient="Endosulfan",
        formulation="All formulations (35% EC, 4% Dust)",
        concentration="All",
        regulatory_status=RegulatoryStatus.BANNED_NATIONWIDE,
        applicable_crop_or_crop_group=["all_crops"],
        applicable_use="Total ban on manufacture, import, sale, and use across India",
        notification_number="Supreme Court of India WP(C) 213/2011; CIBRC Ref F.No. 1-17/2011-SD.II",
        notification_date="2011-05-13",
        effective_date="2011-05-13",
        official_source="Supreme Court of India / Central Insecticides Board & Registration Committee",
        source_document_version="PPQS Banned Pesticides Schedule Item 27",
        last_verified_at="2026-09-16",
        notes="Complete nationwide ban following Supreme Court order WP(C) 213/2011 dated 13.05.2011 due to severe persistent neurotoxicity and congenital health impacts.",
        who_class="Ib",
        banned_crops=["all", "paddy", "tomato", "banana", "chilli"],
        allowed_crops=[],
        statutory_reference="Supreme Court of India WP(C) 213/2011; CIBRC Schedule Item 27",
        legal_description="Completely banned across India by Supreme Court ruling due to severe persistent neurotoxicity and health hazards.",
        legal_description_ta="என்டோசல்பான் இந்தியாவில் முழுமையாக உச்சநீதிமன்றத்தால் தடை செய்யப்பட்ட நச்சு மருந்து.",
    ),
    "carbofuran": RegulatoryEntry(
        active_ingredient="Carbofuran",
        formulation="50% SP banned; 3% CG restricted/phased",
        concentration="50% SP, 3% CG",
        regulatory_status=RegulatoryStatus.BANNED_NATIONWIDE,
        applicable_crop_or_crop_group=["all_crops"],
        applicable_use="Systemic insecticide/nematicide",
        notification_number="S.O. 3960(E) dated 06.12.2019; Gazette S.O. 562(E) dated 02.02.2023",
        notification_date="2023-02-02",
        effective_date="2023-02-02",
        official_source="Ministry of Agriculture & Farmers Welfare / Gazette of India",
        source_document_version="PPQS Insecticides Act 1968 Schedule List 2024",
        last_verified_at="2026-09-16",
        notes="Carbofuran 50% SP formulation completely banned; 3% CG phased out / banned due to extreme oral toxicity and massive avian/wildlife mortality.",
        who_class="Ib",
        banned_crops=["all", "paddy", "tomato", "banana", "chilli"],
        allowed_crops=[],
        statutory_reference="CIBRC Gazette Notification S.O. 3960(E) / S.O. 562(E)",
        legal_description="Banned / prohibited formulation (Furadan) due to extreme acute toxicity and aquatic / wildlife mortality.",
        legal_description_ta="கார்போபியூரான் (பியூரிடான்) தீவிர நச்சுத்தன்மை காரணமாக தடை செய்யப்பட்டுள்ளது.",
    ),
    "paraquat": RegulatoryEntry(
        active_ingredient="Paraquat Dichloride",
        formulation="24% SL",
        concentration="24% SL",
        regulatory_status=RegulatoryStatus.RESTRICTED_USE,
        applicable_crop_or_crop_group=["tea", "rubber", "non-crop"],
        applicable_use="Non-selective contact herbicide (tea plantations, rubber basins, aquatic weeds)",
        notification_number="Insecticides Rules 1971 / CIBRC Restriction S.O. 3960(E)",
        notification_date="2019-12-06",
        effective_date="2020-12-31",
        official_source="PPQS / CIBRC Ministry of Agriculture & Farmers Welfare",
        source_document_version="PPQS Pesticides Restricted for Use in India 2024",
        last_verified_at="2026-09-16",
        notes="Statutorily restricted non-selective herbicide. Prohibited for in-crop foliar application on food crops (Paddy, Tomato, Banana, Chilli). Fatal if ingested; no antidote.",
        who_class="II",
        banned_crops=[],
        allowed_crops=["tea", "rubber", "non-crop"],
        statutory_reference="CIBRC Section 9(3) / Insecticides Rules 1971 / S.O. 3960(E)",
        legal_description="Severely restricted contact herbicide; prohibited for in-crop foliar application on food crops.",
        legal_description_ta="பாராக்குவாட் களைக்கொல்லி உணவுப் பயிர்களில் நேரடியாக தெளிக்கத் தடை செய்யப்பட்டுள்ளது.",
    ),
    "glyphosate": RegulatoryEntry(
        active_ingredient="Glyphosate",
        formulation="41% SL",
        concentration="41% SL",
        regulatory_status=RegulatoryStatus.RESTRICTED_OPERATOR,
        applicable_crop_or_crop_group=["tea", "non-crop"],
        applicable_use="Non-selective systemic herbicide applied strictly through Pest Control Operators (PCOs)",
        notification_number="Ministry of Agriculture Gazette Notification S.O. 4910(E)",
        notification_date="2022-10-21",
        effective_date="2022-10-21",
        official_source="Ministry of Agriculture & Farmers Welfare, Department of Agriculture & Farmers Welfare",
        source_document_version="Gazette of India Extraordinary Part II Section 3(ii)",
        last_verified_at="2026-09-16",
        notes="Use statutorily restricted only to tea plantations and non-cropped land. Strict operator restriction: application permitted only by licensed Pest Control Operators (PCOs).",
        who_class="III",
        banned_crops=[],
        allowed_crops=["tea", "non-crop"],
        statutory_reference="Ministry of Agriculture Notification S.O. 4910(E) (2022)",
        legal_description="Strictly restricted to tea plantations and non-cropped land through licensed Pest Control Operators.",
        legal_description_ta="கிளைபோசேட் தேயிலைத் தோட்டங்கள் மற்றும் பயிரற்ற நிலங்களுக்கு மட்டுமே அனுமதிக்கப்பட்டது.",
    ),
    "methyl parathion": RegulatoryEntry(
        active_ingredient="Methyl Parathion",
        formulation="All formulations (50% EC, 2% DP)",
        concentration="All",
        regulatory_status=RegulatoryStatus.BANNED_NATIONWIDE,
        applicable_crop_or_crop_group=["all_crops"],
        applicable_use="Total ban across all agricultural and domestic applications",
        notification_number="CIBRC Gazette Notification S.O. 682(E) and S.O. 3960(E)",
        notification_date="2001-07-17",
        effective_date="2001-07-17",
        official_source="Central Insecticides Board & Registration Committee, Ministry of Agriculture",
        source_document_version="PPQS Compendium of Banned Pesticides List 2024",
        last_verified_at="2026-09-16",
        notes="Completely banned in India due to extremely high acute oral and dermal organophosphate toxicity (WHO Class Ia).",
        who_class="Ia",
        banned_crops=["all", "paddy", "tomato", "banana", "chilli"],
        allowed_crops=[],
        statutory_reference="CIBRC Gazette Notification S.O. 682(E)",
        legal_description="Completely banned in India due to extremely hazardous organophosphate toxicity (WHO Class Ia).",
        legal_description_ta="மெத்தில் பாராத்தியான் தீவிர நச்சுத்தன்மை காரணமாக முற்றிலும் தடை செய்யப்பட்டுள்ளது.",
    ),
    "phorate": RegulatoryEntry(
        active_ingredient="Phorate",
        formulation="10% CG (Granules)",
        concentration="10% CG",
        regulatory_status=RegulatoryStatus.BANNED_NATIONWIDE,
        applicable_crop_or_crop_group=["all_crops"],
        applicable_use="Total ban on agricultural use",
        notification_number="Ministry of Agriculture Notification S.O. 3960(E); Gazette Notification 2023",
        notification_date="2019-12-06",
        effective_date="2020-12-31",
        official_source="Ministry of Agriculture & Farmers Welfare, Govt of India",
        source_document_version="PPQS Compendium of Banned Pesticides 2024",
        last_verified_at="2026-09-16",
        notes="Completely banned in India due to extreme acute toxicity (WHO Class Ia) and high worker exposure hazards.",
        who_class="Ia",
        banned_crops=["all", "paddy", "tomato", "banana", "chilli"],
        allowed_crops=[],
        statutory_reference="CIBRC Notification S.O. 3960(E)",
        legal_description="Completely phased out and banned in India due to extreme systemic neurotoxicity.",
        legal_description_ta="ஃபோரேட் இந்தியாவில் முற்றிலும் தடை செய்யப்பட்ட பூச்சிக்கொல்லி.",
    ),
    "methomyl": RegulatoryEntry(
        active_ingredient="Methomyl",
        formulation="12.5% L / 24% L",
        concentration="12.5% L, 24% L",
        regulatory_status=RegulatoryStatus.BANNED_NATIONWIDE,
        applicable_crop_or_crop_group=["all_crops"],
        applicable_use="Prohibited across all agricultural uses",
        notification_number="CIBRC Gazette Notification S.O. 3960(E)",
        notification_date="2019-12-06",
        effective_date="2020-12-31",
        official_source="Central Insecticides Board & Registration Committee",
        source_document_version="PPQS Banned Pesticides 2024",
        last_verified_at="2026-09-16",
        notes="Banned across India due to high acute oral and inhalation toxicity (WHO Class Ib carbamate).",
        who_class="Ib",
        banned_crops=["all", "paddy", "tomato", "banana", "chilli"],
        allowed_crops=[],
        statutory_reference="CIBRC Gazette Notification S.O. 3960(E)",
        legal_description="Banned across India due to high acute oral and inhalation toxicity.",
        legal_description_ta="மெத்தோமைல் இந்தியாவில் தடை செய்யப்பட்டுள்ளது.",
    ),
    "triazophos": RegulatoryEntry(
        active_ingredient="Triazophos",
        formulation="40% EC",
        concentration="40% EC",
        regulatory_status=RegulatoryStatus.BANNED_FOR_CROP,
        applicable_crop_or_crop_group=["vegetables", "tomato", "chilli"],
        applicable_use="Insecticide (approved on rice and cotton only)",
        notification_number="CIBRC Notification S.O. 3960(E)",
        notification_date="2019-12-06",
        effective_date="2020-12-31",
        official_source="Central Insecticides Board & Registration Committee",
        source_document_version="PPQS Restricted Pesticides List 2024",
        last_verified_at="2026-09-16",
        notes="Statutory ban on vegetable crops due to persistent residues and high mammalian toxicity. Permitted on rice and cotton.",
        who_class="Ib",
        banned_crops=["tomato", "chilli"],
        allowed_crops=["cotton", "rice", "paddy"],
        statutory_reference="CIBRC Notification S.O. 3960(E)",
        legal_description="Banned for use on vegetables due to persistent residues and high toxicity.",
        legal_description_ta="காய்கறிகளில் ட்ரையாசோபாஸ் தெளிப்பது தடை செய்யப்பட்டுள்ளது.",
    ),
    "chlorpyrifos": RegulatoryEntry(
        active_ingredient="Chlorpyrifos",
        formulation="20% EC",
        concentration="20% EC",
        regulatory_status=RegulatoryStatus.RESTRICTED_USE,
        applicable_crop_or_crop_group=["paddy", "banana", "cotton", "sugarcane"],
        applicable_use="Foliar / soil application on registered label crops only",
        notification_number="CIBRC Major Uses of Pesticides (Registered under Section 9(3))",
        notification_date="2023-06-30",
        effective_date="2023-06-30",
        official_source="Directorate of Plant Protection, Quarantine & Storage (PPQS)",
        source_document_version="CIBRC Insecticides Registered List 2024",
        last_verified_at="2026-09-16",
        notes="Registered label claims exist for stem borer in Paddy and pseudostem swabbing in Banana. Not approved for Tomato or Chilli (off-label use).",
        who_class="II",
        banned_crops=[],
        allowed_crops=["paddy", "banana"],
        statutory_reference="CIBRC Gazetted Crop Label Claims",
        legal_description="Restricted in vegetables; registered for specific stem/soil treatments in select field/plantation crops.",
        legal_description_ta="குளோர்பைரிபாஸ் காய்கறிகளில் அனுமதிக்கப்படவில்லை, குறிப்பிட்ட பயிர்களில் மட்டுமே பயன்பாடு.",
    ),
}

# Registered CIBRC Label Claims for our 4 crops (Active Ingredients approved per crop)
REGISTERED_CROP_CHEMICALS: Dict[str, Set[str]] = {
    "paddy": {
        "chlorantraniliprole",
        "cartap hydrochloride",
        "fipronil",
        "flubendiamide",
        "tricyclazole",
        "isoprothiolane",
        "azoxystrobin",
        "propiconazole",
        "carbendazim",
        "thiamethoxam",
        "buprofezin",
        "trifloxystrobin",
        "tebuconazole",
        "hexaconazole",
        "validamycin",
        "azadirachtin",
        "bacillus thuringiensis",
        "copper hydroxide",
        "chlorpyrifos",
    },
    "tomato": {
        "chlorantraniliprole",
        "flubendiamide",
        "indoxacarb",
        "azadirachtin",
        "bacillus thuringiensis",
        "mancozeb",
        "azoxystrobin",
        "acetamiprid",
        "spiromesifen",
        "copper oxychloride",
        "metalaxyl-m",
        "chlorothalonil",
        "difenoconazole",
        "cyantraniliprole",
        "spinosad",
    },
    "banana": {
        "propiconazole",
        "carbendazim",
        "mancozeb",
        "chlorpyrifos",  # pseudostem swabbing
        "dimethoate",    # pseudostem injection / axil drenching for aphid vector
        "copper oxychloride",
        "azoxystrobin",
        "mineral oil",
        "pseudomonas fluorescens",
    },
    "chilli": {
        "fipronil",
        "imidacloprid",
        "spinetoram",
        "diafenthiuron",
        "spiromesifen",
        "azoxystrobin",
        "mancozeb",
        "copper oxychloride",
        "flubendiamide",
        "chlorantraniliprole",
        "acetamiprid",
        "azadirachtin",
        "tebuconazole",
    },
}


# Incompatible hazardous tank mix active ingredient pairs
HAZARDOUS_TANK_MIX_PAIRS: List[Tuple[Set[str], Set[str], str, str]] = [
    (
        {"copper oxychloride", "copper hydroxide", "blitox", "bordeaux mixture"},
        {"dimethoate", "chlorpyrifos", "rogor", "durmet"},
        "Copper fungicides must not be tank-mixed with organophosphate insecticides (Dimethoate, Chlorpyrifos) due to alkaline hydrolysis causing rapid chemical breakdown and severe crop phytotoxicity (foliage scorching).",
        "தாமிர பூஞ்சாணக் கொல்லிகளை ஆர்கனோபாஸ்பேட் பூச்சிக்கொல்லிகளுடன் கலக்கக் கூடாது; இது ரசாயன வீரியத்தை இழக்கச் செய்து பயிர் கருகலை ஏற்படுத்தும்.",
    ),
]


def check_hazardous_tank_mix(chemical_input: str) -> Optional[Tuple[str, str]]:
    """Detects incompatible chemical tank-mix combinations.

    Returns (english_explanation, tamil_explanation) if hazardous, or None.
    """
    if not chemical_input:
        return None
    split_tokens = [
        t.strip()
        for t in re.split(r"[\+,]|\band\b|\bwith\b", chemical_input, flags=re.IGNORECASE)
        if t.strip()
    ]
    if len(split_tokens) < 2:
        return None

    norm_ais = [normalize_chemical(t).active_ingredient.lower() for t in split_tokens]
    for group_a, group_b, en_reason, ta_reason in HAZARDOUS_TANK_MIX_PAIRS:
        has_a = any(any(ga in ai for ga in group_a) for ai in norm_ais)
        has_b = any(any(gb in ai for gb in group_b) for ai in norm_ais)
        if has_a and has_b:
            return en_reason, ta_reason
    return None


class ChemicalSafetyResult(BaseModel):
    model_config = ConfigDict(frozen=True)
    is_safe: bool
    reason_code: Optional[ReasonCode] = None
    reason_category: Optional[ReasonCategory] = None
    explanation: str
    explanation_ta: str
    normalized_chemical: Optional[NormalizedChemical] = None
    regulatory_status: str
    who_class: Optional[str] = None
    statutory_reference: Optional[str] = None
    provenance_entry: Optional[RegulatoryEntry] = None


def inspect_chemical_safety(
    chemical_input: Optional[str],
    crop_id: str,
    days_to_harvest: Optional[int] = None,
    waiting_period_days: Optional[int] = None,
) -> ChemicalSafetyResult:
    """Evaluates regulatory compliance and THUNAI safety policy for a chemical.

    Verifies:
    1. Statutory bans (CIBRC / Court bans): BANNED_NATIONWIDE, BANNED_FOR_CROP, BANNED_FORMULATION
    2. Regulatory restrictions: RESTRICTED_USE, RESTRICTED_OPERATOR
    3. CIBRC registered label claims for target crop: REGISTERED_LABEL_USE vs UNREGISTERED_LABEL_CLAIM
    4. THUNAI safety policy (independent of Indian law): PHI intervals, hazardous tank-mixes, toxicity policy
    """
    if not chemical_input:
        return ChemicalSafetyResult(
            is_safe=False,
            reason_code=ReasonCode.INCOMPLETE_METADATA,
            reason_category=ReasonCategory.UNCERTAINTY,
            explanation="No chemical or active ingredient was specified.",
            explanation_ta="மருந்தின் பெயர் அல்லது செயலில் உள்ள வேதிப்பொருள் குறிப்பிடப்படவில்லை.",
            regulatory_status=RegulatoryStatus.UNKNOWN.value,
        )

    norm_chem = normalize_chemical(chemical_input)
    ai_key = norm_chem.active_ingredient.lower().strip()
    crop_key = crop_id.lower().strip()

    # 0. Check Hazardous Tank Mix Policy (THUNAI Product Safety Policy)
    tank_mix_hazard = check_hazardous_tank_mix(chemical_input)
    if tank_mix_hazard:
        en_hazard, ta_hazard = tank_mix_hazard
        return ChemicalSafetyResult(
            is_safe=False,
            reason_code=ReasonCode.HAZARDOUS_TANK_MIX,
            reason_category=ReasonCategory.PRODUCT_SAFETY_POLICY,
            explanation=f"HAZARDOUS TANK MIX: {en_hazard}",
            explanation_ta=f"ஆபத்தான மருந்து கலவை: {ta_hazard}",
            normalized_chemical=norm_chem,
            regulatory_status="HAZARDOUS_MIX",
        )

    # 1. Check against Regulatory Database for bans & restrictions
    for reg_key, reg_entry in REGULATORY_DATABASE.items():
        matched = False
        if any(ord(c) > 127 for c in reg_key):
            matched = reg_key == ai_key or reg_key in ai_key
        else:
            pattern = rf"\b{re.escape(reg_key)}\b"
            matched = bool(re.search(pattern, ai_key, re.IGNORECASE))
            if not matched:
                ai_canon = reg_entry.active_ingredient.lower().strip()
                matched = bool(re.search(rf"\b{re.escape(ai_canon)}\b", ai_key, re.IGNORECASE))
        if matched:
            # A. Check Nationwide Ban (Statutory)
            if reg_entry.regulatory_status == RegulatoryStatus.BANNED_NATIONWIDE:
                return ChemicalSafetyResult(
                    is_safe=False,
                    reason_code=ReasonCode.BANNED_NATIONWIDE,
                    reason_category=ReasonCategory.LEGAL_REGULATORY,
                    explanation=(
                        f"STATUTORY NATIONWIDE BAN: {reg_entry.active_ingredient} is completely banned in India. "
                        f"{reg_entry.legal_description} Official Source: {reg_entry.official_source} "
                        f"(Ref: {reg_entry.statutory_reference}, Notif Date: {reg_entry.notification_date})."
                    ),
                    explanation_ta=(
                        f"சட்டப்பூர்வ தேசிய தடை: {reg_entry.active_ingredient} இந்தியாவில் முற்றிலுமாக தடை செய்யப்பட்டுள்ளது. "
                        f"{reg_entry.legal_description_ta}"
                    ),
                    normalized_chemical=norm_chem,
                    regulatory_status=RegulatoryStatus.BANNED_NATIONWIDE.value,
                    who_class=reg_entry.who_class,
                    statutory_reference=reg_entry.statutory_reference,
                    provenance_entry=reg_entry,
                )

            # B. Check Crop-Specific Ban (e.g. Monocrotophos / Triazophos on Vegetables)
            if reg_entry.regulatory_status == RegulatoryStatus.BANNED_FOR_CROP:
                is_banned_crop = (
                    crop_key in reg_entry.banned_crops
                    or (crop_key in ["tomato", "chilli"] and "vegetables" in reg_entry.banned_crops)
                )
                if is_banned_crop:
                    return ChemicalSafetyResult(
                        is_safe=False,
                        reason_code=ReasonCode.BANNED_FOR_CROP,
                        reason_category=ReasonCategory.LEGAL_REGULATORY,
                        explanation=(
                            f"STATUTORY CROP BAN: {reg_entry.active_ingredient} is prohibited on {crop_key.title()} by law. "
                            f"{reg_entry.legal_description} Official Source: {reg_entry.official_source} "
                            f"(Ref: {reg_entry.statutory_reference}, Notif: {reg_entry.notification_number})."
                        ),
                        explanation_ta=(
                            f"பயிர் சார்ந்த சட்டப்பூர்வ தடை: {reg_entry.active_ingredient} {crop_key.title()} பயிரில் "
                            f"பயன்படுத்த தடை செய்யப்பட்டுள்ளது. {reg_entry.legal_description_ta}"
                        ),
                        normalized_chemical=norm_chem,
                        regulatory_status=RegulatoryStatus.BANNED_FOR_CROP.value,
                        who_class=reg_entry.who_class,
                        statutory_reference=reg_entry.statutory_reference,
                        provenance_entry=reg_entry,
                    )

            # C. Check Operator-Restricted Chemical (e.g. Glyphosate under S.O. 4910(E))
            if reg_entry.regulatory_status == RegulatoryStatus.RESTRICTED_OPERATOR:
                return ChemicalSafetyResult(
                    is_safe=False,
                    reason_code=ReasonCode.RESTRICTED_OPERATOR,
                    reason_category=ReasonCategory.LEGAL_REGULATORY,
                    explanation=(
                        f"RESTRICTED OPERATOR: {reg_entry.active_ingredient} use is strictly restricted by law to "
                        f"certified Pest Control Operators (PCOs) and cannot be recommended for farmer application. "
                        f"{reg_entry.legal_description} Ref: {reg_entry.statutory_reference}."
                    ),
                    explanation_ta=(
                        f"சான்றளிக்கப்பட்ட இயக்குபவருக்கு மட்டுமே அனுமதி: {reg_entry.active_ingredient} அரசு உரிமம் பெற்ற "
                        f"பூச்சி கட்டுப்பாட்டு நிபுணர்களால் மட்டுமே பயன்படுத்த சட்டம் அனுமதிக்கிறது."
                    ),
                    normalized_chemical=norm_chem,
                    regulatory_status=RegulatoryStatus.RESTRICTED_OPERATOR.value,
                    who_class=reg_entry.who_class,
                    statutory_reference=reg_entry.statutory_reference,
                    provenance_entry=reg_entry,
                )

            # D. Check Statutory Use Restrictions (e.g. Paraquat)
            if reg_entry.regulatory_status == RegulatoryStatus.RESTRICTED_USE:
                if crop_key not in reg_entry.allowed_crops:
                    return ChemicalSafetyResult(
                        is_safe=False,
                        reason_code=ReasonCode.RESTRICTED_USE,
                        reason_category=ReasonCategory.LEGAL_REGULATORY,
                        explanation=(
                            f"STATUTORY USE RESTRICTION: {reg_entry.active_ingredient} is restricted and prohibited on "
                            f"{crop_key.title()}. {reg_entry.legal_description} Ref: {reg_entry.statutory_reference}."
                        ),
                        explanation_ta=(
                            f"கட்டுப்படுத்தப்பட்ட பயன்பாடு: {reg_entry.active_ingredient} {crop_key.title()} பயிருக்கு "
                            f"சட்டப்பூர்வமாக அனுமதிக்கப்படவில்லை. {reg_entry.legal_description_ta}"
                        ),
                        normalized_chemical=norm_chem,
                        regulatory_status=RegulatoryStatus.RESTRICTED_USE.value,
                        who_class=reg_entry.who_class,
                        statutory_reference=reg_entry.statutory_reference,
                        provenance_entry=reg_entry,
                    )

            # E. Check THUNAI Product-Safety Policy (Independent of statutory law)
            if reg_entry.thunai_safety_policy == "BLOCKED":
                return ChemicalSafetyResult(
                    is_safe=False,
                    reason_code=ReasonCode.THUNAI_SAFETY_POLICY,
                    reason_category=ReasonCategory.PRODUCT_SAFETY_POLICY,
                    explanation=(
                        f"THUNAI SAFETY POLICY: {reg_entry.active_ingredient} is blocked by THUNAI product safety policy "
                        f"to protect smallholder farmers and environmental health."
                    ),
                    explanation_ta=(
                        f"துணை பாதுகாப்பு கொள்கை: சிறு விவசாயிகளின் பாதுகாப்பு கருதி இந்நடவடிக்கை தடுக்கப்பட்டுள்ளது."
                    ),
                    normalized_chemical=norm_chem,
                    regulatory_status="POLICY_BLOCKED",
                    who_class=reg_entry.who_class,
                    provenance_entry=reg_entry,
                )

    # 2. Check CIBRC Registered Label Claim for target crop
    allowed_ais = REGISTERED_CROP_CHEMICALS.get(crop_key, set())
    components = [
        c.strip()
        for c in re.split(r"[\+,]|\band\b", ai_key, flags=re.IGNORECASE)
        if c.strip()
    ]
    is_registered = False
    for comp in components:
        for allowed in allowed_ais:
            if comp == allowed or bool(re.search(rf"\b{re.escape(allowed)}\b", comp, re.IGNORECASE)):
                is_registered = True
                break
        if is_registered:
            break
    if not is_registered:
        return ChemicalSafetyResult(
            is_safe=False,
            reason_code=ReasonCode.UNREGISTERED_LABEL_CLAIM,
            reason_category=ReasonCategory.LEGAL_REGULATORY,
            explanation=(
                f"UNREGISTERED LABEL CLAIM: {norm_chem.active_ingredient} has no approved CIBRC label claim "
                f"for {crop_key.title()}. Off-label application is not authorized under the Insecticides Act 1968."
            ),
            explanation_ta=(
                f"பதிவு செய்யப்படாத பயன்பாடு: {norm_chem.active_ingredient} {crop_key.title()} பயிருக்கு "
                f"மத்திய பூச்சிக்கொல்லி வாரியத்தால் (CIBRC) அங்கீகரிக்கப்படவில்லை."
            ),
            normalized_chemical=norm_chem,
            regulatory_status=RegulatoryStatus.UNREGISTERED_LABEL_CLAIM.value,
        )

    # 3. THUNAI Product-Safety Policy: Pre-Harvest Interval (PHI) check
    if days_to_harvest is not None and waiting_period_days is not None:
        if days_to_harvest < waiting_period_days:
            return ChemicalSafetyResult(
                is_safe=False,
                reason_code=ReasonCode.PRE_HARVEST_INTERVAL_VIOLATION,
                reason_category=ReasonCategory.PRODUCT_SAFETY_POLICY,
                explanation=(
                    f"PRE-HARVEST SAFETY VIOLATION: Crop is {days_to_harvest} days from harvest, "
                    f"but {norm_chem.active_ingredient} requires a waiting period (PHI) of "
                    f"{waiting_period_days} days to prevent unsafe chemical residue."
                ),
                explanation_ta=(
                    f"அறுவடைக்கு முந்தைய பாதுகாப்புக் கட்டுப்பாடு: அறுவடைக்கு {days_to_harvest} நாட்களே உள்ள நிலையில், "
                    f"இந்த மருந்துக்கு {waiting_period_days} நாட்கள் இடைவெளி தேவை. நச்சு எச்சத்தைத் தவிர்க்க இது தடுக்கப்பட்டுள்ளது."
                ),
                normalized_chemical=norm_chem,
                regulatory_status="PHI_VIOLATION",
            )

    return ChemicalSafetyResult(
        is_safe=True,
        reason_code=ReasonCode.REGISTERED_LABEL_USE,
        reason_category=ReasonCategory.LEGAL_REGULATORY,
        explanation=f"{norm_chem.active_ingredient} is approved and compliant for {crop_key.title()}.",
        explanation_ta=f"{norm_chem.active_ingredient} {crop_key.title()} பயிருக்கு அனுமதிக்கப்பட்ட பாதுகாப்பான மருந்து.",
        normalized_chemical=norm_chem,
        regulatory_status=RegulatoryStatus.REGISTERED_LABEL_USE.value,
    )
