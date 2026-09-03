# Phase 0B — TED embedded-demand result

Date: 2026-09-03
CI run: #166
Result: FAIL

The preregistered thresholds in `PHASE0B_TED_DEMAND_PREREG.md` were not changed after observation.

## Observed metrics

- sample size: 300 — PASS
- any requirement: 26.0% — PASS vs 20.0% gate
- multi-requirement: 2.0% — diagnostic
- description-only value: 2.7% — **FAIL** vs 10.0% gate
- CPV-blind value: 20.7% — PASS vs 5.0% gate
- distinct categories: 20 — PASS vs 8 gate
- domains represented: 5 — PASS vs 3 gate

## Interpretation

The original v2 framing is not validated as preregistered. In particular, the evidence does not support making "requirements buried in the description beyond what the notice title already reveals" a core product claim under the current deterministic taxonomy.

The same untouched test produced a different, strong signal: 20.7% of sampled notices contained a text-supported requirement whose corresponding rule CPV prefixes were absent from the notice CPV list, while 20 distinct categories across all five domains were observed. That is evidence for a narrower hypothesis: **structured requirement normalization can add information beyond CPV classification even when the relevant concept is already visible in notice text.**

Because this narrower hypothesis was selected after seeing Phase 0B, it cannot be declared validated on the same sample. It requires a new preregistered confirmation test on a disjoint historical Portugal period before it can support a build decision.