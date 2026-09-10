# A21a — Numerical Threshold Preregistration

**Status:** `a21a-thresholds-v1` INVALIDATED — CLEAN REPREREGISTRATION REQUIRED

The v1 numerical thresholds were frozen before the sealed final holdout was opened, but **after development results had been viewed from a source lineage later proven to violate the permanent download-then-filter prohibition**. That timing invalidates v1 as a clean preregistration.

The values are retained below strictly as historical provenance. They are not an active product-quality gate and cannot produce A21a PASS in code.

## Historical v1 values — inactive

| Dimension | Historical v1 threshold |
| --- | ---: |
| Evidence precision | >= 0.95 |
| Gold excerpt recall | >= 0.90 |
| Gold-positive case recall | >= 0.95 |
| Negative-case false-positive rate | <= 0.05 |
| Exact source-span integrity failures | 0 |
| Provenance / source-type failures | 0 |
| Translation violations in authoritative evidence | 0 |
| Determinism failures | 0 |
| Aggregate hard-integrity gate | PASS |

These values must not simply be relabeled as v2. A new threshold version may be frozen only after a fresh independent development review has been completed on the clean sanitized-source lineage pinned in `A21A_REPRODUCIBILITY_INCIDENT_2026-09-10.md`.

## Required clean sequence

1. Use the clean-v2 development sample derived from the approved publisher-sanitized source pool.
2. Do not reuse the invalidated v1 title-utility or objective-fallback labels as adjudication.
3. Complete the independent development review while the sealed final holdout remains untouched.
4. Inspect and document the clean development results.
5. Freeze a new numerical threshold preregistration after those development results and before any final-holdout result is viewed.
6. Only then may a final A21a evaluator be enabled against the new preregistration version.

The active evaluator therefore includes a `clean_preregistration_lineage` hard check and remains fail-closed until this sequence is complete.

## Holdout discipline

The sealed A21/A21b holdout remains untouched by this incident and must remain unopened during remediation. The invalidation concerns development/preregistration provenance, not contamination of the sealed holdout itself.
