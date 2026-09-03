# ProcRun

ProcRun is a private, evidence-first procurement-intelligence research product for suppliers to public infrastructure markets.

## Current product decision

**Status: NOT READY FOR WEBSITE BUILD.**

The TED-based v2 candidate is a deliberate pivot away from the original funded-project-first Procurement Runway mechanism. It must not inherit the original Phase 0 validation by assumption.

The v2 candidate tested this pipeline:

`TED notice -> normalized purchasable requirements -> supplier relevance -> evidence -> customer feed`

The source foundation is technically viable, but the customer-value mechanism has now been tested separately and did not pass its preregistered validation gates.

## What is technically validated

The production-safe source foundation is the TED Search API. The prior TED capability inventory established a substantial Portugal infrastructure universe and safe server-side field projection under ProcRun's absolute pre-receipt privacy boundary.

The validated TED source hypotheses remain:

| Hypothesis | Result |
| --- | --- |
| Active infrastructure notice feed | SUPPORTED |
| Procurement market intelligence dataset | SUPPORTED |
| Early procurement runway from TED | NOT SUPPORTED |
| Comprehensive EU-funding subset | NOT SUPPORTED |

These results establish source capability. They do not by themselves validate a paid supplier product.

## Phase 0B — embedded-demand test

Phase 0B preregistered a direct test of whether active Portugal TED infrastructure notices contained a sufficiently rich purchasable-requirement layer under the existing frozen deterministic taxonomy.

Observed on 300 notices:

- any requirement: 26.0% — PASS;
- description-only value: 2.7% — **FAIL**;
- CPV-blind value: 20.7% — PASS;
- distinct categories: 20 — PASS;
- domains represented: 5 — PASS.

Because all mandatory gates had to pass, Phase 0B result was **FAIL**. The failed threshold was not changed after observation.

See [`docs/PHASE0B_TED_DEMAND_PREREG.md`](docs/PHASE0B_TED_DEMAND_PREREG.md) and [`docs/PHASE0B_TED_DEMAND_RESULT.md`](docs/PHASE0B_TED_DEMAND_RESULT.md).

## Phase 0C — disjoint confirmation

The strong post-hoc CPV-blind signal from Phase 0B was treated as a new hypothesis rather than being promoted to a conclusion. Phase 0C preregistered a confirmation test on a non-overlapping historical Portugal period.

Observed on another 300 notices:

- any normalized requirement: 20.3% — PASS;
- CPV-blind value: 18.7% — PASS;
- distinct categories: 13 — **FAIL** against the frozen 15-category gate;
- domains represented: 5 — PASS.

Phase 0C therefore also resulted in **FAIL**. No threshold was lowered and no post-hoc PASS is declared.

See [`docs/PHASE0C_CPV_NORMALIZATION_PREREG.md`](docs/PHASE0C_CPV_NORMALIZATION_PREREG.md) and [`docs/PHASE0C_CPV_NORMALIZATION_RESULT.md`](docs/PHASE0C_CPV_NORMALIZATION_RESULT.md).

## Consequence

The previous `READY FOR WEBSITE BUILD` statement is superseded by these empirical results.

Do **not** build a full customer web application around the current TED-based v2 promise yet. The data source is usable and the CPV-blind signal is reproducible, but the complete commercial mechanism did not satisfy its frozen build gates.

The next move requires an explicit product decision rather than more threshold tuning or repeated testing on the same hypothesis.

## Original Procurement Runway

The original product mechanism was:

`funded infrastructure project -> purchasable components -> procurement coverage -> components not yet procured`

That mechanism had separate Phase 0 evidence and a different value proposition: finding potential commercial demand before procurement publication. Its production path remains blocked by the absolute pre-receipt zero-PII source boundary for the required funded-project discovery data. The old evidence remains valid for what it actually tested, but it does not validate the TED-based v2 pivot.

## Absolute intelligence-data boundary

No natural-person data may be collected, stored or processed in the ProcRun intelligence plane.

This is a pre-receipt requirement. Receiving a broad response and deleting prohibited fields afterwards is not permitted. Production collectors must pass independent RIGHTS, ACCESS and DATA SAFETY gates before retrieval.

See [`docs/SOURCE_STATUS.md`](docs/SOURCE_STATUS.md), [`docs/COMPLIANCE.md`](docs/COMPLIANCE.md) and [`docs/BUILD_GATES.md`](docs/BUILD_GATES.md).

## Current rule

Further product work must preserve the failed validation results and must not silently relabel the current v2 candidate as build-ready. A new build decision requires a genuinely new, preregistered product hypothesis or a resolved production-safe source path for the original mechanism.
