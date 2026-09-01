import hashlib
from datetime import date
from pathlib import Path

from procrun import benchmark_runner, model_benchmark, model_fallback, model_registry
from procrun.llama_adapter import LlamaBenchmarkConfig, LlamaBenchmarkResult

LocalModelIdentity = model_fallback.LocalModelIdentity
ModelArtifactSpec = model_registry.ModelArtifactSpec
ModelApprovalStatus = model_registry.ModelApprovalStatus

FIXTURE = Path(__file__).parent / "fixtures" / "component_benchmark_v1.json"


def test_one_command_runner_writes_complete_hash_bound_report(tmp_path: Path) -> None:
    loaded = model_benchmark.load_component_benchmark(FIXTURE)
    expected_by_operation = {
        case.operation_code: case.expected_proposals for case in loaded.corpus.cases
    }
    model_bytes = b"benchmark-fixture-model"
    cli_bytes = b"benchmark-fixture-cli"
    model_path = tmp_path / "fixture.gguf"
    cli_path = tmp_path / "llama-cli"
    output_path = tmp_path / "report.json"
    model_path.write_bytes(model_bytes)
    cli_path.write_bytes(cli_bytes)
    cli_path.chmod(0o755)

    spec = ModelArtifactSpec(
        repository="fixture/model",
        revision="a" * 40,
        filename="fixture.gguf",
        identity=LocalModelIdentity(
            model_id="fixture/model:Q4",
            artifact_sha256=hashlib.sha256(model_bytes).hexdigest(),
        ),
        size_bytes=len(model_bytes),
        license_id="Apache-2.0",
        license_url="https://example.invalid/model-license",
        commercial_use_allowed=True,
        license_reviewed_on=date(2026, 9, 1),
        license_review_due_on=date(2026, 11, 30),
        status=ModelApprovalStatus.BENCHMARK_CANDIDATE,
    )

    def fake_case_runner(request, runtime, *, cache_dir=None):
        del cache_dir
        return LlamaBenchmarkResult(
            batch=model_fallback.ModelProposalBatch(
                operation_code=request.operation_code,
                source_sha256=request.source_sha256,
                model_identity=runtime.model_spec.identity,
                proposals=expected_by_operation[request.operation_code],
            ),
            cache_key=f"cache-{request.operation_code}",
            cache_hit=False,
            elapsed_seconds=0.25,
            llama_cli_sha256=runtime.llama_cli_sha256,
        )

    report = benchmark_runner.run_registered_component_benchmark(
        corpus_path=FIXTURE,
        llama_cli_path=cli_path,
        model_path=model_path,
        output_path=output_path,
        model_spec=spec,
        config=LlamaBenchmarkConfig(max_memory_mb=6144),
        case_runner=fake_case_runner,
    )

    written = model_benchmark.ComponentBenchmarkReport.model_validate_json(
        output_path.read_text(encoding="utf-8")
    )
    assert written == report
    assert report.corpus_sha256 == loaded.sha256
    assert report.score.exact_case_match_rate == 1.0
    assert report.inference_count == 12
    assert report.cache_hit_count == 0
    assert report.median_elapsed_seconds == 0.25
    assert report.max_elapsed_seconds == 0.25


def test_report_write_is_atomic_and_creates_parent_directory(tmp_path: Path) -> None:
    loaded = model_benchmark.load_component_benchmark(FIXTURE)
    identity = LocalModelIdentity(
        model_id="fixture/model:Q4",
        artifact_sha256="a" * 64,
    )
    results = {}
    for case in loaded.corpus.cases:
        request = model_benchmark.benchmark_request(case)
        results[case.case_id] = LlamaBenchmarkResult(
            batch=model_fallback.ModelProposalBatch(
                operation_code=request.operation_code,
                source_sha256=request.source_sha256,
                model_identity=identity,
                proposals=case.expected_proposals,
            ),
            cache_key=case.case_id,
            cache_hit=False,
            elapsed_seconds=0.1,
            llama_cli_sha256="b" * 64,
        )
    report = model_benchmark.build_component_benchmark_report(loaded, results)
    output = tmp_path / "nested" / "report.json"

    benchmark_runner.write_benchmark_report(report, output)

    assert output.is_file()
    assert not list(output.parent.glob("*.tmp"))
