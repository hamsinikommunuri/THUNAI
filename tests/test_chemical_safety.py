"""Unit tests for chemical safety and regulatory compliance."""

import pytest
from thunai.core.enums import ReasonCategory, ReasonCode
from thunai.core.normalizer import normalize_chemical
from thunai.safety.chemical_safety import inspect_chemical_safety


class TestChemicalSafety:
    def test_registry_version_and_provenance(self):
        from thunai.safety.chemical_safety import REGISTRY_VERSION, REGULATORY_DATABASE
        assert REGISTRY_VERSION == "2026-09-16"
        for key, entry in REGULATORY_DATABASE.items():
            assert entry.official_source, f"Missing official_source for {key}"
            assert entry.notification_number, f"Missing notification_number for {key}"
            assert entry.last_verified_at == "2026-09-16"
            assert entry.who_class in ("Ia", "Ib", "II", "III", "U")

    def test_monocrotophos_banned_on_vegetables(self):
        # On Tomato -> BANNED_FOR_CROP (Statutory)
        res_tomato = inspect_chemical_safety("Monocrotophos", "tomato")
        assert not res_tomato.is_safe
        assert res_tomato.reason_code == ReasonCode.BANNED_FOR_CROP
        assert res_tomato.reason_category == ReasonCategory.LEGAL_REGULATORY
        assert "S.O." in (res_tomato.statutory_reference or "")
        assert res_tomato.provenance_entry is not None
        assert res_tomato.provenance_entry.notification_number == "S.O. 3960(E); S.O. 1139(E)"

        # On Chilli -> BANNED_FOR_CROP (Statutory)
        res_chilli = inspect_chemical_safety("Monocil", "chilli")
        assert not res_chilli.is_safe
        assert res_chilli.reason_code == ReasonCode.BANNED_FOR_CROP

    def test_endosulfan_completely_banned(self):
        res_paddy = inspect_chemical_safety("Endosulfan", "paddy")
        assert not res_paddy.is_safe
        assert res_paddy.reason_code == ReasonCode.BANNED_NATIONWIDE
        assert "Supreme Court" in res_paddy.explanation
        assert res_paddy.provenance_entry.notification_number == "Supreme Court of India WP(C) 213/2011; CIBRC Ref F.No. 1-17/2011-SD.II"

        res_banana = inspect_chemical_safety("Endosulfan 35% EC", "banana")
        assert not res_banana.is_safe
        assert res_banana.reason_code == ReasonCode.BANNED_NATIONWIDE

    def test_carbofuran_furadan_banned(self):
        res = inspect_chemical_safety("Furadan", "tomato")
        assert not res.is_safe
        assert res.reason_code == ReasonCode.BANNED_NATIONWIDE
        assert res.normalized_chemical.active_ingredient == "Carbofuran"

    def test_glyphosate_restricted_to_non_crop(self):
        res = inspect_chemical_safety("Roundup", "tomato")
        assert not res.is_safe
        assert res.reason_code == ReasonCode.RESTRICTED_OPERATOR
        assert res.reason_category == ReasonCategory.LEGAL_REGULATORY
        assert "S.O. 4910(E)" in (res.statutory_reference or "")

    def test_unregistered_label_claim_rejected(self):
        # Atrazine on tomato
        res = inspect_chemical_safety("Atrazine", "tomato")
        assert not res.is_safe
        assert res.reason_code == ReasonCode.UNREGISTERED_LABEL_CLAIM
        assert res.reason_category == ReasonCategory.LEGAL_REGULATORY

    def test_approved_registered_chemical(self):
        # Coragen (Chlorantraniliprole) on tomato
        res = inspect_chemical_safety("Coragen", "tomato")
        assert res.is_safe
        assert res.regulatory_status == "REGISTERED_LABEL_USE"
        assert res.normalized_chemical.active_ingredient == "Chlorantraniliprole"
        assert res.normalized_chemical.formulation == "SC"

    def test_pre_harvest_interval_violation(self):
        # Waiting period is 7 days, but farmer is harvesting in 2 days
        res = inspect_chemical_safety(
            "Chlorantraniliprole",
            "tomato",
            days_to_harvest=2,
            waiting_period_days=7,
        )
        assert not res.is_safe
        assert res.reason_code == ReasonCode.PRE_HARVEST_INTERVAL_VIOLATION
        assert res.reason_category == ReasonCategory.PRODUCT_SAFETY_POLICY

    @pytest.mark.parametrize(
        "brand,expected_ai,expected_form,expected_conc",
        [
            ("Coragen", "Chlorantraniliprole", "SC", "18.5%"),
            ("Confidor", "Imidacloprid", "SL", "17.8%"),
            ("Tata Mida", "Imidacloprid", "SL", "17.8%"),
            ("Monocil", "Monocrotophos", "SL", "36%"),
            ("Roundup", "Glyphosate", "SL", "41%"),
            ("Beam", "Tricyclazole", "WP", "75%"),
            ("Tilt", "Propiconazole", "EC", "25%"),
            ("Dithane M-45", "Mancozeb", "WP", "75%"),
        ],
    )
    def test_brand_normalization(self, brand, expected_ai, expected_form, expected_conc):
        norm = normalize_chemical(brand)
        assert norm.active_ingredient == expected_ai
        assert norm.formulation == expected_form
        assert norm.concentration == expected_conc

    def test_rate_does_not_falsely_match_phorate(self):
        res = inspect_chemical_safety("rate", "paddy")
        assert not res.is_safe
        assert res.reason_code != ReasonCode.BANNED_CHEMICAL
        assert res.reason_code == ReasonCode.UNREGISTERED_LABEL_CLAIM

    def test_end_does_not_falsely_match_endosulfan(self):
        res = inspect_chemical_safety("end", "paddy")
        assert not res.is_safe
        assert res.reason_code != ReasonCode.BANNED_CHEMICAL
        assert res.reason_code == ReasonCode.UNREGISTERED_LABEL_CLAIM

    def test_para_does_not_falsely_match_paraquat(self):
        res = inspect_chemical_safety("para", "paddy")
        assert not res.is_safe
        assert res.reason_code != ReasonCode.RESTRICTED_CHEMICAL
        assert res.reason_code == ReasonCode.UNREGISTERED_LABEL_CLAIM

    def test_bu_does_not_falsely_match_buprofezin(self):
        res = inspect_chemical_safety("bu", "paddy")
        assert not res.is_safe
        assert res.reason_code == ReasonCode.UNREGISTERED_LABEL_CLAIM
        assert res.regulatory_status == "UNREGISTERED_LABEL_CLAIM"

    def test_pro_does_not_falsely_match_propiconazole(self):
        res = inspect_chemical_safety("pro", "paddy")
        assert not res.is_safe
        assert res.reason_code == ReasonCode.UNREGISTERED_LABEL_CLAIM
        assert res.regulatory_status == "UNREGISTERED_LABEL_CLAIM"

    def test_chlorpyrifos_registered_on_paddy(self):
        res = inspect_chemical_safety("Chlorpyrifos", "paddy")
        assert res.is_safe is True
        assert res.regulatory_status == "REGISTERED_LABEL_USE"

    def test_hazardous_tank_mix_detection(self):
        # Blitox (Copper oxychloride) + Rogor (Dimethoate)
        res = inspect_chemical_safety("Blitox + Rogor", "banana")
        assert not res.is_safe
        assert res.reason_code == ReasonCode.HAZARDOUS_TANK_MIX
        assert res.reason_category == ReasonCategory.PRODUCT_SAFETY_POLICY
        assert "phytotoxicity" in res.explanation.lower()
        assert "கருகலை" in res.explanation_ta

        # Copper oxychloride and Chlorpyrifos
        res2 = inspect_chemical_safety("Copper oxychloride and Chlorpyrifos", "paddy")
        assert not res2.is_safe
        assert res2.reason_code == ReasonCode.HAZARDOUS_TANK_MIX

    def test_tamil_statutory_banned_chemicals(self):
        # Phorate in Tamil
        res_phorate = inspect_chemical_safety("ஃபோரேட்", "paddy")
        assert not res_phorate.is_safe
        assert res_phorate.reason_code == ReasonCode.BANNED_NATIONWIDE

        # Methyl Parathion in Tamil
        res_mp = inspect_chemical_safety("மெத்தில் பாராத்தியான்", "tomato")
        assert not res_mp.is_safe
        assert res_mp.reason_code == ReasonCode.BANNED_NATIONWIDE

        # Paraquat in Tamil
        res_pq = inspect_chemical_safety("பாராக்குவாட்", "chilli")
        assert not res_pq.is_safe
        assert res_pq.reason_code == ReasonCode.RESTRICTED_USE

