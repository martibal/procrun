# A21a — Evidence Retrieval Validation Gate

**Status:** AUTHORITATIVE HARD PRODUCT-QUALITY GATE — THRESHOLDS NOT YET FROZEN

## Scope

A21a validates the ProcRun 2.0 source-evidence layer independently of the A21b interpretation/classification gate.

It answers one question only:

> Can ProcRun reliably surface the exact project-document text a customer needs to inspect, without rewriting, inventing, or obscuring provenance?

A21a does **not** score OPEN/CLOSED/UNRESOLVED correctness. That remains A21b.

## Required output contract

Each evidence result must contain:

- exact original text from approved project documentation;
- exact start and end offsets in the source field;
- source field name;
- source URL/document reference;
- original language;
- document date when available;
- deterministic extractor version;
- optional English translation, always separate from the authoritative original.

The authoritative evidence string must always equal the source substring at the stored offsets. Rewritten or generated text can never become source evidence.

## Hard safety requirements

- PII violations: **0**.
- Hallucinated or rewritten source evidence: **0**.
- Evidence outside approved source fields: **0**.
- Evidence whose stored offsets do not reproduce the exact original text: **0**.
- Evidence without source provenance: **0**.
- Sealed A21b holdout must not be opened, reused or contaminated by A21a development.

## Quality dimensions requiring preregistered numerical thresholds

Before the final A21a evaluation, numerical thresholds must be frozen for at least:

1. exact source-span validity;
2. source-document correctness;
3. relevant-evidence recall;
4. irrelevant-evidence rate / precision;
5. case-level success rate for returning 1–3 useful sentences;
6. deterministic reproducibility across repeated runs.

Thresholds must be preregistered before final benchmark scoring. They may not be chosen after viewing final results.

## Gold-standard requirement

The final benchmark must be independently adjudicated from approved, zero-PII project-document text. For each benchmark case, gold annotation must identify one or more acceptable source spans and the source document they come from.

The benchmark must include both:

- positive cases where useful procurement-related evidence exists; and
- negative cases where no defensible procurement-related excerpt should be returned.

A convenience sample is not sufficient. Sampling must represent the production universe across text length, domains, project types, ambiguity and source-document structures.

## Customer-facing rule

Passing A21a means ProcRun may use source evidence as a validated primary product layer. It does **not** authorize claims that ProcRun's interpretation is correct. Such claims remain gated by A21b.

A21a is necessary but not sufficient for launch: all other applicable safety, source, operational and commercial release gates must also be green.

## Current decision label

Until thresholds are preregistered, benchmark material is frozen, and the final benchmark passes:

**A21a — EVIDENCE RETRIEVAL: NOT YET GREEN**
