"""THUNAI Knowledge & Retrieval Package.
Contains official source registries, synonym mappings, document ingestion,
lexical/vector indexers, and hybrid evidence retrieval engine.
"""

from thunai.knowledge.source_registry import SourceRecord, SourceTier, get_source, is_trusted_tier
from thunai.knowledge.synonyms import (
    AgriculturalSynonymNormalizer,
    resolve_crop,
    resolve_problem,
    expand_synonyms,
    tokenize_bilingual,
)
from thunai.knowledge.document_ingestion import DocumentIngestionEngine, RawCorpusDocument
from thunai.knowledge.extractor import extract_evidence_record, extract_all_evidence_records
from thunai.knowledge.indexer import BM25Index, DenseSubwordIndex
from thunai.knowledge.retriever import HybridEvidenceRetriever, RetrievalResult

__all__ = [
    "SourceRecord",
    "SourceTier",
    "get_source",
    "is_trusted_tier",
    "AgriculturalSynonymNormalizer",
    "resolve_crop",
    "resolve_problem",
    "expand_synonyms",
    "tokenize_bilingual",
    "DocumentIngestionEngine",
    "RawCorpusDocument",
    "extract_evidence_record",
    "extract_all_evidence_records",
    "BM25Index",
    "DenseSubwordIndex",
    "HybridEvidenceRetriever",
    "RetrievalResult",
]