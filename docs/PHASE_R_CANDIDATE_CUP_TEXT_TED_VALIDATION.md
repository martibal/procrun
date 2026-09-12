# Phase R — exact CUP text + candidate CPV TED validation

Status: **DIAGNOSTIC ONLY**

Reviewed: 2026-09-12

## Purpose

Test whether the two Phase R candidate domains can obtain deterministic project-level support from fields already admitted in the TED safe projection, without adding new fields or inferential matching.

The gate requires both:

1. a candidate-domain CPV match; and
2. the project's exact CUP token appearing verbatim in either the projected TED `notice-title` or `description-proc` text.

## Frozen candidate cohorts

- `digital_transformation`: 573 projects (`013` + action `1.2.3`), candidate CPV families `302*`, `48*`, `72*`;
- `waste_circular_economy`: 142 projects (`067` + action `2.6.2`), candidate CPV family `90514*`.

Frozen OpenCoesione source SHA-256:

`35dc073ec9e5e06201080bc949a9da19dfd3366deee3524417491e2b2fd21c6a`

TED cutoff: 2026-09-12.

## Exact-match semantics

A CUP text hit is valid only when the full CUP appears case-insensitively as one exact alphanumeric token with non-alphanumeric boundaries. No substring, fuzzy, translated, semantic or model-based matching is permitted.

The notice must independently match the candidate domain's frozen CPV family. A CUP occurrence without the candidate CPV is not counted as candidate procurement evidence.

## Output

Aggregate counts only:

- complete TED universe count/pages;
- matching notices by candidate domain and source field;
- distinct candidate projects with at least one exact CUP-text + CPV hit;
- project hit percentage by domain.

No CUP values, notice IDs, titles, descriptions or row-level records may be emitted in the artifact.

## Boundary

This gate uses only fields already present in the frozen TED safe projection:

- `notice-title`;
- `description-proc`;
- `classification-cpv`.

No new TED field, beneficiary field or buyer-name field is requested.

This gate does not change:

- `ComponentDomain`;
- component extraction;
- production matching;
- OPEN/CLOSED/UNRESOLVED semantics;
- read model;
- customer output.

## Decision rule

Any exact CUP-text + candidate-CPV hit is direct deterministic evidence that the notice references the candidate project and belongs to the candidate procurement family. Absence of such a hit is not evidence of absence of procurement.

Production promotion remains prohibited until a separate integration gate defines how validated project-level evidence enters the production matcher without weakening existing semantics.
