"""Benchmark-only llama.cpp adapter for local component proposals."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import tempfile
import time
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from procrun.domain import StrictModel
from procrun.model_fallback import (
    LocalModelRequest,
    ModelComponentProposal,
    ModelProposalBatch,
)
from procrun.model_registry import (
    ModelApprovalStatus,
    ModelArtifactSpec,
    verify_local_model_artifact,
)

LLAMA_ADAPTER_VERSION = "llama-component-benchmark-v4"


class LlamaAdapterError(RuntimeError):
    """Raised when the benchmark adapter cannot produce a validated proposal batch."""


class GeneratedProposalEnvelope(StrictModel):
    """The only structure the model itself is allowed to generate."""

    proposals: tuple[ModelComponentProposal, ...] = ()


@dataclass(frozen=True)
class LlamaBenchmarkConfig:
    """Resource and determinism bounds for one benchmark inference."""

    threads: int = 4
    context_size: int = 4096
    max_output_tokens: int = 768
    timeout_seconds: float = 120.0
    seed: int = 0
    max_proposals: int = 32
    max_stdout_bytes: int = 256 * 1024
    max_stderr_bytes: int = 2 * 1024 * 1024
    max_cache_record_bytes: int = 512 * 1024
    max_cache_entries: int = 256
    max_memory_mb: int = 6 * 1024

    def __post_init__(self) -> None:
        positive_ints = (
            self.threads,
            self.context_size,
            self.max_output_tokens,
            self.max_proposals,
            self.max_stdout_bytes,
            self.max_stderr_bytes,
            self.max_cache_record_bytes,
            self.max_cache_entries,
            self.max_memory_mb,
        )
        if any(value <= 0 for value in positive_ints):
            raise ValueError("llama benchmark integer limits must all be positive")
        if self.max_memory_mb < 1024:
            raise ValueError("llama benchmark max_memory_mb must be at least 1024")
        if self.timeout_seconds <= 0:
            raise ValueError("llama benchmark timeout_seconds must be positive")
        if self.seed < 0:
            raise ValueError("llama benchmark seed must be non-negative")


@dataclass(frozen=True)
class PreparedLlamaRuntime:
    """Verified local bytes used for a benchmark run."""

    llama_cli_path: Path
    llama_cli_sha256: str
    model_path: Path
    model_spec: ModelArtifactSpec
    config: LlamaBenchmarkConfig


@dataclass(frozen=True)
class ProcessResult:
    returncode: int
    stdout: bytes
    stderr: bytes
    elapsed_seconds: float


ProcessInvoker = Callable[
    [tuple[str, ...], Mapping[str, str], float, int],
    ProcessResult,
]


@dataclass(frozen=True)
class LlamaBenchmarkResult:
    batch: ModelProposalBatch
    cache_key: str
    cache_hit: bool
    elapsed_seconds: float | None
    llama_cli_sha256: str


class _CacheRecord(StrictModel):
    adapter_version: str
    cache_key: str
    batch: ModelProposalBatch


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def prepare_llama_benchmark_runtime(
    *,
    llama_cli_path: Path,
    model_path: Path,
    model_spec: ModelArtifactSpec,
    config: LlamaBenchmarkConfig | None = None,
) -> PreparedLlamaRuntime:
    """Verify exact local model/runtime bytes before any benchmark inference."""

    if model_spec.status is not ModelApprovalStatus.BENCHMARK_CANDIDATE:
        raise LlamaAdapterError(
            "benchmark adapter accepts BENCHMARK_CANDIDATE model artifacts only"
        )

    actual_config = config if config is not None else LlamaBenchmarkConfig()
    resolved_cli = llama_cli_path.resolve()
    resolved_model = model_path.resolve()
    if not resolved_cli.is_file():
        raise LlamaAdapterError(f"llama-cli binary does not exist: {resolved_cli}")
    if os.name == "posix" and not os.access(resolved_cli, os.X_OK):
        raise LlamaAdapterError(f"llama-cli binary is not executable: {resolved_cli}")

    verify_local_model_artifact(resolved_model, model_spec)
    return PreparedLlamaRuntime(
        llama_cli_path=resolved_cli,
        llama_cli_sha256=_sha256_file(resolved_cli),
        model_path=resolved_model,
        model_spec=model_spec,
        config=actual_config,
    )


def _canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def benchmark_cache_key(
    request: LocalModelRequest,
    runtime: PreparedLlamaRuntime,
) -> str:
    """Bind cached output to request, exact binaries and inference settings."""

    payload = {
        "adapter_version": LLAMA_ADAPTER_VERSION,
        "request": request.model_dump(mode="json"),
        "model_id": runtime.model_spec.identity.model_id,
        "model_sha256": runtime.model_spec.identity.artifact_sha256,
        "llama_cli_sha256": runtime.llama_cli_sha256,
        "config": {
            "threads": runtime.config.threads,
            "context_size": runtime.config.context_size,
            "max_output_tokens": runtime.config.max_output_tokens,
            "seed": runtime.config.seed,
            "max_proposals": runtime.config.max_proposals,
            "max_memory_mb": runtime.config.max_memory_mb,
            "reasoning": "off",
            "temperature": 0,
            "top_k": 1,
            "top_p": 1,
            "min_p": 0,
            "offline": True,
        },
    }
    return hashlib.sha256(_canonical_json(payload).encode("utf-8")).hexdigest()


def _output_schema(
    request: LocalModelRequest,
    config: LlamaBenchmarkConfig,
) -> str:
    domains = sorted({domain.value for domain in request.domains})
    categories = sorted({item.category for item in request.allowed_categories})
    schema = {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "proposals": {
                "type": "array",
                "maxItems": config.max_proposals,
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "domain": {"type": "string", "enum": domains},
                        "category": {"type": "string", "enum": categories},
                        "start": {"type": "integer", "minimum": 0},
                        "end": {"type": "integer", "minimum": 0},
                        "source_text": {"type": "string", "minLength": 1},
                    },
                    "required": [
                        "domain",
                        "category",
                        "start",
                        "end",
                        "source_text",
                    ],
                },
            }
        },
        "required": ["proposals"],
    }
    return _canonical_json(schema)


def _prompt(request: LocalModelRequest) -> str:
    input_json = _canonical_json(request.model_dump(mode="json"))
    return (
        "Classify only the supplied unmatched project-scope spans into the supplied "
        "allowed component categories. Each proposal must represent a concrete "
        "purchasable component, system, equipment item, or scoped works package that is "
        "explicitly named in the text. Use exactly one allowed domain/category pair. "
        "For source_text, return the shortest contiguous phrase that directly names the "
        "proposed component; never copy the surrounding sentence merely as evidence. "
        "start/end must be the absolute offsets of that exact shortest phrase. Prefer "
        "the narrowest defensible category based on the named component, not broad project "
        "context. Return an empty proposals array when the text only describes maintenance, "
        "generic or undefined technical activities, or otherwise does not explicitly name "
        "a concrete component or scoped works package. Do not infer procurement status, "
        "opportunity state, buyer contacts, dates, values, or facts absent from the input. "
        "If either the category or exact minimal span cannot be identified defensibly, omit "
        "the proposal. Return only JSON matching the constrained schema; do not emit "
        "reasoning or commentary. /no_think\nINPUT_JSON:\n"
        f"{input_json}"
    )


def _sanitized_environment() -> dict[str, str]:
    blocked_prefixes = (
        "LLAMA_ARG_",
        "HF_",
        "HUGGING_FACE_",
    )
    blocked_exact = {
        "HTTP_PROXY",
        "HTTPS_PROXY",
        "ALL_PROXY",
        "NO_PROXY",
    }
    env = {
        key: value
        for key, value in os.environ.items()
        if not key.upper().startswith(blocked_prefixes)
        and key.upper() not in blocked_exact
    }
    env["NO_COLOR"] = "1"
    return env


def _posix_memory_limiter(max_memory_mb: int) -> Callable[[], None] | None:
    if os.name != "posix":
        return None

    max_bytes = max_memory_mb * 1024 * 1024

    def apply_limit() -> None:
        import resource

        resource.setrlimit(resource.RLIMIT_AS, (max_bytes, max_bytes))

    return apply_limit


def _invoke_process(
    argv: tuple[str, ...],
    env: Mapping[str, str],
    timeout_seconds: float,
    max_memory_mb: int,
) -> ProcessResult:
    started = time.perf_counter()
    try:
        completed = subprocess.run(
            argv,
            stdin=subprocess.DEVNULL,
            capture_output=True,
            env=dict(env),
            timeout=timeout_seconds,
            check=False,
            preexec_fn=_posix_memory_limiter(max_memory_mb),
        )
    except subprocess.TimeoutExpired as exc:
        raise LlamaAdapterError(
            f"llama-cli exceeded benchmark timeout of {timeout_seconds:g}s"
        ) from exc
    except OSError as exc:
        raise LlamaAdapterError(f"llama-cli could not be started: {exc}") from exc

    return ProcessResult(
        returncode=completed.returncode,
        stdout=completed.stdout,
        stderr=completed.stderr,
        elapsed_seconds=time.perf_counter() - started,
    )


def _invoke_llama(
    request: LocalModelRequest,
    runtime: PreparedLlamaRuntime,
    invoker: ProcessInvoker,
) -> ProcessResult:
    with tempfile.TemporaryDirectory(prefix="procrun-llama-") as directory:
        workdir = Path(directory)
        prompt_file = workdir / "prompt.txt"
        schema_file = workdir / "output-schema.json"
        prompt_file.write_text(_prompt(request), encoding="utf-8")
        schema_file.write_text(
            _output_schema(request, runtime.config),
            encoding="utf-8",
        )

        argv = (
            str(runtime.llama_cli_path),
            "--offline",
            "-m",
            str(runtime.model_path),
            "--threads",
            str(runtime.config.threads),
            "--ctx-size",
            str(runtime.config.context_size),
            "--n-predict",
            str(runtime.config.max_output_tokens),
            "--seed",
            str(runtime.config.seed),
            "--temp",
            "0",
            "--top-k",
            "1",
            "--top-p",
            "1",
            "--min-p",
            "0",
            "--reasoning",
            "off",
            "--reasoning-budget",
            "0",
            "--single-turn",
            "--no-display-prompt",
            "--log-verbosity",
            "1",
            "--color",
            "off",
            "--file",
            str(prompt_file),
            "--json-schema-file",
            str(schema_file),
        )
        return invoker(
            argv,
            _sanitized_environment(),
            runtime.config.timeout_seconds,
            runtime.config.max_memory_mb,
        )


def _parse_generated_output(
    request: LocalModelRequest,
    runtime: PreparedLlamaRuntime,
    process: ProcessResult,
) -> GeneratedProposalEnvelope:
    if len(process.stdout) > runtime.config.max_stdout_bytes:
        raise LlamaAdapterError("llama-cli stdout exceeded the configured byte limit")
    if len(process.stderr) > runtime.config.max_stderr_bytes:
        raise LlamaAdapterError("llama-cli stderr exceeded the configured byte limit")
    if process.returncode != 0:
        stderr = process.stderr.decode("utf-8", errors="replace").strip()
        suffix = stderr[-1000:] if stderr else "no stderr"
        raise LlamaAdapterError(
            f"llama-cli exited with code {process.returncode}: {suffix}"
        )

    try:
        decoded = process.stdout.decode("utf-8", errors="strict").strip()
    except UnicodeDecodeError as exc:
        raise LlamaAdapterError("llama-cli stdout is not valid UTF-8") from exc

    completion_eog_suffix = " [end of text]"
    if decoded.endswith(completion_eog_suffix):
        decoded = decoded[: -len(completion_eog_suffix)].rstrip()
    if not decoded:
        raise LlamaAdapterError("llama-cli returned an empty response")

    try:
        payload = json.loads(decoded)
        envelope = GeneratedProposalEnvelope.model_validate(payload)
    except ValueError as exc:
        raise LlamaAdapterError(
            "llama-cli response is not the strict proposal JSON contract"
        ) from exc

    if len(envelope.proposals) > runtime.config.max_proposals:
        raise LlamaAdapterError("llama-cli returned too many component proposals")
    return _validate_against_request(request, envelope)


def _validate_against_request(
    request: LocalModelRequest,
    envelope: GeneratedProposalEnvelope,
) -> GeneratedProposalEnvelope:
    allowed_pairs = {
        (item.domain, item.category)
        for item in request.allowed_categories
    }
    allowed_domains = frozenset(request.domains)
    unique: dict[
        tuple[str, str, int, int, str],
        ModelComponentProposal,
    ] = {}

    for proposal in envelope.proposals:
        if proposal.domain not in allowed_domains:
            raise LlamaAdapterError("model proposal domain is outside the request")
        if (proposal.domain, proposal.category) not in allowed_pairs:
            raise LlamaAdapterError(
                "model proposal domain/category pair is outside the request"
            )
        if proposal.start >= proposal.end:
            raise LlamaAdapterError("model proposal span must have positive length")

        containing = [
            span
            for span in request.unmatched_scope_spans
            if proposal.start >= span.start and proposal.end <= span.end
        ]
        if not containing:
            raise LlamaAdapterError(
                "model proposal is outside the supplied unmatched scope spans"
            )
        if not any(
            span.text[
                proposal.start - span.start : proposal.end - span.start
            ]
            == proposal.source_text
            for span in containing
        ):
            raise LlamaAdapterError(
                "model proposal source_text does not match its cited request span"
            )

        key = (
            proposal.domain.value,
            proposal.category,
            proposal.start,
            proposal.end,
            proposal.source_text,
        )
        unique[key] = proposal

    proposals = tuple(
        unique[key]
        for key in sorted(
            unique,
            key=lambda item: (item[2], item[3], item[0], item[1], item[4]),
        )
    )
    return GeneratedProposalEnvelope(proposals=proposals)


def _cache_path(cache_dir: Path, cache_key: str) -> Path:
    return cache_dir / f"{cache_key}.json"


def _read_cache(
    cache_dir: Path,
    cache_key: str,
    runtime: PreparedLlamaRuntime,
    request: LocalModelRequest,
) -> ModelProposalBatch | None:
    path = _cache_path(cache_dir, cache_key)
    if not path.exists():
        return None
    if not path.is_file():
        raise LlamaAdapterError(f"benchmark cache entry is not a file: {path}")
    if path.stat().st_size > runtime.config.max_cache_record_bytes:
        raise LlamaAdapterError("benchmark cache entry exceeds the configured byte limit")

    try:
        record = _CacheRecord.model_validate_json(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise LlamaAdapterError("benchmark cache entry is invalid") from exc
    if record.adapter_version != LLAMA_ADAPTER_VERSION:
        raise LlamaAdapterError("benchmark cache adapter version mismatch")
    if record.cache_key != cache_key:
        raise LlamaAdapterError("benchmark cache key mismatch")
    if record.batch.model_identity != runtime.model_spec.identity:
        raise LlamaAdapterError("benchmark cache model identity mismatch")
    if record.batch.operation_code != request.operation_code:
        raise LlamaAdapterError("benchmark cache operation_code mismatch")
    if record.batch.source_sha256 != request.source_sha256:
        raise LlamaAdapterError("benchmark cache source hash mismatch")

    validated = _validate_against_request(
        request,
        GeneratedProposalEnvelope(proposals=record.batch.proposals),
    )
    return record.batch.model_copy(update={"proposals": validated.proposals})


def _prune_cache(cache_dir: Path, max_entries: int) -> None:
    entries = sorted(
        (path for path in cache_dir.glob("*.json") if path.is_file()),
        key=lambda path: (path.stat().st_mtime_ns, path.name),
    )
    excess = len(entries) - max_entries
    for path in entries[: max(excess, 0)]:
        path.unlink(missing_ok=True)


def _write_cache(
    cache_dir: Path,
    cache_key: str,
    batch: ModelProposalBatch,
    runtime: PreparedLlamaRuntime,
) -> None:
    cache_dir.mkdir(parents=True, exist_ok=True)
    record = _CacheRecord(
        adapter_version=LLAMA_ADAPTER_VERSION,
        cache_key=cache_key,
        batch=batch,
    )
    encoded = record.model_dump_json().encode("utf-8")
    if len(encoded) > runtime.config.max_cache_record_bytes:
        raise LlamaAdapterError("benchmark cache record exceeds the configured byte limit")

    destination = _cache_path(cache_dir, cache_key)
    temporary = cache_dir / f".{cache_key}.{os.getpid()}.tmp"
    try:
        temporary.write_bytes(encoded)
        os.replace(temporary, destination)
        _prune_cache(cache_dir, runtime.config.max_cache_entries)
    except OSError as exc:
        temporary.unlink(missing_ok=True)
        raise LlamaAdapterError("benchmark cache entry could not be written") from exc


def run_llama_component_benchmark(
    request: LocalModelRequest,
    runtime: PreparedLlamaRuntime,
    *,
    cache_dir: Path | None = None,
    invoker: ProcessInvoker = _invoke_process,
) -> LlamaBenchmarkResult:
    """Run one local benchmark inference without assigning procurement state."""

    cache_key = benchmark_cache_key(request, runtime)
    if cache_dir is not None:
        cached = _read_cache(cache_dir, cache_key, runtime, request)
        if cached is not None:
            return LlamaBenchmarkResult(
                batch=cached,
                cache_key=cache_key,
                cache_hit=True,
                elapsed_seconds=None,
                llama_cli_sha256=runtime.llama_cli_sha256,
            )

    process = _invoke_llama(request, runtime, invoker)
    envelope = _parse_generated_output(request, runtime, process)
    batch = ModelProposalBatch(
        operation_code=request.operation_code,
        source_sha256=request.source_sha256,
        model_identity=runtime.model_spec.identity,
        proposals=envelope.proposals,
    )
    if cache_dir is not None:
        _write_cache(cache_dir, cache_key, batch, runtime)

    return LlamaBenchmarkResult(
        batch=batch,
        cache_key=cache_key,
        cache_hit=False,
        elapsed_seconds=process.elapsed_seconds,
        llama_cli_sha256=runtime.llama_cli_sha256,
    )
