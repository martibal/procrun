# Phase R — exact CUP text linkage gate

Status: **DIAGNOSTIC ONLY**

Reviewed: 2026-09-12

## Purpose

Test whether the two Phase R candidate procurement families can be linked deterministically to their frozen funded-project cohorts by an exact CUP token appearing in already-qualified TED text fields.

A qualifying diagnostic hit requires both:

1. a TED CPV code matching the candidate domain's frozen diagnostic CPV family; and
2. the corresponding CUP appearing as an exact alphanumeric token in either `notice-title` or `description-proc`.

No fuzzy matching, punctuation-stripping, translation, semantic similarity, LLM inference or expanded TED fields are allowed.

## Candidate cohorts

- `digital_transformation`: 573 projects, intervention `013` + action `1.2.3`;
- `waste_circular_economy`: 142 projects, intervention `067` + action `2.6.2`.

## Frozen TED evidence families

- `digital_transformation`: CPV `302*`, `48*`, `72*`;
- `waste_circular_economy`: CPV `90514*`.

## Measurement

The diagnostic scans the complete already-qualified TED Italy universe through 2026-09-12 and emits aggregate counts only:

- exact-CUP-token notices by domain;
- title vs scope-description exact-CUP hits;
- unique candidate CUPs with a qualifying hit;
- candidate projects represented by those exact CUP hits.

## Boundary

The diagnostic uses only the existing production-safe TED projection and the existing qualified Lombardia Socrata projection.

It must not emit:

- CUP values;
- notice IDs;
- titles or descriptions;
- beneficiary data;
- row-level artifacts.

It does not change `ComponentDomain`, production component extraction, matching, OPEN/CLOSED/UNRESOLVED semantics, read model or customer output.

## Decision rule

An exact CUP-token + candidate-CPV hit is direct deterministic project-linkage evidence suitable for a later production-integration review. Absence of such a hit is not evidence that procurement did not occur. Any broader linkage method requires a separate preregistered gate.
