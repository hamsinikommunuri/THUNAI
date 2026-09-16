"""Hybrid Evidence Retriever with Hard Agricultural Pre-Filtering for THUNAI.

Core Principle:
Semantic search must never override crop isolation.
Pre-filtering by crop is mathematically enforced before hybrid ranking,
ensuring a Wrong-Crop Retrieval Rate of exactly 0.0 at the safety boundary.
"""

from typing import List, Optional, Tuple
from pydantic import BaseModel, ConfigDict

from thunai.core.models import EvidenceRecord, FarmerContext
from thunai.core.normalizer import normalize_crop
from thunai.knowledge.document_ingestion import DocumentIngestionEngine
from thunai.knowledge.extractor import extract_all_evidence_records
from thunai.knowledge.indexer import BM25Index, DenseSubwordIndex
from thunai.knowledge.synonyms import resolve_crop, resolve_problem


class RetrievalResult(BaseModel):
    """Container for retrieved evidence candidates and evaluation telemetry."""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    query: str
    filtered_crop_id: Optional[str] = None
    candidates: List[EvidenceRecord] = []
    scores: List[float] = []
    has_evidence: bool = False
    has_conflict: bool = False
    conflict_notes: Optional[str] = None


class HybridEvidenceRetriever:
    """Production hybrid retriever for THUNAI Phase 1 crops."""

    def __init__(
        self,
        corpus_engine: Optional[DocumentIngestionEngine] = None,
        bm25_weight: float = 0.55,
        dense_weight: float = 0.45,
        score_threshold: float = 0.15,
    ):
        self.corpus_engine = corpus_engine or DocumentIngestionEngine()
        self.bm25_weight = bm25_weight
        self.dense_weight = dense_weight
        self.score_threshold = score_threshold

        # Load and extract all official evidence records
        raw_docs = self.corpus_engine.load_all_documents()
        self.all_records: List[EvidenceRecord] = extract_all_evidence_records(raw_docs)

        # Index records grouped by crop for hard agricultural pre-filtering
        self.crop_indices: dict = {}
        self._build_crop_isolated_indices()

    def _build_crop_isolated_indices(self) -> None:
        """Builds separate lexical and dense indexes per crop to guarantee 0 cross-crop leakage."""
        crops = {"paddy", "tomato", "banana", "chilli"}
        for crop in crops:
            crop_recs = [r for r in self.all_records if r.crop_id.lower().strip() == crop]
            bm25 = BM25Index()
            bm25.fit(crop_recs)
            dense = DenseSubwordIndex()
            dense.fit(crop_recs)
            self.crop_indices[crop] = {
                "records": crop_recs,
                "bm25": bm25,
                "dense": dense,
            }

    def retrieve(
        self,
        query: str,
        context: Optional[FarmerContext] = None,
        top_k: int = 5,
    ) -> RetrievalResult:
        """Retrieves evidence candidates with mandatory hard agricultural pre-filter.

        Pipeline:
        1. Context Normalization: Determine target crop from context or raw query.
        2. Hard Agricultural Filter: Drop all non-matching crops before any similarity calculation.
        3. Lexical BM25 Scoring on crop-isolated corpus.
        4. Dense Subword Scoring on crop-isolated corpus.
        5. Hybrid Linear Fusion.
        6. Threshold & Conflict Analysis.
        """
        # Step 1: Resolve crop strictly
        target_crop_id: Optional[str] = None
        if context and context.crop_id:
            target_crop_id = context.crop_id.lower().strip()
        elif context and context.crop:
            norm = normalize_crop(context.crop)
            target_crop_id = norm.crop_id if norm.is_known else None

        if not target_crop_id:
            resolved = resolve_crop(query)
            if resolved:
                target_crop_id = resolved

        # If crop cannot be identified, HARD GATE: do not retrieve dangerous ungrounded candidates
        if not target_crop_id or target_crop_id not in self.crop_indices:
            return RetrievalResult(
                query=query,
                filtered_crop_id=None,
                candidates=[],
                scores=[],
                has_evidence=False,
                has_conflict=False,
                conflict_notes="No target crop could be reliably isolated. Hard agricultural gate blocked cross-crop retrieval.",
            )

        # Step 2: Retrieve strictly within isolated crop index
        crop_data = self.crop_indices[target_crop_id]
        crop_records: List[EvidenceRecord] = crop_data["records"]

        if not crop_records:
            return RetrievalResult(
                query=query,
                filtered_crop_id=target_crop_id,
                candidates=[],
                scores=[],
                has_evidence=False,
            )

        bm25_scores = crop_data["bm25"].score(query)
        dense_scores = crop_data["dense"].score(query)

        # Step 3: Hybrid Fusion
        fused_candidates: List[Tuple[float, EvidenceRecord]] = []
        for idx, rec in enumerate(crop_records):
            s_bm25 = bm25_scores[idx] if idx < len(bm25_scores) else 0.0
            s_dense = dense_scores[idx] if idx < len(dense_scores) else 0.0
            hybrid_score = self.bm25_weight * s_bm25 + self.dense_weight * s_dense

            if hybrid_score >= self.score_threshold:
                fused_candidates.append((hybrid_score, rec))

        # Rank descending by score
        fused_candidates.sort(key=lambda x: x[0], reverse=True)
        top_candidates = fused_candidates[:top_k]

        ranked_records = [c[1] for c in top_candidates]
        ranked_scores = [c[0] for c in top_candidates]

        # Step 4: Check for conflicting authoritative doses
        has_conflict = False
        conflict_note = None
        if len(ranked_records) >= 2:
            first = ranked_records[0]
            second = ranked_records[1]
            # If same problem & same active ingredient but conflicting doses
            if (
                first.problem_id == second.problem_id
                and first.active_ingredient == second.active_ingredient
                and first.dose != second.dose
            ):
                has_conflict = True
                conflict_note = (
                    f"Conflicting dosage detected between {first.source} ({first.dose} {first.dose_unit}) "
                    f"and {second.source} ({second.dose} {second.dose_unit}) for {first.problem}."
                )

        return RetrievalResult(
            query=query,
            filtered_crop_id=target_crop_id,
            candidates=ranked_records,
            scores=ranked_scores,
            has_evidence=len(ranked_records) > 0,
            has_conflict=has_conflict,
            conflict_notes=conflict_note,
        )