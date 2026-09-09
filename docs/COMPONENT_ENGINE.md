# ProcRun component engine

Status date: 2026-09-09
Status: **A21 V2 REMEDIATION IN VALIDATION**

## Governing rule

The component engine converts only approved funded-project scope text into evidence-backed purchasable component categories. It is not a generic LLM decomposition layer and it is not a TED-only demand extractor.

Current remediation rule version: `component-taxonomy-v2`.

## Frozen domains

- `water_wastewater`
- `rail_transport`
- `ports_coastal`
- `energy_efficiency`
- `resilience_fire`

The v2 deterministic phrase layer retains the existing Portuguese/English rules and adds conservative Italian extraction vocabulary for the A21 Italian validation corpus. Domain selection remains explicit input; the engine does not silently guess a domain from arbitrary text.

`energy_efficiency:battery_storage` is added as an explicit frozen category because the A21 blind source-text adjudication exposed source-evidenced battery-storage demand that v1 could not represent.

## Evidence contract

Every accepted deterministic component retains the exact contiguous source-text sentence that justified it, including source offsets. Multiple matches for the same domain/category canonicalise to one component while preserving all evidence spans.

Component IDs are deterministic SHA-256-derived identifiers over:

`rule_version | operation_code | domain | category`

A component label is a ProcRun transformation, not a verbatim source fact. Customer-facing trust language must therefore say that the component is **source-evidenced**, not that the source itself published the canonical ProcRun category.

## Zero-invented-demand invariant

A component may exist only when:

1. a deterministic frozen rule matches accepted project scope; or
2. an approved local-model fallback proposes a frozen category and an exact verbatim source span, and deterministic validation accepts both.

No evidence span means no accepted component. Unsupported model text is rejected.

## Unmatched scope

The deterministic dictionary is not assumed complete. Every non-empty source sentence without a deterministic match is retained as `unmatched_scope_span` and sets `model_fallback_required=True`.

No deterministic match never means `no components` or `no demand`.

## Local-model handoff

A production-approved model may only:

- inspect already allowlisted project scope text;
- propose a category from the frozen taxonomy;
- return the exact supporting source span;
- submit the proposal to deterministic canonicalisation.

It may not create source text, assign procurement evidence, set component state, set project state or override matching/coverage gates. Ambiguous output remains unresolved.

The v2 model-category guidance must cover the exact v2 taxonomy, including `energy_efficiency:battery_storage`.

## CPV use

CPV prefixes are category hints, never standalone evidence that a funded-project component has entered procurement. Battery storage is intentionally added without inventing a new CPV mapping; a future CPV mapping requires separate qualification.

## Fail-closed invariants

- Empty domain input is rejected rather than guessed.
- No deterministic match triggers unresolved/fallback handling, never absence-of-demand.
- Exact source spans are retained and hash/version bound.
- Component extraction never assigns OPEN/CLOSED.
- CPV agreement never establishes CLOSED by itself.
- Model output cannot bypass exact-span/category validation.
- Taxonomy changes require explicit versioning and regression tests.
- The separately frozen A21 holdout must not be used to author v2 rules.
