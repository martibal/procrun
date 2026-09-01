# Phase C component engine

Status date: 2026-09-01.

## Governing rule

Product Requirements v1.0 makes component decomposition a core product requirement. The MVP must
run deterministic phrase/rule extraction first. A local model may later propose additional components
and supporting source spans, but it may never assign OPEN, CLOSED or PARTIAL.

Current deterministic rule version: `component-taxonomy-v1`.

## Frozen initial domains

The initial taxonomy mirrors the five infrastructure domains in Product Requirements v1.0:

- `water_wastewater`
- `rail_transport`
- `ports_coastal`
- `energy_efficiency`
- `resilience_fire`

Each domain has explicit component families, Portuguese/English phrase rules and optional CPV-prefix
hints. Domain selection is an explicit input to the extractor. The rule engine does not infer a domain
from arbitrary free text because an incorrect domain guess could silently omit purchasable scope.

## Evidence spans

A deterministic match retains the exact contiguous source-text sentence that justified the component,
including source offsets. The persisted `PurchaseComponent.scope_evidence` is the first exact span;
the extraction result retains every matching span for canonicalisation and later evidence-ledger use.

Component IDs are deterministic SHA-256-derived identifiers over:

`rule_version | operation_code | domain | category`

This keeps IDs stable across reruns when source content and rules are unchanged.

## Canonicalisation

Multiple phrase hits for the same domain/category produce one component. Evidence spans are deduplicated
and sorted by source position. Different domains remain namespaced so a multi-domain project can retain,
for example, both port and building photovoltaic scope without collapsing unrelated component context.

## Local-model handoff

The deterministic engine does not claim that a phrase dictionary is complete. Every non-empty source
sentence that has no deterministic component match is returned as an exact `unmatched_scope_span` and
sets `model_fallback_required=True`.

The later local-model stage may only:

1. inspect already allowlisted scope text;
2. propose a component label/category;
3. return the exact supporting source span; and
4. submit the proposal to deterministic canonicalisation.

It may not create procurement evidence or set OPEN/CLOSED/PARTIAL. If a component boundary remains
ambiguous after fallback, downstream classification must remain `UNRESOLVED`.

## CPV use

CPV prefixes are category hints, not standalone closure evidence. Product Requirements v1.0 requires
CPV/category agreement only as one element of the Tier B/C matching hierarchy; a CPV match by itself
must never set a component to CLOSED.

The CPV hierarchy follows the official EU Common Procurement Vocabulary. The regulation defines the
first two digits as divisions, then progressively more specific groups/classes/categories. Initial
precise mappings used here include, among others, pumps (`42122`), valves (`42131`), water-treatment
equipment (`429123`), railway signalling (`34942` / `45234115`), track works (`45234116`), level
crossings (`45234140`), catenary (`45234160`), photovoltaic modules (`093312`), HVAC (`45331`),
insulation (`4532`), lighting (`315`), energy-efficiency consultancy (`713143`), surveillance sensors
(`35125`) and emergency-service vehicles (`341442`).

Official reference:

`https://eur-lex.europa.eu/eli/reg/2008/213/oj/eng`

## Fail-closed invariants

- An empty domain list is rejected rather than guessed.
- No deterministic matches means local fallback is required; it never means “no components”.
- Unmatched source sentences are retained for fallback rather than discarded.
- Rule extraction never assigns procurement state.
- CPV prefix agreement never establishes CLOSED by itself.
- Model output, when implemented, cannot bypass evidence-span or classification rules.
