from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime, timezone

from procrun.domain import FundingProject, TemporalProvenance
from procrun.evidence_retrieval_v2 import SemanticRecallEngine, sentence_spans


class FakeEmbedder:
    model_name = "fake-embedder"

    def encode(self, texts: Sequence[str], *, kind: str) -> tuple[tuple[float, ...], ...]:
        vectors: list[tuple[float, ...]] = []
        for text in texts:
            normalized = text.casefold()
            procurement = float(
                any(token in normalized for token in ("pompe", "fornitura", "acquisto", "gara", "installazione"))
            )
            unrelated = float(any(token in normalized for token in ("festival", "turismo", "marketing")))
            vectors.append((procurement, unrelated, 1.0))
        return tuple(vectors)


class FakeReranker:
    model_name = "fake-reranker"

    def score(self, query: str, passages: Sequence[str]) -> tuple[float, ...]:
        return tuple(
            10.0 if "pompe" in passage.casefold() else 1.0
            for passage in passages
        )


def project(text: str) -> FundingProject:
    return FundingProject(
        operation_code="op-1",
        first_seen_at=datetime(2026, 9, 1, tzinfo=timezone.utc),
        temporal_provenance=TemporalProvenance.RESOLVED,
        project_scope_text=text,
        source_url="https://example.invalid/project",
    )


def test_sentence_spans_preserve_exact_source_offsets() -> None:
    source = "Prima frase.  Fornitura di nuove pompe e sistemi di controllo.\nTerza frase."
    spans = sentence_spans(source)
    assert len(spans) == 3
    for span in spans:
        assert source[span.start : span.end] == span.text


def test_semantic_recall_finds_paraphrased_procurement_sentence_and_preserves_span() -> None:
    source = (
        "Il progetto riguarda la riqualificazione generale dell'impianto. "
        "È prevista la fornitura di nuove pompe ad alta efficienza. "
        "Sono inoltre previste attività informative per i cittadini."
    )
    engine = SemanticRecallEngine(FakeEmbedder(), FakeReranker())
    candidates = engine.retrieve(project(source), candidate_limit=8, return_limit=3, minimum_semantic_score=0.1)

    assert candidates
    assert candidates[0].original_text == "È prevista la fornitura di nuove pompe ad alta efficienza."
    assert source[candidates[0].start_offset : candidates[0].end_offset] == candidates[0].original_text
    assert candidates[0].rerank_score == 10.0


def test_semantic_recall_can_return_no_candidate_for_unrelated_text() -> None:
    source = "Il progetto promuove un festival culturale e attività di marketing territoriale."
    engine = SemanticRecallEngine(FakeEmbedder(), FakeReranker())
    candidates = engine.retrieve(project(source), minimum_semantic_score=0.95)
    assert candidates == ()


def test_semantic_recall_is_deterministic() -> None:
    source = "Fornitura di pompe. Installazione di sistemi di monitoraggio."
    engine = SemanticRecallEngine(FakeEmbedder(), FakeReranker())
    first = engine.retrieve(project(source), candidate_limit=6, return_limit=2, minimum_semantic_score=0.1)
    second = engine.retrieve(project(source), candidate_limit=6, return_limit=2, minimum_semantic_score=0.1)
    assert first == second
