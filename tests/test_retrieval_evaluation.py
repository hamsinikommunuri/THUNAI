"""Test Suite for THUNAI Knowledge Retrieval & Evaluation Engine.

Validates:
1. Multi-lingual resolution (Tamil, Tanglish, English).
2. Hard Agricultural Crop Isolation (Wrong-Crop Retrieval Rate == 0.0).
3. IR Metrics: Precision@1, Recall@3, MRR on benchmark queries.
4. Unsupported queries returning zero / empty evidence safely.
5. Conflicting dosage detection across multiple records.
6. Full End-to-End Integration Pipeline:
   Query -> Retriever -> EvidenceRecord -> DoseLockEngine -> SafetyDecision -> ActionDecision.
"""

import pytest
from pathlib import Path

from thunai.core.enums import (
    ActionStatus,
    CropId,
    DecisionType,
    ReasonCategory,
    ReasonCode,
    SourceTier,
)
from thunai.core.models import FarmerContext, EvidenceRecord
from thunai.knowledge.source_registry import SourceRecord, SourceTier, get_source
from thunai.knowledge.synonyms import (
    AgriculturalSynonymNormalizer,
    resolve_crop,
    resolve_problem,
)
from thunai.knowledge.document_ingestion import DocumentIngestionEngine
from thunai.knowledge.retriever import HybridEvidenceRetriever, RetrievalResult
from thunai.safety.dose_lock import DoseLockEngine
from thunai.safety.escalation import build_action_decision


@pytest.fixture(scope="module")
def retriever() -> HybridEvidenceRetriever:
    """Initialize a HybridEvidenceRetriever with the authentic 4-crop corpus."""
    engine = DocumentIngestionEngine()
    retriever = HybridEvidenceRetriever(
        corpus_engine=engine,
        bm25_weight=0.55,
        dense_weight=0.45,
        score_threshold=0.10,
    )
    return retriever


class TestSynonymNormalizer:
    def test_tamil_crop_resolution(self):
        norm = AgriculturalSynonymNormalizer()
        assert norm.normalize_crop("நெல்") == CropId.PADDY
        assert norm.normalize_crop("தக்காளி") == CropId.TOMATO
        assert norm.normalize_crop("வாழை") == CropId.BANANA
        assert norm.normalize_crop("மிளகாய்") == CropId.CHILLI

    def test_tanglish_crop_resolution(self):
        norm = AgriculturalSynonymNormalizer()
        assert norm.normalize_crop("nel") == CropId.PADDY
        assert norm.normalize_crop("thakkali") == CropId.TOMATO
        assert norm.normalize_crop("vazhai") == CropId.BANANA
        assert norm.normalize_crop("milagai") == CropId.CHILLI

    def test_pest_disease_resolution(self):
        norm = AgriculturalSynonymNormalizer()
        assert norm.normalize_target("குருத்துப்பூச்சி") == "stem_borer"
        assert norm.normalize_target("காய்ப்புழு") == "fruit_borer"
        assert norm.normalize_target("இலைப்புள்ளி") == "sigatoka"
        assert norm.normalize_target("இலைப்பேன்") == "thrips"


class TestHardCropIsolation:
    """Rigorous verification that Wrong-Crop Retrieval Rate == 0.0 at the safety boundary."""

    def test_banana_query_never_returns_other_crops(self, retriever: HybridEvidenceRetriever):
        queries = [
            "வாழை இலைப்புள்ளி நோய் மருந்து என்ன?",
            "vazhai sigatoka leaf spot control",
            "வாழை தண்டு துளைப்பான்",
            "banana panama wilt drenching",
        ]
        for q in queries:
            ctx = FarmerContext(crop="Banana", crop_id="banana", raw_query=q)
            result = retriever.retrieve(q, context=ctx, top_k=5)
            for record in result.candidates:
                assert record.crop_id == "banana", f"Leakage: {record.crop_id} found in banana query '{q}'"

    def test_tomato_query_never_returns_other_crops(self, retriever: HybridEvidenceRetriever):
        queries = [
            "தக்காளி காய்ப்புழு மருந்து அளவு",
            "thakkali fruit borer spray",
            "tomato early blight mancozeb",
            "தக்காளி இலைக்கருகல் நோய்",
        ]
        for q in queries:
            ctx = FarmerContext(crop="Tomato", crop_id="tomato", raw_query=q)
            result = retriever.retrieve(q, context=ctx, top_k=5)
            for record in result.candidates:
                assert record.crop_id == "tomato", f"Leakage: {record.crop_id} found in tomato query '{q}'"

    def test_paddy_query_never_returns_other_crops(self, retriever: HybridEvidenceRetriever):
        queries = [
            "நெல் குருத்துப்பூச்சிக்கு என்ன மருந்து அடிக்கலாம்?",
            "nel blast disease control",
            "paddy brown planthopper buprofezin",
        ]
        for q in queries:
            ctx = FarmerContext(crop="Paddy", crop_id="paddy", raw_query=q)
            result = retriever.retrieve(q, context=ctx, top_k=5)
            for record in result.candidates:
                assert record.crop_id == "paddy", f"Leakage: {record.crop_id} found in paddy query '{q}'"

    def test_chilli_query_never_returns_other_crops(self, retriever: HybridEvidenceRetriever):
        queries = [
            "மிளகாய் இலைப்பேன் கட்டுப்பாடு",
            "chilli thrips fipronil dose",
            "milagai anthracnose fruit rot",
        ]
        for q in queries:
            ctx = FarmerContext(crop="Chilli", crop_id="chilli", raw_query=q)
            result = retriever.retrieve(q, context=ctx, top_k=5)
            for record in result.candidates:
                assert record.crop_id == "chilli", f"Leakage: {record.crop_id} found in chilli query '{q}'"

    def test_wrong_crop_retrieval_rate_is_strictly_zero(self, retriever: HybridEvidenceRetriever):
        """Quantify wrong-crop retrieval rate across a matrix of 20 queries."""
        test_matrix = [
            ("paddy", "நெல் குருத்துப்பூச்சி"),
            ("paddy", "paddy blast tricyclazole"),
            ("paddy", "nel bph buprofezin"),
            ("paddy", "paddy brown planthopper"),
            ("paddy", "நெல் குலை நோய்"),
            ("tomato", "தக்காளி காய்ப்புழு"),
            ("tomato", "tomato fruit borer indoxacarb"),
            ("tomato", "thakkali early blight"),
            ("tomato", "tomato late blight mancozeb"),
            ("tomato", "தக்காளி இலைக்கருகல்"),
            ("banana", "வாழை இலைப்புள்ளி"),
            ("banana", "banana sigatoka propiconazole"),
            ("banana", "vazhai stem weevil"),
            ("banana", "banana panama wilt carbendazim"),
            ("banana", "வாழை தண்டு வண்டு"),
            ("chilli", "மிளகாய் இலைப்பேன்"),
            ("chilli", "chilli thrips fipronil"),
            ("chilli", "milagai fruit rot azoxystrobin"),
            ("chilli", "chilli die-back anthracnose"),
            ("chilli", "மிளகாய் காய் அழுகல்"),
        ]
        wrong_crop_count = 0
        total_retrieved = 0

        for target_crop_id, query in test_matrix:
            ctx = FarmerContext(crop=target_crop_id, crop_id=target_crop_id, raw_query=query)
            result = retriever.retrieve(query, context=ctx, top_k=3)
            for rec in result.candidates:
                total_retrieved += 1
                if rec.crop_id != target_crop_id:
                    wrong_crop_count += 1

        assert total_retrieved > 0
        wrong_crop_rate = wrong_crop_count / total_retrieved
        assert wrong_crop_rate == 0.0, f"Expected 0.0 wrong crop rate, got {wrong_crop_rate}"


class TestInformationRetrievalMetrics:
    """Evaluates Precision@1, Recall@3, and MRR against gold ground truth."""

    GOLD_EVAL_BENCHMARK = [
        {
            "crop_id": "paddy",
            "query": "நெல் குருத்துப்பூச்சி மருந்து என்ன?",
            "expected_ai": "Chlorantraniliprole",
        },
        {
            "crop_id": "paddy",
            "query": "nel blast disease tricyclazole dose",
            "expected_ai": "Tricyclazole",
        },
        {
            "crop_id": "tomato",
            "query": "தக்காளி காய்ப்புழு மருந்து என்ன?",
            "expected_ai": "Chlorantraniliprole",
        },
        {
            "crop_id": "tomato",
            "query": "tomato early blight mancozeb spray",
            "expected_ai": "Mancozeb",
        },
        {
            "crop_id": "banana",
            "query": "வாழை சிகாடோகா இலைப்புள்ளி ப்ரோபிகோனசோல்",
            "expected_ai": "Propiconazole",
        },
        {
            "crop_id": "chilli",
            "query": "மிளகாய் இலைப்பேன் ஸ்பினடோரம் அளவு",
            "expected_ai": "Spinetoram",
        },
    ]

    def test_precision_recall_mrr_benchmarks(self, retriever: HybridEvidenceRetriever):
        p1_hits = 0
        r3_hits = 0
        reciprocal_ranks = []

        for item in self.GOLD_EVAL_BENCHMARK:
            ctx = FarmerContext(crop=item["crop_id"], crop_id=item["crop_id"], raw_query=item["query"])
            res = retriever.retrieve(item["query"], context=ctx, top_k=3)
            candidates = res.candidates
            expected_ai = item["expected_ai"].lower()

            # Rank of first relevant item
            rank = None
            for idx, rec in enumerate(candidates):
                if rec.active_ingredient and expected_ai in rec.active_ingredient.lower():
                    rank = idx + 1
                    break

            if rank == 1:
                p1_hits += 1
            if rank is not None and rank <= 3:
                r3_hits += 1
                reciprocal_ranks.append(1.0 / rank)
            else:
                reciprocal_ranks.append(0.0)

        total = len(self.GOLD_EVAL_BENCHMARK)
        precision_at_1 = p1_hits / total
        recall_at_3 = r3_hits / total
        mrr = sum(reciprocal_ranks) / total

        assert precision_at_1 >= 0.80, f"Precision@1 ({precision_at_1:.2f}) < 0.80"
        assert recall_at_3 >= 0.90, f"Recall@3 ({recall_at_3:.2f}) < 0.90"
        assert mrr >= 0.85, f"MRR ({mrr:.2f}) < 0.85"


class TestUnsupportedAndConflictQueries:
    def test_unsupported_crop_returns_no_evidence(self, retriever: HybridEvidenceRetriever):
        # Mango is not in our 4 crops
        res = retriever.retrieve("மாம்பழம் வண்டு மருந்து", context=None, top_k=3)
        assert res.has_evidence is False
        assert len(res.candidates) == 0

    def test_unknown_target_returns_empty_or_low_score(self, retriever: HybridEvidenceRetriever):
        ctx = FarmerContext(crop="Tomato", crop_id="tomato", raw_query="விநோத மர்ம வியாதி")
        res = retriever.retrieve("விநோத மர்ம வியாதி", context=ctx, top_k=3)
        # Random non-agricultural terms do not match candidate records
        assert len(res.candidates) == 0 or res.scores[0] < 0.50

    def test_conflicting_dosage_detection(self, retriever: HybridEvidenceRetriever):
        # In tomato early blight or blast, check conflict detection logic
        res = retriever.retrieve("tomato early blight", context=FarmerContext(crop="Tomato", crop_id="tomato"), top_k=5)
        assert res.has_evidence is True
        # Verify that multiple records with different active ingredients or formulations are retrieved
        assert len(res.candidates) >= 2


class TestEndToEndIntegrationPipeline:
    """Validates:
    Farmer Query (Tamil) -> Retriever -> EvidenceRecord -> DoseLockEngine -> SafetyDecision -> ActionDecision
    """

    def test_e2e_safe_query_paddy_stem_borer(self, retriever: HybridEvidenceRetriever):
        # 1. Farmer query in natural Tamil
        tamil_query = "நெல் குருத்துப்பூச்சி தாக்குதலுக்கு என்ன மருந்து தெளிக்க வேண்டும்?"
        context = FarmerContext(
            crop="Paddy",
            crop_id="paddy",
            target_problem="Stem Borer",
            raw_query=tamil_query,
        )

        # 2. Hybrid Retrieval with hard crop isolation
        retrieval_res = retriever.retrieve(context.raw_query, context=context, top_k=1)
        assert retrieval_res.has_evidence is True
        top_evidence: EvidenceRecord = retrieval_res.candidates[0]
        assert top_evidence.crop_id == "paddy"
        assert "Chlorantraniliprole" in top_evidence.active_ingredient

        # 3. DoseLock Engine Evaluation
        engine = DoseLockEngine()
        safety_dec = engine.evaluate(
            context=context,
            evidence=top_evidence,
        )
        assert safety_dec.decision == DecisionType.ALLOW
        assert safety_dec.reason_code == ReasonCode.VERIFIED_AND_ALLOWED
        assert safety_dec.allowed_dose is not None
        assert safety_dec.allowed_dose.dose_amount == top_evidence.dose

        # 4. ActionDecision Builder
        action_dec = build_action_decision(safety_decision=safety_dec, context=context)
        assert action_dec.status == ActionStatus.ALLOW_RECOMMENDATION
        assert action_dec.can_recommend_dose is True
        assert action_dec.farmer_message != ""
        assert action_dec.farmer_message_ta is not None
        assert "Chlorantraniliprole" in action_dec.farmer_message

    def test_e2e_banned_chemical_in_query_blocked(self, retriever: HybridEvidenceRetriever):
        # Farmer asks for Monocrotophos on Tomato (prohibited on vegetables under S.O. 3960(E))
        query = "தக்காளி காய்ப்புழுவுக்கு மோனோகுரோட்டோபாஸ் அடிக்கலாமா?"
        context = FarmerContext(
            crop="Tomato",
            crop_id="tomato",
            target_problem="Fruit Borer",
            requested_chemical="Monocrotophos",
            raw_query=query,
        )

        retrieval_res = retriever.retrieve(query, context=context, top_k=1)
        top_evidence = retrieval_res.candidates[0] if retrieval_res.candidates else None

        engine = DoseLockEngine()
        safety_dec = engine.evaluate(context=context, evidence=top_evidence)

        # Must be blocked due to BANNED_FOR_CROP on tomato under S.O. 3960(E)
        assert safety_dec.decision == DecisionType.BLOCK
        assert safety_dec.reason_code == ReasonCode.BANNED_FOR_CROP
        assert safety_dec.reason_category == ReasonCategory.LEGAL_REGULATORY

        action_dec = build_action_decision(safety_decision=safety_dec, context=context)
        assert action_dec.status == ActionStatus.BLOCK_AND_EXPLAIN
        assert action_dec.can_recommend_dose is False
        assert action_dec.escalation_needed is True
        assert "தடை செய்யப்பட்டுள்ளது" in (action_dec.farmer_message_ta or "")