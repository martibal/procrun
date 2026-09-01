# Phase B matching rules

Status date: 2026-09-01.

## Governing rule

Product Requirements v1.0 freezes the candidate hierarchy and state semantics, but it does **not** freeze a numeric match score, CLOSED threshold or numeric review band. The implementation must not manufacture one.

Current rule version: `phase-b-conservative-v1`.

## Candidate hierarchy

### Tier A — automatic high confidence

A candidate may enter Tier A only when:

- a deterministic project/funding identifier matches;
- procurement scope has high overlap with the specific component being assessed; and
- the date window is compatible.

An operation-code match alone does not close every component in a multi-component project.

### Tier B — automatic high confidence

All of the following are required:

- contracting-authority organisation match;
- geography match;
- high component-scope overlap;
- CPV/category agreement; and
- compatible date window.

Complete Tier A or Tier B evidence at/before cutoff may set the component to `CLOSED`.

### Tier C — review band

Tier C requires project-title/location support, high scope overlap, CPV/category agreement, compatible dates and corroborating amount/date evidence.

Because v1.0 does not freeze the numeric CLOSED threshold for Tier C, a qualifying Tier C candidate is deliberately `REVIEW`, not automatically `CLOSED`. A pre-cutoff Tier C candidate therefore makes the component `UNRESOLVED`, never `OPEN`.

A later Product Requirements version may promote a formally validated Tier C threshold. That change must be explicit and regression-tested; it must not appear as an undocumented code-tuning change.

### Tier D — rejected for CLOSED

Semantic similarity alone is Tier D and is never sufficient for `CLOSED`. Under the current deterministic baseline it is rejected rather than treated as a review-band match.

## Component state order

For each component and historical cutoff:

1. If the component boundary itself is ambiguous: `UNRESOLVED`.
2. Else if at least one Tier A/B high-confidence pre-cutoff record covers it: `CLOSED`.
3. Else if at least one Tier C pre-cutoff candidate is in review: `UNRESOLVED`.
4. Else if required source coverage is incomplete: `UNRESOLVED`.
5. Else: `OPEN`, with the bounded wording “No relevant procurement found in indexed sources as of DATE.”

Coverage completeness is required for `OPEN`, but not for `CLOSED`: one demonstrably covering pre-cutoff procurement record is sufficient to suppress the component even if another source is temporarily unavailable.

Post-cutoff procurement cannot change the historical state at the earlier cutoff. It belongs in forward outcome tracking instead.

## False-OPEN invariant

The implementation is intentionally asymmetric. Ambiguity reduces feed volume; it must never increase it. Review-band procurement, incomplete source coverage and ambiguous component boundaries all withhold the component rather than manufacture `OPEN`.
