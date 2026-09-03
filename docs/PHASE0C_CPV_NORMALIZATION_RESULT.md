# Phase 0C — CPV-normalization confirmation result

Date: 2026-09-03
CI run: #170
Result: **FAIL**

The preregistered thresholds in `PHASE0C_CPV_NORMALIZATION_PREREG.md` were frozen before execution and were not changed after observation.

## Observed metrics

- sample size: 300 — PASS
- any normalized requirement: 20.3% — PASS vs 20.0% gate
- multi-requirement: 2.0% — diagnostic only
- description-only value: 0.7% — diagnostic only
- CPV-blind requirement value: 18.7% — PASS vs 12.0% gate
- distinct categories: 13 — **FAIL** vs 15 gate
- domains represented: 5 — PASS vs all-five gate

## Decision

Phase 0C failed one of five mandatory confirmation gates. Under the preregistered decision rule, the current TED-based ProcRun v2 mechanism is therefore **not validated as a website-build candidate**.

The positive CPV-blind signal reproduced on a disjoint period (20.7% in Phase 0B; 18.7% here), so there is evidence that text normalization can add information beyond component-family CPV filtering. That evidence is not sufficient to override the failed breadth gate or to declare the product validated.

No threshold is lowered, no sample is replaced, and no post-hoc PASS is declared.

## Consequence

The repository must not state `READY FOR WEBSITE BUILD` for the current v2 mechanism. A full customer web application should not be built against the current v2 promise without a new explicit product decision and a separately preregistered validation path.
