# Phase R — candidate CPV occurrence and specificity gate

Status: **DIAGNOSTIC ONLY**

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
- TED scope: `ALL`.

## Data minimisation

Each Search API request uses server-side projection with exactly one returned field:

- `publication-number`.

The response row is used only to satisfy the API result envelope. No notice row is persisted. The artifact contains only aggregate `totalNoticeCount` values and derived percentages.

The diagnostic does **not** request or persist:

- title;
- description;
- buyer identity;
- contact information;
- location;
- value;
- links;
- beneficiary information;
- project narrative.

## Queries

Nine bounded count queries are executed:

1. all Italy notices in the frozen window;
2. `302*`;
3. `48*`;
4. `72*`;
5. digital union (`302* OR 48* OR 72*`);
6. `42914*`;
7. `452221*`;
8. `9051*`;
9. waste/circular union (`42914* OR 452221* OR 9051*`).

TED officially documents wildcard expert-search syntax such as `classification-cpv = 30*` for CPV subtrees. The candidate rules therefore use the same hierarchical prefix semantics as the official TED search surface.

## Decision rule

This measurement is a specificity diagnostic, not a production matching gate.

- Low-to-moderate share of the Italy universe supports using the candidate CPV family as one structural relevance feature.
- A very broad share is evidence that the CPV family is too generic and should be narrowed before any production proposal.
- CPV occurrence alone never creates CLOSED evidence and cannot change OPEN/CLOSED/UNRESOLVED state.
- Any future production proposal must preserve the frozen matching contract requiring additional structural facts and exact source evidence for CLOSED.

No production taxonomy, mapping, read model, TED production query or customer output changes in this gate.
