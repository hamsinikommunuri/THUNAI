"""Pytest fixtures and verified evidence corpus for THUNAI Phase 1 crops."""

import pytest
from thunai.core.enums import EvidenceStatus, RecommendationType, SourceTier
from thunai.core.models import EvidenceRecord
from thunai.safety.dose_lock import DoseLockEngine


@pytest.fixture
def engine() -> DoseLockEngine:
    return DoseLockEngine()


@pytest.fixture
def verified_paddy_stem_borer() -> EvidenceRecord:
    return EvidenceRecord(
        evidence_id="EV-PAD-001",
        crop="Paddy",
        crop_id="paddy",
        crop_scientific_name="Oryza sativa",
        problem="Yellow Stem Borer",
        problem_id="paddy_stem_borer",
        recommendation_type=RecommendationType.CHEMICAL,
        active_ingredient="Chlorantraniliprole",
        formulation="GR",
        concentration="0.4%",
        brand_names=["Ferterra"],
        dose=4.0,
        dose_unit="kg/acre",
        application_basis="soil application / broadcasting",
        source="TNAU Crop Production Guide 2020",
        source_reference="Page 45, Section 4.2",
        source_tier=SourceTier.TRUSTED_GOV_ACADEMIC,
        geography="Tamil Nadu",
        evidence_status=EvidenceStatus.VERIFIED,
    )


@pytest.fixture
def verified_paddy_blast() -> EvidenceRecord:
    return EvidenceRecord(
        evidence_id="EV-PAD-002",
        crop="Paddy",
        crop_id="paddy",
        crop_scientific_name="Oryza sativa",
        problem="Blast Disease",
        problem_id="paddy_blast",
        recommendation_type=RecommendationType.CHEMICAL,
        active_ingredient="Tricyclazole",
        formulation="WP",
        concentration="75%",
        brand_names=["Beam"],
        dose=0.6,
        dose_unit="g/l",
        application_basis="foliar spray",
        source="TNAU AgriTech Portal",
        source_reference="Crop Protection: Paddy Diseases",
        source_tier=SourceTier.TRUSTED_GOV_ACADEMIC,
        geography="Tamil Nadu",
        evidence_status=EvidenceStatus.VERIFIED,
    )


@pytest.fixture
def verified_paddy_leaf_folder() -> EvidenceRecord:
    return EvidenceRecord(
        evidence_id="EV-PAD-003",
        crop="Paddy",
        crop_id="paddy",
        crop_scientific_name="Oryza sativa",
        problem="Leaf Folder",
        problem_id="paddy_leaf_folder",
        recommendation_type=RecommendationType.CHEMICAL,
        active_ingredient="Flubendiamide",
        formulation="SC",
        concentration="39.35%",
        brand_names=["Fame"],
        dose=0.2,
        dose_unit="ml/l",
        application_basis="foliar spray",
        source="TNAU Crop Production Guide",
        source_reference="Rice Pests",
        source_tier=SourceTier.TRUSTED_GOV_ACADEMIC,
        geography="Tamil Nadu",
        evidence_status=EvidenceStatus.VERIFIED,
    )


@pytest.fixture
def verified_tomato_fruit_borer() -> EvidenceRecord:
    return EvidenceRecord(
        evidence_id="EV-TOM-001",
        crop="Tomato",
        crop_id="tomato",
        crop_scientific_name="Solanum lycopersicum",
        problem="Fruit Borer",
        problem_id="tomato_fruit_borer",
        recommendation_type=RecommendationType.CHEMICAL,
        active_ingredient="Chlorantraniliprole",
        formulation="SC",
        concentration="18.5%",
        brand_names=["Coragen"],
        dose=0.3,
        dose_unit="ml/l",
        application_basis="foliar spray",
        source="TNAU Crop Production Guide",
        source_reference="Vegetable Crops: Tomato Borer",
        source_tier=SourceTier.TRUSTED_GOV_ACADEMIC,
        geography="Tamil Nadu",
        evidence_status=EvidenceStatus.VERIFIED,
    )


@pytest.fixture
def verified_tomato_early_blight() -> EvidenceRecord:
    return EvidenceRecord(
        evidence_id="EV-TOM-002",
        crop="Tomato",
        crop_id="tomato",
        crop_scientific_name="Solanum lycopersicum",
        problem="Early Blight",
        problem_id="tomato_early_blight",
        recommendation_type=RecommendationType.CHEMICAL,
        active_ingredient="Mancozeb",
        formulation="WP",
        concentration="75%",
        brand_names=["Dithane M-45"],
        dose=2.0,
        dose_unit="g/l",
        application_basis="foliar spray",
        source="TNAU AgriTech Portal",
        source_reference="Tomato Diseases",
        source_tier=SourceTier.TRUSTED_GOV_ACADEMIC,
        geography="Tamil Nadu",
        evidence_status=EvidenceStatus.VERIFIED,
    )


@pytest.fixture
def verified_banana_sigatoka() -> EvidenceRecord:
    return EvidenceRecord(
        evidence_id="EV-BAN-001",
        crop="Banana",
        crop_id="banana",
        crop_scientific_name="Musa acuminata",
        problem="Sigatoka Leaf Spot",
        problem_id="banana_sigatoka",
        recommendation_type=RecommendationType.CHEMICAL,
        active_ingredient="Propiconazole",
        formulation="EC",
        concentration="25%",
        brand_names=["Tilt"],
        dose=1.0,
        dose_unit="ml/l",
        application_basis="foliar spray with 1% mineral oil",
        source="TNAU Package of Practices: Banana",
        source_reference="Sigatoka Disease Management",
        source_tier=SourceTier.TRUSTED_GOV_ACADEMIC,
        geography="Tamil Nadu",
        evidence_status=EvidenceStatus.VERIFIED,
    )


@pytest.fixture
def verified_banana_pseudostem_borer() -> EvidenceRecord:
    return EvidenceRecord(
        evidence_id="EV-BAN-002",
        crop="Banana",
        crop_id="banana",
        crop_scientific_name="Musa acuminata",
        problem="Pseudostem Borer",
        problem_id="banana_pseudostem_borer",
        recommendation_type=RecommendationType.CHEMICAL,
        active_ingredient="Chlorpyrifos",
        formulation="EC",
        concentration="20%",
        brand_names=["Durmet"],
        dose=2.5,
        dose_unit="ml/l",
        application_basis="pseudostem swabbing",
        source="TNAU AgriTech Portal",
        source_reference="Banana Weevil and Borer",
        source_tier=SourceTier.TRUSTED_GOV_ACADEMIC,
        geography="Tamil Nadu",
        evidence_status=EvidenceStatus.VERIFIED,
    )


@pytest.fixture
def verified_chilli_thrips() -> EvidenceRecord:
    return EvidenceRecord(
        evidence_id="EV-CHI-001",
        crop="Chilli",
        crop_id="chilli",
        crop_scientific_name="Capsicum annuum",
        problem="Chilli Thrips",
        problem_id="chilli_thrips",
        recommendation_type=RecommendationType.CHEMICAL,
        active_ingredient="Spinetoram",
        formulation="SC",
        concentration="11.7%",
        brand_names=["Delegate"],
        dose=0.8,
        dose_unit="ml/l",
        application_basis="foliar spray",
        source="CIBRC Approved Label Claims / TNAU",
        source_reference="Chilli Pest Management",
        source_tier=SourceTier.REGULATORY,
        geography="Tamil Nadu",
        evidence_status=EvidenceStatus.VERIFIED,
    )


@pytest.fixture
def verified_chilli_anthracnose() -> EvidenceRecord:
    return EvidenceRecord(
        evidence_id="EV-CHI-002",
        crop="Chilli",
        crop_id="chilli",
        crop_scientific_name="Capsicum annuum",
        problem="Anthracnose / Fruit Rot",
        problem_id="chilli_anthracnose",
        recommendation_type=RecommendationType.CHEMICAL,
        active_ingredient="Azoxystrobin",
        formulation="SC",
        concentration="23%",
        brand_names=["Amistar"],
        dose=1.0,
        dose_unit="ml/l",
        application_basis="foliar spray",
        source="TNAU Crop Production Guide",
        source_reference="Chilli Diseases: Fruit Rot",
        source_tier=SourceTier.TRUSTED_GOV_ACADEMIC,
        geography="Tamil Nadu",
        evidence_status=EvidenceStatus.VERIFIED,
    )
