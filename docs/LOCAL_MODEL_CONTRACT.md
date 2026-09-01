# Phase C local-model fallback contract

Status date: 2026-09-01.

## Purpose

The local model is a bounded component-proposal fallback. It is not a classifier, procurement search
engine or source parser. Deterministic extraction runs first; the model is invoked only for exact
allowlisted scope spans left unmatched by the frozen rule taxonomy.

Contract version: `local-component-proposal-v1`.

No model implementation or model weights are selected by this contract. The repository already ignores
`models/`, `*.gguf`, `*.safetensors`, `*.bin` and `*.onnx`; production weights must remain outside Git.

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

The model request contains only:

- operation code;
- scope-text SHA-256;
- explicitly selected infrastructure domains;
- the exact unmatched scope spans with source offsets; and
- allowed categories/labels from the frozen component taxonomy for those domains.

It does not contain funding beneficiary data, procurement evidence, procurement state, contacts, raw
HTTP bodies or source pages. The input is constructed only after the project record has passed the
existing allowlist boundary.

## Allowed output

A proposal has exactly five analytical fields:

- domain;
- frozen category;
- start offset;
- end offset; and
- exact source text.

Pydantic `extra=forbid` applies recursively. A model response that tries to add fields such as
`state=OPEN`, confidence, supplier, contact data or free-form evidence is schema-invalid.

## Validation gates

Before a proposal can become component evidence, all of the following must hold:

1. batch operation code matches the funding project;
2. batch source hash matches the current allowlisted scope text;
3. model ID, runtime and artifact SHA-256 match configured identity;
4. proposal domain was explicitly selected for the deterministic extraction;
5. proposal category exists in the frozen taxonomy for that domain;
6. offsets are valid and source text equals the exact substring at those offsets; and
7. the cited span lies inside a scope span that deterministic rules left unmatched.

Any failure rejects the batch/proposal before persistence. A proposal cannot rewrite a span already
covered by deterministic rules.

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

This contract contains no HTTP client, external inference API or automatic model download. A later
llama.cpp adapter must operate on a local file whose SHA-256 is checked before inference. Model choice,
license, GGUF availability, Portuguese quality and memory footprint are a separate evidence gate and
must be frozen before production inference is enabled.
