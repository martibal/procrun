# Local component-model benchmark adapter

Status date: 2026-09-02.

## Purpose

The local model is a Phase C fallback proposal mechanism. It is not a procurement-state classifier
and it is not a production dependency.

`src/procrun/llama_adapter.py` is benchmark-only. It accepts only model registry entries whose status
is `BENCHMARK_CANDIDATE`; an `APPROVED` artifact requires a separate production path and explicit
governance change.

Current candidate:

- `mistralai/Ministral-3-3B-Instruct-2512-GGUF:Q4_K_M`
- artifact SHA-256:
  `9ed150d4367e68df0ac8e1540f6ddc65b42d0ee26378329d1ecbca60f93fc5f8`
- artifact size: `2,147,023,008` bytes
- weights remain outside Git.

Rejected measured candidate retained for provenance:

- `Qwen/Qwen3-4B-GGUF:Q4_K_M`
- status: `REJECTED` after the 2026-09-02 target-host quality runs.

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

Before the request is written to the temporary prompt, Python deterministically tokenizes each
unmatched scope span. The prompt includes the original span text plus an indexed token list. Token
indices are adapter-local evidence references; they do not replace the canonical character offsets in
the accepted `ModelComponentProposal` contract.

The complete request, including category selection rules, is part of the deterministic cache key.
Adapter v7 is separately bound into that key, so the model-neutral v7 prompt/cache contract cannot
reuse v6 outputs.

The model does not receive raw HTTP bodies, HTML, PDFs, procurement state, contact records,
beneficiary contact data, or arbitrary source fields.

The prompt and JSON schema are temporary local files and are removed after each invocation.

## Runtime boundary

Before inference, the adapter verifies:

1. the exact local GGUF size and SHA-256;
2. the exact local `llama-completion` binary path; and
3. the SHA-256 of that runtime binary.

The process is launched without a shell and with explicit local model loading. The adapter passes
`--offline`, removes ambient Hugging Face/llama argument overrides and proxy variables, and does not
use remote-model flags. Reasoning output is disabled through the pinned llama.cpp runtime flags so the
constrained JSON proposal is the only accepted output surface.

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

## Generated output contract

Generation is constrained to one JSON object containing only `proposals`. Every model-generated
proposal contains exactly:

- frozen domain;
- frozen category;
- `span_index` identifying one supplied unmatched scope span;
- inclusive `start_token`; and
- inclusive `end_token`.

The model does **not** generate source text and does not calculate character offsets. It selects only
a contiguous range of token identifiers that Python supplied with the original source span.

Python validates the domain/category pair, span index and token range. It then reconstructs the
canonical evidence deterministically from the original request text:

- absolute start offset = unmatched-span absolute start + first selected token start;
- absolute end offset = unmatched-span absolute start + last selected token end;
- `source_text` = the exact original substring between those two character positions.

The reconstructed `ModelComponentProposal` is then passed through exact request-span validation again.
The model therefore cannot paraphrase, translate, normalize or invent evidence text, and it does not
calculate Unicode character offsets. An invalid token range or disallowed category fails closed.

An empty proposal list is valid. It means the fallback did not resolve that scope. It never means that
no component exists.

## Per-case failure scoring

A malformed model response is benchmark evidence, not a reason to discard the rest of a paid corpus
run. The v3 benchmark report therefore records adapter/model-output failures per synthetic case and
continues with the remaining cases.

For a failed case:

- the accepted proposal set is empty;
- `inference_error` records the fail-closed adapter reason;
- the case can never count as an exact match;
- expected positive proposals count as false negatives; and
- a failed negative case can never count as a correct abstention.

Only `LlamaAdapterError` is converted into a scored case failure. Programming errors, corpus invariant
violations and report/provenance failures still abort the run rather than being hidden as model
quality.

This distinction exists so malformed token indices, invalid constrained JSON, runtime non-zero exits
and similar model/adapter failures remain visible while one failure no longer destroys all remaining
primary/holdout measurements.

## Deterministic bounded cache

The optional cache key binds:

- adapter version;
- complete `LocalModelRequest`, including category selection rules;
- model ID and artifact SHA-256;
- `llama-completion` executable SHA-256;
- deterministic inference settings;
- evidence-reference mode (`inclusive_token_indices`); and
- the benchmark memory bound.

The cache stores only canonical `ModelProposalBatch` records after Python has reconstructed exact
source evidence. Every cache hit is revalidated against the current request spans before it can be
returned. Failed outputs are not written as valid cache entries.

Cache records are size-limited and the directory is capped at 256 JSON entries by default. Cache data
is disposable runtime state and remains outside Git.

## Primary and holdout evaluation

The target-host run executes both:

- `component_benchmark_v1.json` as the primary diagnostic/regression corpus; and
- `component_benchmark_holdout_v1.json` as a disjoint holdout corpus.

Both are run in one ephemeral CX33 session against the same verified model/runtime. Separate corpus
SHA-256 values, quality reports and GNU `time -v` resource reports are retained.

The scoring contract remains strict: one true positive requires the exact frozen category and exact
frozen evidence span. No fuzzy credit is introduced after observing model behavior.

## Qwen3-4B empirical rejection

The exact pinned Qwen3-4B Q4_K_M artifact is no longer a candidate.

Observed evidence included:

- v5: only 2 exact positive hits from the 10 positive primary cases;
- v6 primary after taxonomy guidance/token evidence: 0 exact true positives from 10 positive cases,
  with 10 false positives and 10 false negatives under the frozen exact scoring contract;
- both v6 negative primary cases correctly abstained;
- v6 primary median inference latency about 42.0 seconds and maximum about 44.5 seconds per case;
- v6 holdout produced an out-of-range token reference before the old runner could complete the corpus;
- partial holdout peak RSS about 4.91 million KiB with zero swap on CX33.

The resource envelope was feasible, but the quality/output-validity evidence was not. The artifact is
therefore `REJECTED`; the primary benchmark will not be weakened to make it pass.

## Production approval remains closed

The selected Ministral artifact stays `BENCHMARK_CANDIDATE` until a later explicit decision. Before
production approval, at minimum the following evidence is still required:

1. complete primary and disjoint holdout results from the exact pinned artifact;
2. error analysis including malformed/failed cases, false proposals and unresolved behavior;
3. completed RAM and latency measurements on the actual target server;
4. exact llama.cpp runtime/model/corpus provenance; and
5. an explicit registry and governance change.

No numeric production threshold is invented here because the governing requirements have not frozen
one. A passing-looking small benchmark is evidence for a later decision, not automatic production
approval.
