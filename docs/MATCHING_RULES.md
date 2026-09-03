# ProcRun procurement matching rules

Status date: 2026-09-03
Status: **CANONICAL FOR FUNDED-PROJECT RUNWAY**
Current rule version: `phase-b-conservative-v1`

## Governing rule

ProcRun tests each source-evidenced funded-project component against approved procurement evidence. It does not manufacture a numeric confidence score or turn semantic similarity into a procurement fact.

Component states are `OPEN`, `CLOSED` and `UNRESOLVED`. `PARTIAL` is a project-level aggregate state when a project's component states differ; it is not currently a component state.

## Tier A — automatic high confidence

A candidate may enter Tier A only when:

- a deterministic project/funding identifier matches;
- procurement scope has high overlap with the specific component being assessed;
- the date window is compatible.

An operation-code match alone never closes every component in a multi-component project.

## Tier B — automatic high confidence

All are required:

- contracting-authority organisation match;
- geography match;
- high component-scope overlap;
- CPV/category agreement;
- compatible date window.

Complete Tier A or Tier B evidence at/before cutoff may set the component to `CLOSED`.

## Tier C — review only

Tier C requires title/location support, high scope overlap, CPV/category agreement, compatible dates and corroborating amount/date evidence.

Tier C is deliberately `REVIEW`, never automatic CLOSED. A pre-cutoff Tier C candidate makes the component `UNRESOLVED`, never OPEN.

## Tier D — rejected for closure

Semantic similarity alone is Tier D and is never sufficient for CLOSED. The current baseline rejects it rather than promoting it into a confidence score.

## Component-state decision order

For each component and historical cutoff:

1. ambiguous component boundary -> `UNRESOLVED`;
2. accepted Tier A/B pre-cutoff evidence -> `CLOSED`;
3. Tier C pre-cutoff review candidate -> `UNRESOLVED`;
4. incomplete required source coverage -> `UNRESOLVED`;
5. otherwise -> `OPEN`.

The only customer wording for OPEN is:

> **No relevant procurement found in approved indexed sources as of DATE.**

OPEN is a bounded search conclusion, not a statement that the source itself proves no procurement exists.

## Project-state aggregation

- all components CLOSED -> project `CLOSED`;
- all components OPEN -> project `OPEN`;
- mixed component states -> project `PARTIAL`;
- only unresolved/no components -> project `UNRESOLVED`.

The existing deterministic aggregation implementation is authoritative unless a later explicitly versioned rule changes it.

## False-OPEN invariant

False OPEN is the highest-cost error. Ambiguity must reduce feed volume rather than create a lead. Review-band evidence, incomplete coverage and ambiguous component boundaries all suppress OPEN.

## Historical integrity

Post-cutoff procurement cannot rewrite the state at an earlier cutoff. It becomes later evidence/outcome history. Every accepted state keeps the cutoff, evidence references, rule/model versions and immutable classification hash required by the ledger contract.
