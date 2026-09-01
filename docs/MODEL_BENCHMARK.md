# Local component-model benchmark adapter

Status date: 2026-09-01.

## Purpose

The local model is a fallback proposal mechanism for Phase C component extraction. It is not a
classifier for procurement state and it is not a production dependency yet.

The adapter in `src/procrun/llama_adapter.py` is deliberately benchmark-only. It can turn a
`LocalModelRequest` into a strict `ModelProposalBatch`, but it cannot assign `OPEN`, `CLOSED`,
`PARTIAL` or `UNRESOLVED`. Those semantics remain outside the model boundary.

Current registered model candidate:

- `Qwen/Qwen3-4B-GGUF:Q4_K_M`
- status: `BENCHMARK_CANDIDATE`
- artifact SHA-256:
  `7485fe6f11af29433bc51cab58009521f205840f5b4ae3a32fa7f92e8534fdf5`
- model weights remain outside Git.

No code path in this phase upgrades the candidate to `APPROVED`.

## Input boundary

The adapter receives only the already constructed `LocalModelRequest`:

- operation code;
- source-scope SHA-256;
- selected frozen domains;
- unmatched allowlisted project-scope spans; and
- allowed frozen component categories.

It does not receive raw HTTP bodies, HTML, PDFs, procurement status, contact records, beneficiary
contact data or arbitrary source fields.

The prompt is written to a temporary local file rather than placed directly in the process command
line. The JSON schema is also written to a temporary file. Both disappear when the invocation
returns.

## Runtime boundary

`prepare_llama_benchmark_runtime()` verifies the exact local GGUF bytes using the registry size and
SHA-256 before inference. It also hashes the exact local `llama-cli` executable.

The adapter invokes an explicit local executable path with `shell=False` semantics. It never uses
Hugging Face download flags or a remote model reference. Environment variables beginning with
`LLAMA_ARG_`, `HF_` or `HUGGING_FACE_` are removed so ambient configuration cannot silently change
the benchmark. Common proxy variables are also removed.

The current `llama-cli` interface was checked against the upstream llama.cpp CLI documentation on
2026-09-01. The adapter uses local model loading, single-turn generation and JSON-schema constrained
output.

## Deterministic benchmark defaults

Defaults are engineering bounds, not model-approval thresholds:

- threads: 4;
- context: 4096 tokens;
- maximum generated output: 768 tokens;
- seed: 0;
- temperature: 0;
- top-k: 1;
- top-p: 1;
- min-p: 0;
- timeout: 120 seconds;
- maximum proposals: 32;
- bounded stdout/stderr/cache record sizes.

The target server still needs an empirical RAM/latency benchmark. These defaults do not assert that
the current candidate fits the target machine with acceptable headroom.

## Output contract

Generation is constrained to one object containing only `proposals`. Every proposal must contain:

- frozen domain;
- frozen category;
- absolute start offset;
- absolute end offset; and
- exact `source_text`.

The adapter then validates the generated result again in Python. A proposal is rejected if:

- its domain/category pair was not present in the request;
- its offsets are outside an unmatched request span;
- its source text is not the exact substring identified by the offsets;
- extra output fields are present;
- output is not strict UTF-8 JSON;
- output exceeds configured bounds; or
- `llama-cli` fails.

An empty proposal list is valid. It means the fallback did not resolve that scope. It never means
"there is no component" and cannot manufacture an opportunity.

## Deterministic cache

The optional benchmark cache is local and stores only validated proposal batches. The cache key binds
all of the following:

- adapter version;
- complete `LocalModelRequest`;
- model ID;
- model artifact SHA-256;
- `llama-cli` executable SHA-256; and
- deterministic inference settings.

A cache record from a different model, runtime binary, request or settings therefore cannot be reused.
Cache records live under caller-supplied runtime storage and are already covered by the repository's
ignored runtime-data policy.

## Production approval remains closed

The model remains `BENCHMARK_CANDIDATE` until a later explicit change. Before any production approval,
at minimum the following evidence still has to be produced:

1. A curated PII-safe Portuguese component-extraction benchmark with frozen expected components and
   exact evidence spans.
2. Accuracy/error analysis against that frozen benchmark, including false component proposals and
   unresolved-rate behavior.
3. RAM and latency measurements on the actual target server configuration.
4. Exact llama.cpp runtime/container provenance in addition to the executable hash.
5. A documented approval decision and registry change.

No numeric quality or performance threshold is invented here because the governing requirements have
not frozen such thresholds yet.
