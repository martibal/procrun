# Phase R — candidate CPV TED validation

Status: **DIAGNOSTIC ONLY**

Reviewed: 2026-09-12

## Purpose

Validate the two public-definition-qualified candidate domains against the complete, already-qualified TED Italy safe-projection universe without changing production classification semantics.

Candidate domains:

- `digital_transformation`: CPV `302*`, `48*`, `72*`;
- `waste_circular_economy`: CPV `90514*` only.

## Frozen inputs

- OpenCoesione Phase R corpus: 4,305 projects;
- OpenCoesione source SHA-256: `35dc073ec9e5e06201080bc949a9da19dfd3366deee3524417491e2b2fd21c6a`;
- candidate cohorts: 573 digital-transformation projects and 142 waste/circular-economy projects;
- TED cutoff: 2026-09-12;
- TED source: existing production safe field projection only.

## Measurement

The diagnostic reports aggregate counts only:

1. complete TED Italy notice count and pages fetched;
2. TED notices whose CPV codes match each candidate domain and candidate component rule;
3. exact CUP-reference TED notices whose projected `eu-funds-identifier` equals a CUP in the corresponding candidate cohort;
4. distinct candidate projects with at least one exact CUP-reference + candidate-CPV hit.

The all-TED CPV counts are **market/evidence prevalence only** and are not project matches. Exact CUP-reference hits are a deliberately strict lower bound because the projected TED record currently retains only the first projected EU-funds identifier and no inferential project linkage is introduced here.

## Boundary

No beneficiary data, buyer-name expansion, non-qualified TED fields, project narrative, notice IDs, CUP values, row-level artifacts or customer records may be emitted.

This gate does not change:

- `ComponentDomain`;
- production component extraction;
- OPEN/CLOSED/UNRESOLVED semantics;
- matching logic;
- read model;
- customer output.

## Decision rule

- High TED CPV prevalence establishes that the candidate procurement families are materially present in the admitted TED universe, not that a particular funded project procured them.
- Exact CUP-reference + CPV hits provide direct deterministic project-level support for the subset where TED publishes the project reference.
- Absence of an exact CUP-reference hit must not be interpreted as absence of procurement.
- Production promotion requires a separate evidence/matching integration gate and regression tests.
