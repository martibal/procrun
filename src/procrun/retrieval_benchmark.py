"""Benchmark metrics for the engine-v2 semantic recall stage.

This evaluator never needs customer-visible labels. It measures whether exact gold source spans are
retrieved into the candidate set, plus the amount of irrelevant candidate noise introduced.
"""

from __future__ import annotations

from dataclasses import dataclass

from procrun.domain import FundingProject
from procrun.evidence_retrieval_v2 import SemanticEvidenceCandidate, SemanticRecallEngine


@dataclass(frozen=True)
class GoldSpan:
    start: int
    end: int

    def validate(self, source_text: str) -> None:
        if self.start < 0 or self.end <= self.start or self.end > len(source_text):
            raise ValueError("gold span is outside source text")


@dataclass(frozen=True)
class RetrievalBenchmarkCase:
    case_id: str
    project: FundingProject
    gold_spans: tuple[GoldSpan, ...]

    @property
    def is_positive(self) -> bool:
        return bool(self.gold_spans)


@dataclass(frozen=True)
class RetrievalBenchmarkMetrics:
    case_count: int
    positive_case_count: int
    negative_case_count: int
    candidate_count: int
    gold_span_count: int
    retrieved_gold_span_count: int
    positive_cases_hit: int
    negative_cases_with_candidates: int
    candidates_overlapping_gold: int
    exact_span_failures: int

    @property
    def gold_excerpt_recall(self) -> float:
        return self.retrieved_gold_span_count / self.gold_span_count if self.gold_span_count else 1.0

    @property
    def positive_case_recall(self) -> float:
        return self.positive_cases_hit / self.positive_case_count if self.positive_case_count else 1.0

    @property
    def candidate_precision(self) -> float:
        return self.candidates_overlapping_gold / self.candidate_count if self.candidate_count else 1.0

    @property
    def negative_case_false_positive_rate(self) -> float:
        return (
            self.negative_cases_with_candidates / self.negative_case_count
            if self.negative_case_count
            else 0.0
        )


def _overlaps(candidate: SemanticEvidenceCandidate, gold: GoldSpan) -> bool:
    return candidate.start_offset < gold.end and gold.start < candidate.end_offset


def evaluate_semantic_recall(
    engine: SemanticRecallEngine,
    cases: tuple[RetrievalBenchmarkCase, ...],
    *,
    candidate_limit: int = 24,
    return_limit: int = 12,
    minimum_semantic_score: float = 0.15,
) -> RetrievalBenchmarkMetrics:
    positive_case_count = 0
    negative_case_count = 0
    candidate_count = 0
    gold_span_count = 0
    retrieved_gold_span_count = 0
    positive_cases_hit = 0
    negative_cases_with_candidates = 0
    candidates_overlapping_gold = 0
    exact_span_failures = 0

    for case in cases:
        source = case.project.project_scope_text
        for span in case.gold_spans:
            span.validate(source)
        candidates = engine.retrieve(
            case.project,
            candidate_limit=candidate_limit,
            return_limit=return_limit,
            minimum_semantic_score=minimum_semantic_score,
        )
        candidate_count += len(candidates)
        for candidate in candidates:
            try:
                candidate.validate_against(source)
            except ValueError:
                exact_span_failures += 1

        if case.is_positive:
            positive_case_count += 1
            gold_span_count += len(case.gold_spans)
            hit_indexes = {
                gold_index
                for gold_index, gold in enumerate(case.gold_spans)
                if any(_overlaps(candidate, gold) for candidate in candidates)
            }
            retrieved_gold_span_count += len(hit_indexes)
            if hit_indexes:
                positive_cases_hit += 1
            candidates_overlapping_gold += sum(
                1
                for candidate in candidates
                if any(_overlaps(candidate, gold) for gold in case.gold_spans)
            )
        else:
            negative_case_count += 1
            if candidates:
                negative_cases_with_candidates += 1

    return RetrievalBenchmarkMetrics(
        case_count=len(cases),
        positive_case_count=positive_case_count,
        negative_case_count=negative_case_count,
        candidate_count=candidate_count,
        gold_span_count=gold_span_count,
        retrieved_gold_span_count=retrieved_gold_span_count,
        positive_cases_hit=positive_cases_hit,
        negative_cases_with_candidates=negative_cases_with_candidates,
        candidates_overlapping_gold=candidates_overlapping_gold,
        exact_span_failures=exact_span_failures,
    )
