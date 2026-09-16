"""Lexical (BM25) and Dense vector indexing for THUNAI agricultural knowledge base."""

import math
import re
from typing import Dict, List, Set, Tuple
from collections import Counter

from thunai.core.models import EvidenceRecord
from thunai.knowledge.synonyms import expand_synonyms, tokenize_bilingual


class BM25Index:
    """Deterministic BM25 Okapi lexical index supporting bilingual Tamil/English."""

    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.corpus_size = 0
        self.avg_doc_len = 0.0
        self.doc_lengths: List[int] = []
        self.doc_freqs: Dict[str, int] = Counter()
        self.term_freqs: List[Counter] = []
        self.records: List[EvidenceRecord] = []

    def fit(self, records: List[EvidenceRecord]) -> None:
        """Indexes a collection of EvidenceRecords."""
        self.records = records
        self.corpus_size = len(records)
        self.doc_lengths = []
        self.term_freqs = []
        self.doc_freqs = Counter()

        total_length = 0
        for rec in records:
            # Build rich searchable document text
            doc_text = (
                f"{rec.crop} {rec.crop_id} {rec.problem} {rec.problem_id} "
                f"{rec.active_ingredient or ''} {rec.formulation or ''} "
                f"{' '.join(rec.brand_names)} {rec.source_reference or ''} "
                f"{rec.notes or ''}"
            )
            tokens = tokenize_bilingual(doc_text)
            doc_len = len(tokens)
            self.doc_lengths.append(doc_len)
            total_length += doc_len

            tf = Counter(tokens)
            self.term_freqs.append(tf)
            for term in tf.keys():
                self.doc_freqs[term] += 1

        self.avg_doc_len = (total_length / self.corpus_size) if self.corpus_size > 0 else 0.0

    def score(self, query: str) -> List[float]:
        """Scores all indexed records against the query using BM25."""
        if self.corpus_size == 0:
            return []

        expanded_terms = expand_synonyms(query)
        scores = [0.0] * self.corpus_size

        for term in expanded_terms:
            df = self.doc_freqs.get(term, 0)
            if df == 0:
                continue

            # Standard Robertson-Spärck Jones IDF
            idf = math.log(1.0 + (self.corpus_size - df + 0.5) / (df + 0.5))

            for idx in range(self.corpus_size):
                tf = self.term_freqs[idx].get(term, 0)
                if tf == 0:
                    continue

                doc_len = self.doc_lengths[idx]
                len_norm = 1.0 - self.b + self.b * (doc_len / self.avg_doc_len if self.avg_doc_len > 0 else 1.0)
                numerator = tf * (self.k1 + 1.0)
                denominator = tf + self.k1 * len_norm
                scores[idx] += idf * (numerator / denominator)

        # Normalize scores to [0, 1]
        max_score = max(scores) if scores else 0.0
        if max_score > 0:
            scores = [s / max_score for s in scores]

        return scores


class DenseSubwordIndex:
    """Dense subword n-gram vector index for semantic & spelling-tolerant retrieval."""

    def __init__(self, ngram_min: int = 3, ngram_max: int = 4):
        self.ngram_min = ngram_min
        self.ngram_max = ngram_max
        self.vocabulary: Dict[str, int] = {}
        self.doc_vectors: List[Dict[int, float]] = []
        self.records: List[EvidenceRecord] = []

    def _extract_ngrams(self, text: str) -> List[str]:
        tokens = tokenize_bilingual(text)
        ngrams: List[str] = list(tokens)  # include full tokens
        for token in tokens:
            t_len = len(token)
            if t_len >= self.ngram_min:
                for n in range(self.ngram_min, min(self.ngram_max + 1, t_len + 1)):
                    for i in range(t_len - n + 1):
                        ngrams.append(token[i : i + n])
        return ngrams

    def fit(self, records: List[EvidenceRecord]) -> None:
        self.records = records
        self.vocabulary = {}
        self.doc_vectors = []

        raw_doc_ngrams: List[List[str]] = []
        df_counter: Counter = Counter()

        for rec in records:
            doc_text = (
                f"{rec.crop} {rec.crop_id} {rec.problem} {rec.problem_id} "
                f"{rec.active_ingredient or ''} {rec.formulation or ''} "
                f"{' '.join(rec.brand_names)} {rec.source_reference or ''} "
                f"{rec.notes or ''}"
            )
            ngrams = self._extract_ngrams(doc_text)
            raw_doc_ngrams.append(ngrams)
            for ng in set(ngrams):
                df_counter[ng] += 1

        # Build vocabulary of top distinctive n-grams
        for ng, _ in df_counter.most_common(5000):
            self.vocabulary[ng] = len(self.vocabulary)

        num_docs = len(records)
        for ngrams in raw_doc_ngrams:
            tf = Counter(ngrams)
            vec: Dict[int, float] = {}
            norm_sq = 0.0
            for ng, count in tf.items():
                if ng in self.vocabulary:
                    dim = self.vocabulary[ng]
                    idf = math.log(1.0 + num_docs / (df_counter[ng] + 1.0))
                    val = count * idf
                    vec[dim] = val
                    norm_sq += val * val

            norm = math.sqrt(norm_sq)
            if norm > 0:
                for dim in vec:
                    vec[dim] /= norm
            self.doc_vectors.append(vec)

    def score(self, query: str) -> List[float]:
        if not self.records or not self.doc_vectors:
            return []

        expanded = " ".join(expand_synonyms(query))
        q_ngrams = self._extract_ngrams(f"{query} {expanded}")
        q_tf = Counter(q_ngrams)

        q_vec: Dict[int, float] = {}
        q_norm_sq = 0.0
        num_docs = len(self.records)

        for ng, count in q_tf.items():
            if ng in self.vocabulary:
                dim = self.vocabulary[ng]
                idf = math.log(1.0 + num_docs / 2.0)
                val = count * idf
                q_vec[dim] = val
                q_norm_sq += val * val

        q_norm = math.sqrt(q_norm_sq)
        if q_norm > 0:
            for dim in q_vec:
                q_vec[dim] /= q_norm
        else:
            return [0.0] * len(self.records)

        scores: List[float] = []
        for d_vec in self.doc_vectors:
            # Cosine similarity
            dot = sum(q_val * d_vec.get(dim, 0.0) for dim, q_val in q_vec.items())
            scores.append(max(0.0, dot))

        max_s = max(scores) if scores else 0.0
        if max_s > 0:
            scores = [s / max_s for s in scores]

        return scores