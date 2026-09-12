# Phase R — candidate CPV occurrence and specificity gate

Status: **PASS FOR NON-DECISIVE STRUCTURAL FEATURE — NOT PRODUCTION ADMISSION**

Reviewed: 2026-09-12

## Purpose

The previous Phase R gate defined bounded candidate CPV families for two non-production candidate domains:

- `digital_transformation`: `302*`, `48*`, `72*`;
- `waste_circular_economy`: `42914*`, `452221*`, `9051*`.

This gate measures how common those CPV families are in the same Italy TED universe used by ProcRun, without downloading or persisting notice content.

## Frozen measurement window

- buyer country: `ITA`;
- publication start: `2021-01-01`;
- publication cutoff: `2026-09-12`;
- TED scope: `ALL`;
- total notices: `177,294`.

TED expert-search dates are sent in the API-required `YYYYMMDD` format while the artifact records ISO dates for readability.

## Data minimisation

Each Search API request uses server-side projection requesting exactly one field:

- `publication-number`.

TED injects `links` into the one returned notice stub even though it is not requested. That server-injected metadata is accepted only as an unavoidable non-PII response field, is not inspected for matching, and is never persisted. Any other unrequested notice field fails the diagnostic closed.

No notice row is persisted. The artifact contains only aggregate `totalNoticeCount` values, derived percentages and boundary flags.

The diagnostic does **not** request or persist:

- title;
- description;
- buyer identity;
- contact information;
- location;
- value;
- beneficiary information;
- project narrative.

## Measured counts

| Candidate family | Notices | Share of Italy TED |
|---|---:|---:|
| `302*` computer hardware | 1,838 | 1.0367% |
| `48*` software/information systems | 2,341 | 1.3204% |
| `72*` IT/computer-related services | 6,874 | 3.8772% |
| **Digital union** | **10,501** | **5.9229%** |
| `42914*` recycling equipment | 11 | 0.0062% |
| `452221*` waste-treatment plant construction | 158 | 0.0891% |
| `9051*` refuse collection/treatment/recycling services | 8,997 | 5.0746% |
| **Waste/circular union** | **9,154** | **5.1632%** |

The union counts are authoritative for the union shares; component-family counts are not summed because a notice may contain more than one CPV classification.

## Interpretation

### Digital transformation

The digital union covers 5.9229% of the frozen Italy TED universe. That is broad enough that CPV cannot be treated as decisive evidence, but bounded enough to remain useful as one structural relevance feature when combined with the already-qualified project cohort, geography/time constraints and the frozen exact-evidence matching contract.

`72*` is the largest digital family at 3.8772%. No widening beyond `302*`, `48*` and `72*` is justified by this gate.

### Waste / circular economy

The waste/circular union covers 5.1632% of the Italy universe. Almost all of that population comes from `9051*` at 5.0746%; `42914*` and `452221*` are very narrow.

Accordingly, `9051*` is explicitly **not** sufficient on its own to identify a ProcRun waste/circular component. It may only operate as a non-decisive structural feature inside the already-qualified `067 + action 2.6.2` project cohort and the existing evidence-bounded matching process. The narrower `42914*` and `452221*` families remain useful high-specificity structural features.

## Decision rule and result

This measurement is a specificity diagnostic, not a production matching gate.

- Low-to-moderate share of the Italy universe supports using the candidate CPV family as one structural relevance feature.
- CPV occurrence alone never creates CLOSED evidence and cannot change OPEN/CLOSED/UNRESOLVED state.
- Any future production proposal must preserve the frozen matching contract requiring additional structural facts and exact source evidence for CLOSED.
- `9051*` must not be promoted to a stand-alone classifier because its 5.0746% Italy-wide prevalence is too broad for that interpretation.

**Decision: PASS to a non-production candidate evidence-feature evaluation.** Both candidate unions are sufficiently bounded to test as structural features, with the explicit `9051*` restriction above. This is not approval to add either candidate domain to production.

No production taxonomy, mapping, read model, TED production query or customer output changes in this gate.
