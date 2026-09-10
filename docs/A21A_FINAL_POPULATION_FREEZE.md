# A21a Final Population Freeze

Status: **POPULATION-FREEZE CONTRACT IMPLEMENTED — FINAL POPULATION NOT YET FROZEN**

This document defines how ProcRun must freeze the A21a final evaluation population without opening or adjudicating sealed holdout content.

The release candidate and numerical thresholds are already frozen. The remaining prerequisite before final A21a evaluation is an immutable, disjoint final-population manifest.

## Required manifest anchors

A valid final-population manifest must contain:

- SHA-256 of the approved source pool used to derive the final population;
- SHA-256 of the exact population artifact;
- SHA-256 of the canonical sorted set of stable final `case_id` values;
- positive final case count;
- `development_overlap_count = 0`;
- manifest version `a21a-final-population-v1`;
- `sealed = true`.

`src/procrun/a21a_final_population.py` validates this contract and fails closed on missing/invalid hashes, empty populations, unsealed manifests or any development overlap.

## Content-blind disjointness check

Disjointness is established from stable identifiers only. The checker does not inspect source wording, gold excerpts, labels, adjudication or extractor output. Case-ID order and duplicate identifiers cannot change the case-ID fingerprint.

This is intentional: population integrity may be verified before the holdout is opened.

## What is not authorized

This contract does **not** authorize:

- opening or adjudicating an A21a sealed holdout;
- running the final A21a benchmark;
- using A21b sealed material;
- downloading an unqualified raw source merely to construct a holdout;
- changing the frozen A21a release candidate or preregistered thresholds after seeing final results.

## Next gate

The next gate becomes green only when an approved zero-PII source pool exists and a final manifest can be populated with real immutable hashes and proven zero overlap with all A21a development material.

Until then, the final A21a gate remains fail-closed.
