# Local component-model benchmark adapter

Status date: 2026-09-02.

## Purpose

The local model is a Phase C fallback proposal mechanism. It is not a procurement-state classifier
and it is not a production dependency.

`src/procrun/llama_adapter.py` is benchmark-only. It accepts only model registry entries whose status
is `BENCHMARK_CANDIDATE`; an `APPROVED` artifact requires a separate production path and explicit
governance change.

Current candidate:

- `Qwen/Qwen3-4B-GGUF:Q4_K_M`
- artifact SHA-256:
  `7485fe6f11af29433bc51cab58009521f205840f5b4ae3a32fa7f92e8534fdf5`
- weights remain outside Git.

## Input boundary

The model receives only the already constructed `LocalModelRequest`:

- operation code;
- source-scope SHA-256;
- selected frozen domains;
- unmatched allowlisted project-scope spans; and
- allowed frozen component categories.

Each allowed category is serialized with its human label and a computed model-facing
`selection_rule`. The rules are frozen as
`MODEL_CATEGORY_GUIDANCE_VERSION = "component-model-guidance-v1"` and cover the exact taxonomy.
They define category boundaries rather than benchmark-case answers. Import fails if the guidance set
and frozen taxonomy diverge.

The complete request, including these selection rules, is part of the deterministic cache key. A
change to category guidance therefore invalidates old cached model outputs without weakening runtime
validation.

The model does not receive raw HTTP bodies, HTML, PDFs, procurement state, contact records,
beneficiary contact data, or arbitrary source fields.

The prompt and JSON schema are temporary local files and are removed after each invocation.

## Runtime boundary

Before inference, the adapter verifies:

1. the exact local GGUF size and SHA-256;
2. the exact local `llama-cli` binary path; and
3. the SHA-256 of that runtime binary.

The process is launched without a shell and with explicit local model loading. The adapter passes
`--offline`, removes ambient Hugging Face/llama argument overrides and proxy variables, and does not
use remote-model flags.

Qwen reasoning is disabled twice: the prompt contains `/no_think`, while the runtime also receives
`--reasoning off` and `--reasoning-budget 0`.

Current deterministic generation settings are:

- threads: 4;
- context: 4096 tokens;
- maximum generated output: 768 tokens;
- seed: 0;
- temperature: 0;
- top-k: 1;
- top-p: 1;
- min-p: 0;
- timeout: 120 seconds;
- maximum proposals: 32.

On POSIX/Linux, the benchmark child process also receives a hard address-space limit. The default is
6144 MiB. On the 8 GiB CX33 target this deliberately leaves operating-system headroom.

## Output contract

Generation is constrained to one JSON object containing only `proposals`. Every proposal must contain:

- frozen domain;
- frozen category;
- absolute start offset;
- absolute end offset; and
- exact `source_text`.

Python then validates the output again. A proposal fails closed if its domain/category pair was not
allowed, its cited text is outside an unmatched request span, its source text does not exist as the
cited request evidence, extra fields are present, output is invalid UTF-8/JSON, configured byte limits
are exceeded, or the process fails.

When generated `source_text` occurs exactly once in the supplied unmatched spans, the adapter may
normalize incorrect model-provided absolute offsets to the uniquely determined exact source range.
Ambiguous repeated text is rejected rather than guessed.

An empty proposal list is valid. It means the fallback did not resolve that scope. It never means that
no component exists.

## Deterministic bounded cache

The optional cache key binds:

- adapter version;
- complete `LocalModelRequest`, including category selection rules;
- model ID and artifact SHA-256;
- `llama-cli` executable SHA-256;
- deterministic inference settings; and
- the benchmark memory bound.

Every cache hit is revalidated against the current request spans before it can be returned. Editing a
cache file therefore cannot bypass the source-span or taxonomy checks.

Cache records are size-limited and the directory is capped at 256 JSON entries by default. Cache data
is disposable runtime state and remains outside Git.

## Primary and holdout evaluation

The target-host run now executes both:

- `component_benchmark_v1.json` as the primary diagnostic/regression corpus; and
- `component_benchmark_holdout_v1.json` as a disjoint holdout corpus.

Both are run in one ephemeral CX33 session against the same verified model/runtime. Separate corpus
SHA-256 values, quality reports and GNU `time -v` resource reports are retained.

Improvement on the primary corpus alone is not independent evidence because that corpus informed the
error analysis that led to the taxonomy-guidance change. The holdout result must therefore be
inspected separately.

## Production approval remains closed

The candidate stays `BENCHMARK_CANDIDATE` until a later explicit decision. Before production approval,
at minimum the following evidence is still required:

1. a larger curated PII-safe Portuguese component-extraction evaluation set with frozen expected
   components and exact evidence spans;
2. accuracy/error analysis across primary and holdout data, including false proposals and unresolved
   behavior;
3. RAM and latency measurements on the actual target server;
4. exact llama.cpp runtime/model/corpus provenance; and
5. an explicit registry and governance change.

No numeric quality threshold is invented here because the governing requirements have not frozen one.
