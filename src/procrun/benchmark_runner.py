"""One-command runner for the frozen local component-model benchmark."""

from __future__ import annotations

import argparse
import os
from collections.abc import Callable
from pathlib import Path

from procrun.llama_adapter import (
    LlamaBenchmarkConfig,
    LlamaBenchmarkResult,
    PreparedLlamaRuntime,
    prepare_llama_benchmark_runtime,
    run_llama_component_benchmark,
)
from procrun.model_benchmark import (
    ComponentBenchmarkReport,
    LoadedBenchmarkCorpus,
    benchmark_request,
    build_component_benchmark_report,
    load_component_benchmark,
)
from procrun.model_registry import SELECTED_COMPONENT_MODEL, ModelArtifactSpec

CaseRunner = Callable[..., LlamaBenchmarkResult]


def execute_component_benchmark(
    loaded: LoadedBenchmarkCorpus,
    runtime: PreparedLlamaRuntime,
    *,
    cache_dir: Path | None = None,
    case_runner: CaseRunner = run_llama_component_benchmark,
) -> ComponentBenchmarkReport:
    """Execute every frozen case exactly once or satisfy it from the bound cache."""

    results: dict[str, LlamaBenchmarkResult] = {}
    for case in loaded.corpus.cases:
        results[case.case_id] = case_runner(
            benchmark_request(case),
            runtime,
            cache_dir=cache_dir,
        )
    return build_component_benchmark_report(loaded, results)


def write_benchmark_report(report: ComponentBenchmarkReport, output_path: Path) -> None:
    """Write one complete report atomically without leaving a partial JSON file."""

    output_path.parent.mkdir(parents=True, exist_ok=True)
    encoded = (report.model_dump_json(indent=2) + "\n").encode("utf-8")
    temporary = output_path.parent / f".{output_path.name}.{os.getpid()}.tmp"
    try:
        temporary.write_bytes(encoded)
        os.replace(temporary, output_path)
    except OSError:
        temporary.unlink(missing_ok=True)
        raise


def run_registered_component_benchmark(
    *,
    corpus_path: Path,
    llama_cli_path: Path,
    model_path: Path,
    output_path: Path,
    cache_dir: Path | None = None,
    model_spec: ModelArtifactSpec = SELECTED_COMPONENT_MODEL,
    config: LlamaBenchmarkConfig | None = None,
    case_runner: CaseRunner = run_llama_component_benchmark,
) -> ComponentBenchmarkReport:
    """Verify local artifacts, execute the frozen corpus, and persist the measured report."""

    loaded = load_component_benchmark(corpus_path)
    runtime = prepare_llama_benchmark_runtime(
        llama_cli_path=llama_cli_path,
        model_path=model_path,
        model_spec=model_spec,
        config=config,
    )
    report = execute_component_benchmark(
        loaded,
        runtime,
        cache_dir=cache_dir,
        case_runner=case_runner,
    )
    write_benchmark_report(report, output_path)
    return report


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="procrun-model-benchmark",
        description=(
            "Run the frozen PII-safe component benchmark against the pinned local model artifact."
        ),
    )
    parser.add_argument("--corpus", required=True, type=Path)
    parser.add_argument("--llama-cli", required=True, type=Path)
    parser.add_argument("--model", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--cache-dir", type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    report = run_registered_component_benchmark(
        corpus_path=args.corpus,
        llama_cli_path=args.llama_cli,
        model_path=args.model,
        output_path=args.output,
        cache_dir=args.cache_dir,
    )
    print(report.model_dump_json(indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
