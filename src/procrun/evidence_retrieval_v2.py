"""High-recall semantic evidence retrieval for ProcRun engine v2.

Semantic models are used only to rank exact source sentences. Customer-visible evidence remains
verbatim text from the approved project source with exact offsets. The default runtime backends run
locally; no project text is sent to an external inference service.
"""

from __future__ import annotations

import importlib
import math
import re
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any, Literal, Protocol

from procrun.component_engine import RULES
from procrun.domain import FundingProject

SEMANTIC_RECALL_VERSION = "semantic-recall-v2"
DEFAULT_EMBEDDING_MODEL = "intfloat/multilingual-e5-small"
DEFAULT_RERANKER_MODEL = "cross-encoder/mmarco-mMiniLMv2-L12-H384-v1"

_SENTENCE_RE = re.compile(r"[^.!?\n]+(?:[.!?]+|(?=\n|$))", re.UNICODE)

_PROCUREMENT_INTENT_QUERIES: tuple[tuple[str, str], ...] = (
    (
        "procurement-intent:planned-supply",
        "progetto che prevede acquisto, fornitura, installazione o approvvigionamento di beni, "
        "attrezzature, impianti, sistemi o servizi",
    ),
    (
        "procurement-intent:tender",
        "progetto con futura gara, appalto, bando, affidamento, procedura di acquisto o contratto",
    ),
    (
        "procurement-intent:works",
        "intervento che richiede lavori, realizzazione, costruzione, riqualificazione o installazione "
        "da affidare a un fornitore o appaltatore",
    ),
    (
        "procurement-intent:equipment",
        "progetto che necessita apparecchiature, macchinari, componenti tecnici, sistemi elettrici, "
        "digitali, di controllo o monitoraggio",
    ),
    (
        "procurement-intent:services",
        "progetto che richiede progettazione, ingegneria, consulenza tecnica, manutenzione, studio, "
        "audit o altri servizi professionali acquistabili",
    ),
)


Vector = tuple[float, ...]
EmbeddingKind = Literal["query", "passage"]


class EmbeddingBackend(Protocol):
    model_name: str

    def encode(self, texts: Sequence[str], *, kind: EmbeddingKind) -> tuple[Vector, ...]: ...


class RerankerBackend(Protocol):
    model_name: str

    def score(self, query: str, passages: Sequence[str]) -> tuple[float, ...]: ...


@dataclass(frozen=True)
class SemanticQuery:
    query_id: str
    text: str
    category: str | None = None


@dataclass(frozen=True)
class SentenceSpan:
    start: int
    end: int
    text: str


@dataclass(frozen=True)
class SemanticEvidenceCandidate:
    operation_code: str
    source_url: str
    source_field: str
    start_offset: int
    end_offset: int
    original_text: str
    query_id: str
    suggested_category: str | None
    semantic_score: float
    rerank_score: float
    engine_version: str = SEMANTIC_RECALL_VERSION

    def validate_against(self, source_text: str) -> None:
        if self.end_offset <= self.start_offset:
            raise ValueError("semantic evidence candidate has invalid offsets")
        if source_text[self.start_offset : self.end_offset] != self.original_text:
            raise ValueError("semantic evidence candidate is not an exact source span")


class LocalSentenceTransformersEmbedder:
    """Local-only multilingual E5 adapter loaded lazily at runtime."""

    def __init__(self, model_name: str = DEFAULT_EMBEDDING_MODEL) -> None:
        module = importlib.import_module("sentence_transformers")
        sentence_transformer = getattr(module, "SentenceTransformer")
        self.model_name = model_name
        self._model: Any = sentence_transformer(model_name)

    def encode(self, texts: Sequence[str], *, kind: EmbeddingKind) -> tuple[Vector, ...]:
        prefix = "query: " if kind == "query" else "passage: "
        values = self._model.encode(
            [prefix + text for text in texts],
            normalize_embeddings=True,
            convert_to_numpy=False,
        )
        return tuple(tuple(float(value) for value in row) for row in values)


class LocalSentenceTransformersReranker:
    """Local-only multilingual cross-encoder adapter loaded lazily at runtime."""

    def __init__(self, model_name: str = DEFAULT_RERANKER_MODEL) -> None:
        module = importlib.import_module("sentence_transformers")
        cross_encoder = getattr(module, "CrossEncoder")
        self.model_name = model_name
        self._model: Any = cross_encoder(model_name)

    def score(self, query: str, passages: Sequence[str]) -> tuple[float, ...]:
        if not passages:
            return ()
        values = self._model.predict([(query, passage) for passage in passages])
        return tuple(float(value) for value in values)


def _cosine(left: Vector, right: Vector) -> float:
    if len(left) != len(right) or not left:
        raise ValueError("embedding vectors must be non-empty and have equal dimensions")
    numerator = sum(a * b for a, b in zip(left, right, strict=True))
    left_norm = math.sqrt(sum(value * value for value in left))
    right_norm = math.sqrt(sum(value * value for value in right))
    if left_norm == 0.0 or right_norm == 0.0:
        return 0.0
    return numerator / (left_norm * right_norm)


def sentence_spans(source_text: str) -> tuple[SentenceSpan, ...]:
    spans: list[SentenceSpan] = []
    for match in _SENTENCE_RE.finditer(source_text):
        raw = match.group(0)
        left_trim = len(raw) - len(raw.lstrip())
        right_trimmed = raw.rstrip()
        if not right_trimmed.strip():
            continue
        start = match.start() + left_trim
        end = match.start() + len(right_trimmed)
        text = source_text[start:end]
        spans.append(SentenceSpan(start=start, end=end, text=text))
    return tuple(spans)


def semantic_queries() -> tuple[SemanticQuery, ...]:
    queries = [SemanticQuery(query_id=query_id, text=text) for query_id, text in _PROCUREMENT_INTENT_QUERIES]
    for rule in RULES:
        examples = ", ".join(rule.phrases[:6])
        category = f"{rule.domain.value}:{rule.category}"
        queries.append(
            SemanticQuery(
                query_id=f"component:{category}",
                category=category,
                text=(
                    f"progetto che richiede acquisto, fornitura, installazione, lavori o servizi per "
                    f"{rule.label}. Esempi terminologici: {examples}"
                ),
            )
        )
    return tuple(queries)


class SemanticRecallEngine:
    """Two-stage candidate generator optimized for recall while preserving exact source evidence."""

    def __init__(self, embedder: EmbeddingBackend, reranker: RerankerBackend) -> None:
        self.embedder = embedder
        self.reranker = reranker
        self.queries = semantic_queries()
        self._query_vectors = embedder.encode([item.text for item in self.queries], kind="query")
        if len(self._query_vectors) != len(self.queries):
            raise ValueError("embedding backend returned the wrong number of query vectors")

    def retrieve(
        self,
        project: FundingProject,
        *,
        candidate_limit: int = 24,
        return_limit: int = 12,
        minimum_semantic_score: float = 0.15,
    ) -> tuple[SemanticEvidenceCandidate, ...]:
        """Return exact source spans ranked by local semantic retrieval and reranking.

        The semantic threshold is intentionally a broad candidate-generation control, not a product
        quality threshold. Final production thresholds must be frozen from clean development evidence.
        """

        if candidate_limit < 1 or return_limit < 1:
            raise ValueError("candidate and return limits must be positive")
        if return_limit > candidate_limit:
            raise ValueError("return_limit cannot exceed candidate_limit")

        spans = sentence_spans(project.project_scope_text)
        if not spans:
            return ()
        passage_vectors = self.embedder.encode([span.text for span in spans], kind="passage")
        if len(passage_vectors) != len(spans):
            raise ValueError("embedding backend returned the wrong number of passage vectors")

        stage_one: list[tuple[float, int, int]] = []
        for span_index, passage_vector in enumerate(passage_vectors):
            scored_queries = [
                (_cosine(query_vector, passage_vector), query_index)
                for query_index, query_vector in enumerate(self._query_vectors)
            ]
            semantic_score, query_index = max(scored_queries, key=lambda item: (item[0], -item[1]))
            if semantic_score >= minimum_semantic_score:
                stage_one.append((semantic_score, query_index, span_index))

        stage_one.sort(key=lambda item: (-item[0], spans[item[2]].start, item[1]))
        stage_one = stage_one[:candidate_limit]
        if not stage_one:
            return ()

        rerank_scores: list[float] = []
        for _, query_index, span_index in stage_one:
            score = self.reranker.score(self.queries[query_index].text, [spans[span_index].text])
            if len(score) != 1:
                raise ValueError("reranker must return exactly one score per passage")
            rerank_scores.append(score[0])

        candidates: list[SemanticEvidenceCandidate] = []
        for (semantic_score, query_index, span_index), rerank_score in zip(
            stage_one, rerank_scores, strict=True
        ):
            query = self.queries[query_index]
            span = spans[span_index]
            candidate = SemanticEvidenceCandidate(
                operation_code=project.operation_code,
                source_url=project.source_url,
                source_field="project_scope_text",
                start_offset=span.start,
                end_offset=span.end,
                original_text=span.text,
                query_id=query.query_id,
                suggested_category=query.category,
                semantic_score=semantic_score,
                rerank_score=rerank_score,
            )
            candidate.validate_against(project.project_scope_text)
            candidates.append(candidate)

        candidates.sort(
            key=lambda item: (
                -item.rerank_score,
                -item.semantic_score,
                item.start_offset,
                item.query_id,
            )
        )
        return tuple(candidates[:return_limit])
