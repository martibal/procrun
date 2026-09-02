# Phase C local-model fallback contract

Status date: 2026-09-02.

## Purpose

The local model is a bounded component-proposal fallback. It is not a procurement-state classifier,
procurement search engine or source parser. Deterministic extraction runs first; the model is invoked
only for exact allowlisted scope spans left unmatched by the frozen rule taxonomy.

Contract version: `local-component-proposal-v1`.

The accepted analytical contract remains independent of a particular model artifact. Model weights
remain outside Git; the repository ignores `models/`, `*.gguf`, `*.safetensors`, `*.bin` and `*.onnx`.

## Model identity

Every accepted model batch is bound to:

- a configured model ID;
- runtime `llama.cpp`;
- the lowercase SHA-256 digest of the exact local model artifact;
- the operation code;
- SHA-256 of the exact allowlisted project-scope text; and
- the frozen fallback-contract version.

A model-ID or artifact-hash mismatch rejects the entire batch before component construction. The
combined extractor version records the full model artifact SHA-256 so ledger component versions can
be reproduced against the exact model binary used.

## Minimal request surface

The canonical `LocalModelRequest` contains only:

- operation code;
- scope-text SHA-256;
- explicitly selected infrastructure domains;
- exact unmatched scope spans with source offsets; and
- allowed categories/labels from the frozen component taxonomy for those domains.

The benchmark adapter may derive deterministic token identifiers from those already allowlisted spans
before local inference. It does not introduce any additional source fields.

The request does not contain funding beneficiary data, procurement evidence, procurement state,
contacts, raw HTTP bodies or source pages. The input is constructed only after the project record has
passed the existing allowlist boundary.

## Local inference transport output

The benchmark adapter's v7 model-facing JSON transport is deliberately narrower than the canonical
proposal object. A generated proposal contains exactly:

- domain;
- frozen category;
- `span_index`;
- inclusive `start_token`; and
- inclusive `end_token`.

The model does not generate evidence text or character offsets. The adapter supplies indexed tokens
for each unmatched source span, and the model can only select one contiguous token range.

Python resolves those token references back to the original span and constructs the canonical
`ModelComponentProposal` with exactly five analytical fields:

- domain;
- frozen category;
- absolute start offset;
- absolute end offset; and
- exact source text copied from the original request span.

This separation is intentional: semantic selection is model work; evidence copying and Unicode
character-offset calculation are deterministic adapter work. Adapter v7 also removes the historical
Qwen-specific `/no_think` prompt directive so the benchmark prompt is model-neutral; deterministic
reasoning/output controls remain runtime-level llama.cpp settings.

## Validation gates

Before a proposal can become component evidence, all of the following must hold:

1. batch operation code matches the funding project;
2. batch source hash matches the current allowlisted scope text;
3. model ID, runtime and artifact SHA-256 match configured identity;
4. proposal domain was explicitly selected for deterministic extraction;
5. proposal category exists in the frozen taxonomy for that domain;
6. generated `span_index` and token range refer to a valid contiguous range in one supplied unmatched
   span;
7. Python reconstructs `source_text` and absolute offsets directly from that original span; and
8. the reconstructed canonical proposal passes exact source-substring and unmatched-span validation.

Pydantic `extra=forbid` applies recursively. A generated response that tries to add fields such as
`state=OPEN`, confidence, supplier, contact data or free-form evidence is schema-invalid. Invalid token
indices, inverted ranges, disallowed categories or tampered cached source text fail closed.

A proposal cannot rewrite a span already covered by deterministic rules.

## Benchmark failure semantics

A fail-closed model response remains invalid. The benchmark harness does not clamp an out-of-range
token index, guess an intended evidence span, or convert malformed output into a valid proposal.

For benchmark observability only, an adapter/model-output failure is retained as `inference_error` on
the affected synthetic case while the remaining corpus cases continue. A failed positive case remains
unresolved and its missing expected proposal is scored as a false negative. A failed negative case is
not counted as a correct abstention.

This continuation rule changes only benchmark reporting. It does not make failed output acceptable to
the analytical component pipeline.

## Canonicalisation

A valid proposal for a category already found by deterministic rules adds another exact evidence span
to the same deterministic component ID. A valid proposal for a new category constructs the same stable
ID formula used by the rule engine:

`SHA-256(rule_version | operation_code | domain | category)`.

The model therefore cannot create a parallel identity namespace or silently duplicate a component.

## Conservative completion rule

A model proposal can explain an unmatched span; an empty model response cannot certify that the span
contains no purchasable component. Any unmatched span with no accepted proposal remains unresolved and
`model_fallback_required=True`.

This is deliberately asymmetric. Model uncertainty can reduce publishable opportunity volume; it can
never turn missing scope understanding into an OPEN component.

## Runtime boundary

This contract contains no HTTP client or external inference API. The llama.cpp adapter operates on a
local model file whose exact size and SHA-256 are checked before inference, removes remote-model and
proxy configuration from the child environment, and runs with explicit offline/resource bounds.

Model approval remains a separate evidence gate. Licence, Portuguese quality, completed benchmark
results, target-host memory/latency and exact runtime provenance must all be evaluated before production
inference is enabled.
