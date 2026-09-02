import json
from pathlib import Path

import pytest

from procrun import model_benchmark, model_fallback
from procrun.llama_adapter import LlamaBenchmarkResult

BenchmarkCorpusError = model_benchmark.BenchmarkCorpusError
benchmark_request = model_benchmark.benchmark_request
build_component_benchmark_report = model_benchmark.build_component_benchmark_report
load_component_benchmark = model_benchmark.load_component_benchmark
score_component_benchmark = model_benchmark.score_component_benchmark
LocalModelIdentity = model_fallback.LocalModelIdentity
ModelComponentProposal = model_fallback.ModelComponentProposal
ModelProposalBatch = model_fallback.ModelProposalBatch

FIXTURE = Path(__file__).parent / "fixtures" / "component_benchmark_v1.json"


def loaded():
    return load_component_benchmark(FIXTURE)


def test_frozen_portuguese_corpus_is_small_synthetic_and_exact() -> None:
    benchmark = loaded()

    assert benchmark.corpus.schema_version == "component-benchmark-v1"
    assert benchmark.corpus.language == "pt-PT"
    assert len(benchmark.corpus.cases) == 12
    assert sum(bool(case.expected_proposals) for case in benchmark.corpus.cases) == 10
    assert all(case.operation_code.startswith("BENCH-") for case in benchmark.corpus.cases)
    assert all("http" not in case.scope_text.lower() for case in benchmark.corpus.cases)
    assert all("@" not in case.scope_text for case in benchmark.corpus.cases)
    assert len(benchmark.sha256) == 64

    for case in benchmark.corpus.cases:
        for proposal in case.expected_proposals:
            assert case.scope_text[proposal.start : proposal.end] == proposal.source_text


def test_benchmark_request_contains_only_synthetic_scope_and_frozen_categories() -> None:
    case = loaded().corpus.cases[0]
    request = benchmark_request(case)

    assert request.operation_code == case.operation_code
    assert len(request.source_sha256) == 64
    assert len(request.unmatched_scope_spans) == 1
    assert request.unmatched_scope_spans[0].text == case.scope_text
    assert request.unmatched_scope_spans[0].start == 0
    assert request.unmatched_scope_spans[0].end == len(case.scope_text)
    assert request.allowed_categories
    assert all(item.domain in case.domains for item in request.allowed_categories)


def test_exact_oracle_scores_perfectly_without_inventing_thresholds() -> None:
    benchmark = loaded()
    predictions = {
        case.case_id: case.expected_proposals for case in benchmark.corpus.cases
    }

    score = score_component_benchmark(benchmark.corpus, predictions)

    assert score.case_count == 12
    assert score.expected_proposal_count == 10
    assert score.predicted_proposal_count == 10
    assert score.true_positive_count == 10
    assert score.false_positive_count == 0
    assert score.false_negative_count == 0
    assert score.exact_precision == 1.0
    assert score.exact_recall == 1.0
    assert score.exact_f1 == 1.0
    assert score.exact_case_match_rate == 1.0
    assert score.semantic_true_positive_count == 10
    assert score.semantic_false_positive_count == 0
    assert score.semantic_false_negative_count == 0
    assert score.semantic_precision == 1.0
    assert score.semantic_recall == 1.0
    assert score.semantic_f1 == 1.0
    assert score.semantic_case_match_rate == 1.0
    assert score.abstention_case_count == 2
    assert score.correct_abstention_count == 2
    assert score.correct_abstention_rate == 1.0
    assert score.failed_case_count == 0
    assert score.failed_abstention_case_count == 0


def test_correct_category_with_different_exact_span_gets_semantic_not_exact_credit() -> None:
    benchmark = loaded()
    predictions = {
        case.case_id: case.expected_proposals for case in benchmark.corpus.cases
    }
    positive = next(case for case in benchmark.corpus.cases if case.expected_proposals)
    expected = positive.expected_proposals[0]
    predictions[positive.case_id] = (
        ModelComponentProposal(
            domain=expected.domain,
            category=expected.category,
            start=0,
            end=len(positive.scope_text),
            source_text=positive.scope_text,
        ),
    )

    score = score_component_benchmark(benchmark.corpus, predictions)

    assert score.true_positive_count == 9
    assert score.false_positive_count == 1
    assert score.false_negative_count == 1
    assert score.exact_case_match_count == 11
    assert score.semantic_true_positive_count == 10
    assert score.semantic_false_positive_count == 0
    assert score.semantic_false_negative_count == 0
    assert score.semantic_case_match_count == 12


def test_false_positive_on_abstention_case_is_measured_explicitly() -> None:
    benchmark = loaded()
    predictions = {
        case.case_id: case.expected_proposals for case in benchmark.corpus.cases
    }
    negative = next(
        case for case in benchmark.corpus.cases if case.case_id == "negative_generic"
    )
    predictions[negative.case_id] = (
        ModelComponentProposal(
            domain=negative.domains[0],
            category="pumps",
            start=0,
            end=1,
            source_text=negative.scope_text[0:1],
        ),
    )

    score = score_component_benchmark(benchmark.corpus, predictions)

    assert score.false_positive_count == 1
    assert score.semantic_false_positive_count == 1
    assert score.false_positive_abstention_case_count == 1
    assert score.correct_abstention_count == 1
    assert score.exact_case_match_count == 11
    assert score.semantic_case_match_count == 11


def test_failed_negative_case_is_not_misreported_as_correct_abstention() -> None:
    benchmark = loaded()
    predictions = {
        case.case_id: case.expected_proposals for case in benchmark.corpus.cases
    }
    negative = next(
        case for case in benchmark.corpus.cases if case.case_id == "negative_generic"
    )
    predictions[negative.case_id] = ()

    score = score_component_benchmark(
        benchmark.corpus,
        predictions,
        failed_case_ids={negative.case_id},
    )

    assert score.failed_case_count == 1
    assert score.failed_abstention_case_count == 1
    assert score.correct_abstention_count == 1
    assert score.correct_abstention_rate == 0.5
    assert score.exact_case_match_count == 11
    assert score.semantic_case_match_count == 11


def test_failed_positive_case_counts_as_unresolved_false_negative() -> None:
    benchmark = loaded()
    predictions = {
        case.case_id: case.expected_proposals for case in benchmark.corpus.cases
    }
    positive = next(case for case in benchmark.corpus.cases if case.expected_proposals)
    predictions[positive.case_id] = ()

    score = score_component_benchmark(
        benchmark.corpus,
        predictions,
        failed_case_ids={positive.case_id},
    )

    assert score.failed_case_count == 1
    assert score.false_negative_count == 1
    assert score.semantic_false_negative_count == 1
    assert score.exact_case_match_count == 11
    assert score.semantic_case_match_count == 11


def test_missing_case_predictions_fail_instead_of_silently_improving_score() -> None:
    benchmark = loaded()
    predictions = {
        case.case_id: case.expected_proposals for case in benchmark.corpus.cases[:-1]
    }

    with pytest.raises(BenchmarkCorpusError, match="exact case set"):
        score_component_benchmark(benchmark.corpus, predictions)


def test_corpus_rejects_non_exact_expected_span(tmp_path: Path) -> None:
    payload = json.loads(FIXTURE.read_text(encoding="utf-8"))
    payload["cases"][0]["expected_proposals"][0]["start"] = 19
    path = tmp_path / "bad.json"
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")

    with pytest.raises(BenchmarkCorpusError, match="exact source span"):
        load_component_benchmark(path)


def test_corpus_rejects_real_looking_operation_code(tmp_path: Path) -> None:
    payload = json.loads(FIXTURE.read_text(encoding="utf-8"))
    payload["cases"][0]["operation_code"] = "PACS-FC-REAL"
    path = tmp_path / "bad.json"
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")

    with pytest.raises(BenchmarkCorpusError, match="synthetic BENCH"):
        load_component_benchmark(path)


def test_execution_report_binds_model_runtime_corpus_and_measurements() -> None:
    benchmark = loaded()
    identity = LocalModelIdentity(
        model_id="fixture/model:Q4",
        artifact_sha256="a" * 64,
    )
    results: dict[str, LlamaBenchmarkResult] = {}

    for index, case in enumerate(benchmark.corpus.cases):
        request = benchmark_request(case)
        results[case.case_id] = LlamaBenchmarkResult(
            batch=ModelProposalBatch(
                operation_code=request.operation_code,
                source_sha256=request.source_sha256,
                model_identity=identity,
                proposals=case.expected_proposals,
            ),
            cache_key=f"key-{index}",
            cache_hit=index == 0,
            elapsed_seconds=None if index == 0 else float(index),
            llama_cli_sha256="b" * 64,
        )

    report = build_component_benchmark_report(benchmark, results)

    assert report.schema_version == "component-benchmark-report-v4"
    assert report.corpus_sha256 == benchmark.sha256
    assert report.model_id == "fixture/model:Q4"
    assert report.model_artifact_sha256 == "a" * 64
    assert report.llama_cli_sha256 == "b" * 64
    assert report.score.exact_case_match_rate == 1.0
    assert report.score.semantic_case_match_rate == 1.0
    assert report.score.failed_case_count == 0
    assert len(report.case_results) == 12
    assert all(case_result.exact_match for case_result in report.case_results)
    assert all(case_result.semantic_match for case_result in report.case_results)
    assert all(case_result.inference_error is None for case_result in report.case_results)
    assert (
        report.case_results[0].expected_proposals
        == benchmark.corpus.cases[0].expected_proposals
    )
    assert (
        report.case_results[0].predicted_proposals
        == benchmark.corpus.cases[0].expected_proposals
    )
    assert report.case_results[0].cache_hit is True
    assert report.case_results[0].elapsed_seconds is None
    assert report.cache_hit_count == 1
    assert report.inference_count == 11
    assert report.median_elapsed_seconds == 6.0
    assert report.max_elapsed_seconds == 11.0


def test_execution_report_marks_failure_non_matching_and_retains_error() -> None:
    benchmark = loaded()
    identity = LocalModelIdentity(
        model_id="fixture/model:Q4",
        artifact_sha256="a" * 64,
    )
    results: dict[str, LlamaBenchmarkResult] = {}
    failed_case = benchmark.corpus.cases[0]

    for index, case in enumerate(benchmark.corpus.cases):
        request = benchmark_request(case)
        proposals = () if case.case_id == failed_case.case_id else case.expected_proposals
        results[case.case_id] = LlamaBenchmarkResult(
            batch=ModelProposalBatch(
                operation_code=request.operation_code,
                source_sha256=request.source_sha256,
                model_identity=identity,
                proposals=proposals,
            ),
            cache_key=f"key-{index}",
            cache_hit=False,
            elapsed_seconds=0.1,
            llama_cli_sha256="b" * 64,
        )

    report = build_component_benchmark_report(
        benchmark,
        results,
        failures={failed_case.case_id: "LlamaAdapterError: invalid token range"},
    )

    case_result = next(
        item for item in report.case_results if item.case_id == failed_case.case_id
    )
    assert report.score.failed_case_count == 1
    assert case_result.exact_match is False
    assert case_result.semantic_match is False
    assert case_result.inference_error == "LlamaAdapterError: invalid token range"


def test_execution_report_rejects_mixed_runtime_hashes() -> None:
    benchmark = loaded()
    identity = LocalModelIdentity(
        model_id="fixture/model:Q4",
        artifact_sha256="a" * 64,
    )
    results: dict[str, LlamaBenchmarkResult] = {}

    for index, case in enumerate(benchmark.corpus.cases):
        request = benchmark_request(case)
        results[case.case_id] = LlamaBenchmarkResult(
            batch=ModelProposalBatch(
                operation_code=request.operation_code,
                source_sha256=request.source_sha256,
                model_identity=identity,
                proposals=case.expected_proposals,
            ),
            cache_key=f"key-{index}",
            cache_hit=False,
            elapsed_seconds=0.1,
            llama_cli_sha256=("b" * 64 if index else "c" * 64),
        )

    with pytest.raises(BenchmarkCorpusError, match="one exact model and llama runtime"):
        build_component_benchmark_report(benchmark, results)
