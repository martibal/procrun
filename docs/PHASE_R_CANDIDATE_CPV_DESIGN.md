# Phase R — candidate component and CPV design gate

Status: **DIAGNOSTIC ONLY**

Reviewed: 2026-09-12

## Purpose

The public-definition qualification admitted two candidate procurement domains for further design:

- `digital_transformation`: intervention code `013` + action `1.2.3`, frozen cohort 573 projects;
- `waste_circular_economy`: intervention code `067` + action `2.6.2`, frozen cohort 142 projects.

The frozen candidate-domain measurement reproduced 715 incremental projects with zero overlap against the existing 142 safely mapped projects. The combined candidate ceiling is therefore 857 / 4,305 = 19.9071%.

This gate defines the smallest CPV families that are directly supported by official CPV descriptions and the qualified public action definitions. It does **not** add the candidate domains to the production `ComponentDomain` enum and does not change production extraction, matching, OPEN/CLOSED classification, read models or customer output.

## Matching constraint

ProcRun matching remains unchanged. A CPV/category match is only one structural feature. CPV alone cannot establish CLOSED. Under the frozen matching contract, CLOSED still requires the complete Tier A/B structural conditions plus exact source evidence; plausible structural candidates that lack exact evidence remain UNRESOLVED rather than being promoted to CLOSED or silently rejected into OPEN.

## Candidate domain 1 — digital transformation

Qualified structured cohort:

- intervention code: `013`;
- action: `1.2.3`;
- frozen projects: `573`.

Admitted component families:

| Category | CPV prefix | Official CPV scope |
|---|---:|---|
| `computer_hardware` | `302` | Computer equipment and supplies |
| `software_information_systems` | `48` | Software package and information systems |
| `it_services` | `72` | IT / computer and related services, including software and systems work |

The broad candidate action funds concrete digital technology, software, IT services and related implementation. These three CPV families cover the core procurement objects without adding generic consultancy, training, telecommunications or office-equipment families merely to increase recall.

## Candidate domain 2 — waste / circular economy

Qualified structured cohort:

- intervention code: `067`;
- action: `2.6.2`;
- frozen projects: `142`.

Admitted component families:

| Category | CPV prefix | Official CPV scope |
|---|---:|---|
| `recycling_equipment` | `42914` | Recycling equipment |
| `waste_treatment_infrastructure` | `452221` | Waste-treatment plant construction work |
| `waste_collection_treatment_recycling_services` | `9051` | Refuse collection, transport, treatment, disposal and recycling services |

The qualified public definitions describe collection/reuse/recycling infrastructure, equipment and related waste-management processes. The design deliberately excludes sewage CPV `904*`, hazardous/radioactive waste `9052*`, generic civil works `45*`, and generic machinery `429*` because those families are too broad for this candidate domain.

## Official CPV authority

CPV definitions are taken from the EU Common Procurement Vocabulary established by Regulation (EC) No 2195/2002 and amended by Commission Regulation (EC) No 213/2008. The official vocabulary includes, among others:

- `30200000-1` Computer equipment and supplies;
- `48000000-8` Software package and information systems;
- `72000000-5` IT / computer and related services;
- `42914000-6` Recycling equipment;
- `45222100-0` Waste-treatment plant construction work;
- `90510000-5` Refuse disposal and treatment, within the `9051*` refuse collection/treatment family;
- `90514000-3` Refuse recycling services.

## Fail-closed rules

1. Candidate CPV rules stay outside the production `ComponentDomain` enum.
2. Candidate rules do not enter the production `RULES` tuple.
3. No candidate CPV may create a `PurchaseComponent` in production in this gate.
4. No candidate CPV may alter OPEN/CLOSED/UNRESOLVED semantics.
5. No semantic similarity or LLM fallback is admitted.
6. Unknown, empty or malformed CPV values do not match.
7. The next gate must measure candidate CPV occurrence and specificity against the already-qualified TED safe projection before any production taxonomy change is proposed.

## Decision

**GO to CPV occurrence/specificity measurement only.**

The component families are sufficiently bounded to test against TED. They are not yet approved as production component domains. The Phase R 40% coverage target remains open; even full admission of both candidate cohorts would reach only 19.9071% before procurement-evidence constraints are applied.
