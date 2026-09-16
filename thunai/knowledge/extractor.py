"""Evidence extraction module converting raw corpus documents into verified EvidenceRecords."""

from typing import List, Optional
from thunai.core.enums import EvidenceStatus, RecommendationType, SourceTier
from thunai.core.models import EvidenceRecord
from thunai.knowledge.document_ingestion import RawCorpusDocument
from thunai.knowledge.source_registry import get_source


from thunai.core.normalizer import normalize_problem


def extract_evidence_record(doc: RawCorpusDocument) -> EvidenceRecord:
    source_meta = get_source(doc.source_id)
    tier = source_meta.tier if source_meta else SourceTier.TRUSTED_GOV_ACADEMIC

    rec_type_map = {
        "chemical": RecommendationType.CHEMICAL,
        "biological": RecommendationType.BIOLOGICAL,
        "cultural": RecommendationType.CULTURAL,
        "mechanical": RecommendationType.MECHANICAL,
    }
    rec_type = rec_type_map.get(doc.recommendation_type.lower(), RecommendationType.CHEMICAL)

    norm_p = normalize_problem(doc.target_problem, doc.crop_id)
    canonical_problem_id = norm_p.problem_id if norm_p else doc.target_problem.lower().replace(" ", "_").strip()

    provenance_note = (
        f"DocID: {doc.document_id} | Section: {doc.page_or_section} | "
        f"PubDate: {doc.publication_date} | Source: {doc.source_title} | "
        f"Verbatim: {doc.raw_source_text}"
    )

    return EvidenceRecord(
        evidence_id=doc.document_id,
        crop=doc.crop,
        crop_id=doc.crop_id.lower().strip(),
        crop_scientific_name=doc.crop_scientific_name,
        problem=doc.target_problem,
        problem_id=canonical_problem_id,
        recommendation_type=rec_type,
        active_ingredient=doc.active_ingredient,
        formulation=doc.formulation,
        concentration=doc.concentration,
        brand_names=doc.brand_names,
        dose=doc.dose,
        dose_unit=doc.dose_unit,
        application_basis=doc.application_basis,
        water_volume_l_per_acre=doc.water_volume_l_per_acre,
        waiting_period_days=doc.waiting_period_days,
        source=doc.source_id,
        source_reference=f"{doc.source_title}, {doc.page_or_section}",
        source_tier=tier,
        geography="Tamil Nadu",
        evidence_status=EvidenceStatus.VERIFIED if doc.evidence_status == "VERIFIED" else EvidenceStatus.PROVISIONAL,
        notes=provenance_note,
    )


def extract_all_evidence_records(docs: List[RawCorpusDocument]) -> List[EvidenceRecord]:
    return [extract_evidence_record(doc) for doc in docs]