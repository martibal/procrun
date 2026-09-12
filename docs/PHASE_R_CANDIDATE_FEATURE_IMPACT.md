# Phase R — candidate structural-feature impact gate

Status: **NO-GO FOR PRODUCTION ADMISSION UNDER CURRENT MATCHING CONTRACT**

Reviewed: 2026-09-12

## Purpose

The candidate CPV specificity gate showed that the qualified digital and waste/circular CPV unions each cover roughly 5–6% of the Italy TED universe. CPV is therefore usable only as a non-decisive structural feature.

This gate measures what would happen under the existing conservative matching contract if the two candidate project cohorts were combined with those CPV families and the already-qualified structured TED fields.

## Frozen candidate cohorts

- `digital_transformation`: intervention `013` + action `1.2.3` = 573 projects;
- `waste_circular_economy`: intervention `067` + action `2.6.2` = 142 projects.

The frozen OpenCoesione source reproduced exactly:

- project count: `4,305`;
- SHA-256: `35dc073ec9e5e06201080bc949a9da19dfd3366deee3524417491e2b2fd21c6a`.

## TED inputs

For each candidate domain, the diagnostic collected only notices inside the already-qualified candidate CPV union and requested only:

- `publication-number`;
- `publication-date`;
- `classification-cpv`;
- `eu-funds-identifier`;
- `place-of-performance-subdiv-proc`.

TED may inject `links`; it is accepted as non-PII transport metadata and never persisted.

The diagnostic did not request title, scope description, buyer identity, contact information, value, address or municipality.

## Measured result

| Measure | Digital transformation | Waste / circular economy |
|---|---:|---:|
| Frozen projects | 573 | 142 |
| Candidate-CPV TED notices | 10,501 | 9,154 |
| Projects with exact CUP/reference | **0 (0.0%)** | **0 (0.0%)** |
| Exact-reference notice matches | 0 | 0 |
| Projects with NUTS + candidate CPV | **573 (100.0%)** | **142 (100.0%)** |
| Projects with any structural candidate | **573 (100.0%)** | **142 (100.0%)** |
| Projects with date-compatible structural candidate | 553 (96.5096%) | 142 (100.0%) |

The aggregate artifact contains no CUP values, notice identifiers or row-level records.

## Interpretation

The result fails the intended discrimination test.

Neither candidate cohort has a single exact project reference in the relevant TED candidate universe. At the same time, every project in both cohorts has at least one geography + CPV candidate. This means the candidate CPV families and Lombardia geography are too broad to distinguish a project-specific procurement relationship under the current matching contract.

This is especially important because the frozen OPEN protection is intentionally asymmetric. A candidate with CPV/category relevance plus compatible geography is plausible enough to block rule-bounded OPEN even when it cannot establish CLOSED. Therefore, admitting these domains into production with the measured structural features would create plausible candidates for all 715 candidate projects while adding zero exact CUP-linked procurement evidence.

The practical effect would be systematic UNRESOLVED inflation, not useful coverage expansion.

The date-window diagnostic does not rescue the design: 553 / 573 digital projects and all 142 waste/circular projects still have at least one structural candidate inside their published project window.

## Decision

**NO-GO for adding `digital_transformation` or `waste_circular_economy` to the production `ComponentDomain` taxonomy under the current evidence path.**

Specifically:

1. Do not add either candidate domain to the production enum.
2. Do not add the candidate CPV rules to the production `RULES` tuple.
3. Do not treat NUTS + CPV as a stronger project-to-procurement link than the frozen matcher currently permits.
4. Do not weaken `_plausible_without_close`, OPEN protection, Tier A/B requirements or exact-evidence requirements to improve nominal coverage.
5. Do not report the 19.9071% candidate ceiling as achieved production coverage.

## Next gate

Further Phase R work requires a **more discriminative, non-PII project-to-procurement linkage** than geography + CPV. A viable route must provide one or more deterministic structured facts that materially narrow a procurement candidate to the funded project without relying on semantic inference or human contact.

Preferred evidence is an exact public project identifier such as CUP carried on the procurement record, or another public deterministic join key with equivalent semantics. Any new source/route must pass RIGHTS, anonymous ACCESS and pre-receipt DATA SAFETY before row-level intake.

If no such route can be qualified, these two candidate domains remain research-only and Phase R remains below the 40% commercial coverage gate.

## Boundary verification

The successful diagnostic recorded:

- `title_requested = false`;
- `description_requested = false`;
- `buyer_requested = false`;
- `contact_requested = false`;
- `ted_rows_persisted = false`;
- `cup_values_persisted = false`;
- `notice_ids_persisted = false`;
- `row_level_artifact_emitted = false`;
- `production_mapping_changed = false`;
- `production_taxonomy_changed = false`;
- `open_closed_semantics_changed = false`.

No production taxonomy, mapping, customer output or OPEN/CLOSED/UNRESOLVED semantics changed in this gate.
