"""Document ingestion and validation module for THUNAI Knowledge Base."""

import glob
import json
import os
from typing import Dict, List, Optional
from pydantic import BaseModel, ConfigDict

from thunai.core.enums import SourceTier
from thunai.knowledge.source_registry import get_source, is_trusted_tier


class RawCorpusDocument(BaseModel):
    """Raw document ingested from official government or university publication."""
    model_config = ConfigDict(frozen=True)
    document_id: str
    source_id: str
    source_title: str
    publication_date: str
    page_or_section: str
    crop: str
    crop_id: str
    crop_scientific_name: str
    crop_aliases: List[str] = []
    target_problem: str
    problem_scientific_name: str
    problem_category: str
    problem_aliases: List[str] = []
    recommendation_type: str
    active_ingredient: str
    formulation: str
    concentration: str
    dose: float
    dose_unit: str
    application_basis: str
    water_volume_l_per_acre: Optional[float] = None
    waiting_period_days: Optional[int] = None
    brand_names: List[str] = []
    instructions_en: str
    instructions_ta: str
    raw_source_text: str
    evidence_status: str


class DocumentIngestionEngine:
    """Ingests, validates, and stores official corpus documents."""

    def __init__(self, corpus_dir: Optional[str] = None):
        self.corpus_dir = corpus_dir or os.path.join(os.path.dirname(__file__), "corpus")
        self.documents: Dict[str, RawCorpusDocument] = {}

    def load_all_documents(self) -> List[RawCorpusDocument]:
        """Loads all JSON corpus files from the corpus directory."""
        pattern = os.path.join(self.corpus_dir, "*.json")
        loaded_docs: List[RawCorpusDocument] = []

        for filepath in glob.glob(pattern):
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                for item in data:
                    source_meta = get_source(item.get("source_id", ""))
                    if not source_meta or not is_trusted_tier(source_meta.tier):
                        continue

                    doc = RawCorpusDocument(**item)
                    self.documents[doc.document_id] = doc
                    loaded_docs.append(doc)

        return loaded_docs

    def get_document(self, document_id: str) -> Optional[RawCorpusDocument]:
        return self.documents.get(document_id)

    def get_documents_by_crop(self, crop_id: str) -> List[RawCorpusDocument]:
        c_id = crop_id.lower().strip()
        return [doc for doc in self.documents.values() if doc.crop_id.lower().strip() == c_id]
