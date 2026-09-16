"""Source Registry for official agricultural authorities."""

from typing import Dict, Optional
from pydantic import BaseModel, ConfigDict

from thunai.core.enums import SourceTier


class SourceRecord(BaseModel):
    """Metadata for an authoritative agricultural source."""
    model_config = ConfigDict(frozen=True)
    source_id: str
    title: str
    publisher: str
    year: int
    tier: SourceTier
    url: Optional[str] = None
    notes: Optional[str] = None


OFFICIAL_SOURCES: Dict[str, SourceRecord] = {
    "TNAU_CPG_2024": SourceRecord(
        source_id="TNAU_CPG_2024",
        title="Crop Production Guide - Agriculture 2024",
        publisher="Tamil Nadu Agricultural University & Directorate of Agriculture, Government of Tamil Nadu",
        year=2024,
        tier=SourceTier.TRUSTED_GOV_ACADEMIC,
        url="https://agritech.tnau.ac.in/pdf/cpg_agri_2024.pdf",
        notes="Primary agronomic and crop protection standard for Tamil Nadu agroclimatic zones.",
    ),
    "CIBRC_REGISTRY_2024": SourceRecord(
        source_id="CIBRC_REGISTRY_2024",
        title="Major Uses of Pesticides (Registered under the Insecticides Act, 1968)",
        publisher="Central Insecticide Board & Registration Committee (CIBRC), Ministry of Agriculture and Farmers Welfare, Govt of India",
        year=2024,
        tier=SourceTier.REGULATORY,
        url="https://cibrc.gov.in/major-uses-of-pesticides",
        notes="Statutory label-claim registry determining approved crop-pest label combinations and approved doses.",
    ),
    "ICAR_POP_2023": SourceRecord(
        source_id="ICAR_POP_2023",
        title="Package of Practices for Horticultural and Field Crops",
        publisher="Indian Council of Agricultural Research (ICAR)",
        year=2023,
        tier=SourceTier.TRUSTED_GOV_ACADEMIC,
        url="https://icar.org.in/package-of-practices",
        notes="National agricultural research standard for crop cultivation and IPM.",
    ),
}


def get_source(source_id: str) -> Optional[SourceRecord]:
    """Retrieves source record metadata by source_id."""
    return OFFICIAL_SOURCES.get(source_id)


def is_trusted_tier(tier: SourceTier) -> bool:
    """Verifies that the tier meets THUNAI safety credibility standards."""
    return tier in (SourceTier.REGULATORY, SourceTier.TRUSTED_GOV_ACADEMIC)