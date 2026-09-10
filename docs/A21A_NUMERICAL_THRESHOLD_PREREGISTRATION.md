# A21a — Numerical Threshold Preregistration

**Status:** FROZEN BEFORE SEALED FINAL HOLDOUT

Version: `a21a-thresholds-v1`

This document preregisters the ProcRun A21a evidence-retrieval pass/fail thresholds before any sealed final A21a holdout is opened, inspected, scored or used for tuning. The thresholds apply to the release-candidate evidence retriever and are intentionally stricter than a simple majority-quality test because the customer-facing layer presents source wording as auditable evidence.

## Frozen numerical gate

A final A21a run passes only if every condition below is satisfied simultaneously:

| Dimension | Frozen threshold |
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

The gate is conjunctive. There is no averaging, compensating strength or discretionary override: failure on one row means A21a is not green.

## Interpretation

`evidence_precision >= 0.95` limits irrelevant surfaced evidence because a customer must not routinely inspect text that does not support the project relevance question.

`gold_excerpt_recall >= 0.90` requires the retriever to cover the large majority of independently adjudicated relevant source spans while allowing limited span-level disagreement where several defensible excerpts exist.

`gold-positive case recall >= 0.95` is the customer-level utility requirement: when useful approved source wording exists, ProcRun must surface relevant wording in at least 95% of such cases.

`negative-case false-positive rate <= 0.05` forces abstention on cases where no defensible evidence exists. ProcRun must prefer no evidence over invented or weakly related evidence.

All integrity, provenance, translation and determinism failures remain zero-tolerance. These requirements are not statistical quality targets; they are hard contract violations.

## Holdout discipline

The sealed final A21a holdout remains untouched by this preregistration. The final population must be disjoint from development material and must be adjudicated independently from extractor output. No threshold may be changed after final-holdout results are viewed. If the release-candidate extractor or these thresholds are changed after opening the holdout, that holdout can no longer be treated as a clean final evaluation for the changed candidate.

The final evaluator must consume the frozen metrics without silently substituting alternative definitions. A21a evaluates evidence retrieval only; A21b remains the separate interpretation/classification gate.

## Product decision

Threshold preregistration removes the current threshold-definition blocker, but it does not make A21a green. A21a becomes green only after the release candidate is frozen, a disjoint final benchmark is frozen and the sealed final evaluation satisfies every threshold above.
