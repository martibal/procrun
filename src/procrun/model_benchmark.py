"""Frozen scoring harness for the Phase C local component-model benchmark."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from statistics import median
from typing import Literal

from procrun.component_engine import RULES, ComponentDomain
from procrun.domain import StrictModel
from procrun.llama_adapter import LlamaBenchmarkResult
from procrun.model_fallback import (
    AllowedComponentCategory,
    LocalModelRequest,
    ModelComponentProposal,
    ModelPromptSpan,
)

BENCHMARK_SCHEMA_VERSION = "component-benchmark-v1"
_RULE_KEYS = {(rule.domain, rule.category) for rule in RULES}


class BenchmarkCorpusError(ValueError):
    """Raised when a benchmark corpus or result violates a frozen invariant."""


class ComponentBenchmarkCase(StrictModel):
    case_id: str
    operation_code: str
    domains: tuple[ComponentDomain, ...]
    scope_text: str
    expected_proposals: tuple[ModelComponentProposal, ...] = ()


class ComponentBenchmarkCorpus(StrictModel):
    schema_version: Literal["component-benchmark-v1"] = "component-benchmark-v1"
    language: Literal["pt-PT"] = "pt-PT"
    cases: tuple[ComponentBenchmarkCase, ...]


@dataclass(frozen=True)
class LoadedBenchmarkCorpus:
    corpus: ComponentBenchmarkCorpus
    sha256: str


class ComponentBenchmarkScore(StrictModel):
    case_count: int
    expected_proposal_count: int
    predicted_proposal_count: int
    true_positive_count: int
    false_positive_count: int
    false_negative_count: int
    exact_precision: float | None
    exact_recall: float | None
    exact_f1: float | None
    exact_case_match_count: int
    exact_case_match_rate: float
    abstention_case_count: int
    correct_abstention_count: int
    correct_abstention_rate: float | None
    false_positive_abstention_case_count: int


class ComponentBenchmarkCaseResult(StrictModel):
    """Synthetic per-case evidence retained so aggregate failures can be diagnosed."""

    case_id: str
    expected_proposals: tuple[ModelComponentProposal, ...]
    predicted_proposals: tuple[ModelComponentProposal, ...]
    exact_match: bool
    cache_hit: bool
    elapsed_seconds: float | None


class ComponentBenchmarkReport(StrictModel):
    schema_version: Literal["component-benchmark-report-v2"] = "component-benchmark-report-v2"
    corpus_sha256: str
    model_id: str
    model_artifact_sha256: str
    llama_cli_sha256: str
    score: ComponentBenchmarkScore
    case_results: tuple[ComponentBenchmarkCaseResult, ...]
    cache_hit_count: int
    inference_count: int
    measured_elapsed_seconds: tuple[float, ...]
    median_elapsed_seconds: float | None
    max_elapsed_seconds: float | None


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _proposal_key(proposal: ModelComponentProposal) -> tuple[str, str, int, int, str]:
    return (
        proposal.domain.value,
        proposal.category,
        proposal.start,
        proposal.end,
        proposal.source_text,
    )


def _allowed_categories(
    domains: Sequence[ComponentDomain],
) -> tuple[AllowedComponentCategory, ...]:
    selected = frozenset(domains)
    return tuple(
        AllowedComponentCategory(
            domain=rule.domain,
            category=rule.category,
            label=rule.label,
        )
        for rule in sorted(RULES, key=lambda item: (item.domain.value, item.category))
        if rule.domain in selected
    )


def _validate_case(case: ComponentBenchmarkCase) -> None:
    if not case.case_id.strip():
        raise BenchmarkCorpusError("benchmark case_id cannot be blank")
    if not case.operation_code.startswith("BENCH-"):
        raise BenchmarkCorpusError("benchmark operation_code must use the synthetic BENCH- prefix")
    if not case.domains:
        raise BenchmarkCorpusError("benchmark case must contain at least one frozen domain")
    if not case.scope_text.strip():
        raise BenchmarkCorpusError("benchmark scope_text cannot be blank")
    if "http://" in case.scope_text.lower() or "https://" in case.scope_text.lower():
        raise BenchmarkCorpusError("benchmark scope_text must not contain URLs")
    if "@" in case.scope_text:
        raise BenchmarkCorpusError("benchmark scope_text must not contain email-like text")

    domains = frozenset(case.domains)
    for proposal in case.expected_proposals:
        if proposal.domain not in domains:
            raise BenchmarkCorpusError("expected proposal domain is outside the benchmark case")
        if (proposal.domain, proposal.category) not in _RULE_KEYS:
            raise BenchmarkCorpusError("expected proposal category is outside the frozen taxonomy")
        if proposal.start >= proposal.end or proposal.end > len(case.scope_text):
            raise BenchmarkCorpusError("expected proposal offsets are outside benchmark scope_text")
        if case.scope_text[proposal.start : proposal.end] != proposal.source_text:
            raise BenchmarkCorpusError("expected proposal source_text is not its exact source span")


def load_component_benchmark(path: Path) -> LoadedBenchmarkCorpus:
    """Load and validate a small synthetic benchmark corpus without normalizing its bytes."""

    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise BenchmarkCorpusError(f"benchmark corpus could not be read: {path}") from exc
    try:
        payload = json.loads(raw.decode("utf-8", errors="strict"))
        corpus = ComponentBenchmarkCorpus.model_validate(payload)
    except (UnicodeDecodeError, ValueError) as exc:
        raise BenchmarkCorpusError("benchmark corpus is not valid strict UTF-8 JSON") from exc

    if not corpus.cases:
        raise BenchmarkCorpusError("benchmark corpus must contain at least one case")
    case_ids = [case.case_id for case in corpus.cases]
    operation_codes = [case.operation_code for case in corpus.cases]
    if len(case_ids) != len(set(case_ids)):
        raise BenchmarkCorpusError("benchmark case_id values must be unique")
    if len(operation_codes) != len(set(operation_codes)):
        raise BenchmarkCorpusError("benchmark operation_code values must be unique")
    for case in corpus.cases:
        _validate_case(case)

    return LoadedBenchmarkCorpus(
        corpus=corpus,
        sha256=hashlib.sha256(raw).hexdigest(),
    )


def benchmark_request(case: ComponentBenchmarkCase) -> LocalModelRequest:
    """Build the exact model request for one fully synthetic benchmark case."""

    return LocalModelRequest(
        operation_code=case.operation_code,
        source_sha256=_sha256_text(case.scope_text),
        domains=case.domains,
        unmatched_scope_spans=(
            ModelPromptSpan(
                start=0,
                end=len(case.scope_text),
                text=case.scope_text,
            ),
        ),
        allowed_categories=_allowed_categories(case.domains),
    )


def _safe_ratio(numerator: int, denominator: int) -> float | None:
    return numerator / denominator if denominator else None


def score_component_benchmark(
    corpus: ComponentBenchmarkCorpus,
    predictions: Mapping[str, Sequence[ModelComponentProposal]],
) -> ComponentBenchmarkScore:
    """Score exact category + exact evidence-span matches; no fuzzy credit is awarded."""

    expected_ids = {case.case_id for case in corpus.cases}
    supplied_ids = set(predictions)
    if supplied_ids != expected_ids:
        missing = sorted(expected_ids - supplied_ids)
        extra = sorted(supplied_ids - expected_ids)
        raise BenchmarkCorpusError(
            f"benchmark predictions must cover the exact case set; missing={missing}, extra={extra}"
        )

    tp = fp = fn = predicted_count = expected_count = 0
    exact_cases = abstention_cases = correct_abstentions = false_abstention_cases = 0

    for case in corpus.cases:
        expected = {_proposal_key(item) for item in case.expected_proposals}
        predicted = {_proposal_key(item) for item in predictions[case.case_id]}
        expected_count += len(expected)
        predicted_count += len(predicted)
        tp += len(expected & predicted)
        fp += len(predicted - expected)
        fn += len(expected - predicted)
        if predicted == expected:
            exact_cases += 1
        if not expected:
            abstention_cases += 1
            if not predicted:
                correct_abstentions += 1
            else:
                false_abstention_cases += 1

    precision = _safe_ratio(tp, tp + fp)
    recall = _safe_ratio(tp, tp + fn)
    f1 = None
    if precision is not None and recall is not None and precision + recall > 0:
        f1 = 2 * precision * recall / (precision + recall)

    return ComponentBenchmarkScore(
        case_count=len(corpus.cases),
        expected_proposal_count=expected_count,
        predicted_proposal_count=predicted_count,
        true_positive_count=tp,
        false_positive_count=fp,
        false_negative_count=fn,
        exact_precision=precision,
        exact_recall=recall,
        exact_f1=f1,
        exact_case_match_count=exact_cases,
        exact_case_match_rate=exact_cases / len(corpus.cases),
        abstention_case_count=abstention_cases,
        correct_abstention_count=correct_abstentions,
        correct_abstention_rate=_safe_ratio(correct_abstentions, abstention_cases),
        false_positive_abstention_case_count=false_abstention_cases,
    )


def build_component_benchmark_report(
    loaded: LoadedBenchmarkCorpus,
    results: Mapping[str, LlamaBenchmarkResult],
) -> ComponentBenchmarkReport:
    """Validate benchmark run provenance and produce measurements without an approval verdict."""

    expected_ids = {case.case_id for case in loaded.corpus.cases}
    if set(results) != expected_ids:
        missing = sorted(expected_ids - set(results))
        extra = sorted(set(results) - expected_ids)
        raise BenchmarkCorpusError(
            f"benchmark results must cover the exact case set; missing={missing}, extra={extra}"
        )

    model_ids: set[str] = set()
    model_hashes: set[str] = set()
    cli_hashes: set[str] = set()
    predictions: dict[str, tuple[ModelComponentProposal, ...]] = {}
    case_results: list[ComponentBenchmarkCaseResult] = []
    elapsed: list[float] = []
    cache_hits = 0

    for case in loaded.corpus.cases:
        request = benchmark_request(case)
        result = results[case.case_id]
        batch = result.batch
        if batch.operation_code != request.operation_code:
            raise BenchmarkCorpusError("benchmark result operation_code does not match its case")
        if batch.source_sha256 != request.source_sha256:
            raise BenchmarkCorpusError("benchmark result source hash does not match its case")
        model_ids.add(batch.model_identity.model_id)
        model_hashes.add(batch.model_identity.artifact_sha256)
        cli_hashes.add(result.llama_cli_sha256)
        predictions[case.case_id] = batch.proposals
        expected_keys = {_proposal_key(item) for item in case.expected_proposals}
        predicted_keys = {_proposal_key(item) for item in batch.proposals}
        case_results.append(
            ComponentBenchmarkCaseResult(
                case_id=case.case_id,
                expected_proposals=case.expected_proposals,
                predicted_proposals=batch.proposals,
                exact_match=predicted_keys == expected_keys,
                cache_hit=result.cache_hit,
                elapsed_seconds=result.elapsed_seconds,
            )
        )
        cache_hits += int(result.cache_hit)
        if result.elapsed_seconds is not None:
            elapsed.append(result.elapsed_seconds)

    if len(model_ids) != 1 or len(model_hashes) != 1 or len(cli_hashes) != 1:
        raise BenchmarkCorpusError(
            "one benchmark report must use one exact model and llama runtime"
        )

    score = score_component_benchmark(loaded.corpus, predictions)
    measured = tuple(elapsed)
    return ComponentBenchmarkReport(
        corpus_sha256=loaded.sha256,
        model_id=next(iter(model_ids)),
        model_artifact_sha256=next(iter(model_hashes)),
        llama_cli_sha256=next(iter(cli_hashes)),
        score=score,
        case_results=tuple(case_results),
        cache_hit_count=cache_hits,
        inference_count=len(loaded.corpus.cases) - cache_hits,
        measured_elapsed_seconds=measured,
        median_elapsed_seconds=median(measured) if measured else None,
        max_elapsed_seconds=max(measured) if measured else None,
    )
