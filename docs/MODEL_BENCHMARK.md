# Local component-model benchmark adapter

Status date: 2026-09-02.

## Purpose

The local model is a Phase C fallback proposal mechanism. It is not a procurement-state classifier
and it is not a production dependency.

`src/procrun/llama_adapter.py` is benchmark-only. It accepts only model registry entries whose status
is `BENCHMARK_CANDIDATE`; an `APPROVED` artifact requires a separate production path and explicit
governance change.

Current selected candidate:

- `mistralai/Ministral-3-3B-Instruct-2512-GGUF:Q4_K_M`
- artifact SHA-256:
  `9ed150d4367e68df0ac8e1540f6ddc65b42d0ee26378329d1ecbca60f93fc5f8`
- artifact size: `2,147,023,008` bytes
- weights remain outside Git.

Historical Qwen candidate:

- `Qwen/Qwen3-4B-GGUF:Q4_K_M`
- registry status: `INCONCLUSIVE` after correcting the benchmark/product-contract mismatch described
  below.

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

## Generated output contract and evidence integrity

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
canonical evidence deterministically from the original request text and revalidates that evidence
against the supplied unmatched span. The model therefore cannot paraphrase, translate, normalize or
invent evidence text.

The canonical production-side fallback validator accepts any exact source substring contained inside
one deterministic unmatched scope span. It does **not** require the model to reproduce a separately
annotated minimal noun phrase. The deterministic rule engine also stores sentence-level supporting
scope evidence. This distinction matters for benchmark interpretation.

An empty proposal list is valid. It means the fallback did not resolve that scope. It never means that
no component exists.

## Two separate quality questions

Report schema v4 deliberately separates two questions that earlier reports conflated:

1. **Semantic quality** — did the model select the frozen `domain + category` expected for the
   component, and did it abstain on negative cases?
2. **Legacy minimal-phrase exactness** — did the generated exact source substring happen to equal the
   corpus's annotated minimal phrase byte-for-byte?

The first question matches the model's product role. The second remains useful diagnostic information,
but it is stricter than the canonical fallback acceptance rule and is not a production quality gate.

Semantic scoring is not fuzzy matching. A semantic true positive still requires the exact frozen
`domain + category` pair. Wrong category, extra category, missing category, malformed output and false
positive abstention behavior remain explicit failures.

Evidence safety is not scored loosely either: the adapter/canonical validator must still prove that
every accepted source substring is exact source text within a supplied unmatched span. Semantic credit
cannot rescue invalid or hallucinated evidence.

## Per-case failure scoring

A malformed model response is benchmark evidence, not a reason to discard the rest of a paid corpus
run. Report v4 retains the v3 fail-closed behavior: adapter/model-output failures are recorded per
synthetic case and the runner continues with remaining cases.

For a failed case:

- the accepted proposal set is empty;
- `inference_error` records the fail-closed adapter reason;
- the case cannot count as either an exact or semantic match;
- expected positive categories count as semantic false negatives; and
- a failed negative case cannot count as a correct abstention.

Only `LlamaAdapterError` is converted into a scored case failure. Programming errors, corpus invariant
violations and report/provenance failures still abort the run rather than being hidden as model
quality.

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

The 2026-09-02 target-host session completed both:

- `component_benchmark_v1.json` — primary diagnostic/regression corpus; and
- `component_benchmark_holdout_v1.json` — disjoint holdout corpus.

Both used the same verified Ministral artifact and llama.cpp runtime. There were zero adapter-failed
cases in either corpus.

Re-scoring those already-generated proposals by frozen `domain + category` gives:

| Corpus | Semantic TP | Semantic FP | Semantic FN | Precision | Recall | Negative abstention |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Primary | 5 | 1 | 5 | 83.3% | 50.0% | 2/2 |
| Holdout | 7 | 1 | 3 | 87.5% | 70.0% | 2/2 |

Median per-case inference latency was about 41.8 seconds on primary and 42.8 seconds on holdout;
maximum latency was about 47.0 and 48.7 seconds respectively.

These numbers are **diagnostic only**. The semantic scoring interpretation was corrected after the
current outputs had been observed, so the current holdout cannot be reused as independent production
approval evidence under the new interpretation.

## Qwen status correction

The earlier Qwen runs remain valid historical measurements, including resource behavior, category
choices and malformed token output. What changes is the governance conclusion.

The previous `REJECTED` decision relied materially on minimal-phrase exact-match counts, even though
the canonical fallback contract accepts broader/narrower exact source substrings inside the supplied
unmatched span. Qwen is therefore changed to `INCONCLUSIVE`, not restored as the selected candidate and
not approved.

No additional paid Qwen run is planned now.

## Production approval remains closed

The selected Ministral artifact stays `BENCHMARK_CANDIDATE`. Before production approval, at minimum a
fresh evaluation must be frozen **before** new model outputs are inspected and must measure:

1. exact frozen `domain + category` semantic precision/recall/F1;
2. false-positive and negative-abstention behavior;
3. malformed/failed cases;
4. adapter/canonical evidence-integrity failures;
5. target-host RAM, swap and latency;
6. exact llama.cpp/model/evaluation provenance; and
7. an explicit registry/governance decision.

The existing synthetic results are sufficient to diagnose the scoring issue. Do not spend another
Hetzner run merely to regenerate the same primary/holdout under report v4.
