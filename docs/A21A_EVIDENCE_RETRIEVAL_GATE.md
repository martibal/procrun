# A21a — Evidence Retrieval Validation Gate

**Status:** AUTHORITATIVE HARD PRODUCT-QUALITY GATE — CLEAN DEVELOPMENT REPREREGISTRATION REQUIRED

## Scope

A21a validates the ProcRun 2.0 source-evidence layer independently of the A21b interpretation/classification gate.

It answers one question only:

> Can ProcRun reliably surface the exact source wording a customer needs to inspect, without rewriting, inventing, or obscuring provenance or source type?

A21a does **not** score OPEN/CLOSED/UNRESOLVED correctness. That remains A21b.

## Evidence may be title or description

A21a validates source wording, not document length. Valid evidence may be:

- an exact project title when that is the strongest wording the approved source provides; or
- an exact excerpt from a longer approved project description when one exists and adds relevant information.

A title is not a failed evidence result merely because it is short or not a full sentence. Conversely, ProcRun must never present a title as a longer project-description excerpt.

If a source description is identical to the project title, it counts as one evidence surface, not two. The customer-facing source type must be `Project title`. See `A21A_SOURCE_WORDING_SEMANTICS.md`.

## Required output contract

Each evidence result must contain:

- exact original text from an approved project source;
- actual source type / source field;
- exact start and end offsets in that source field;
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
- Incorrect source-type labeling: **0**.
- Sealed A21b holdout must not be opened, reused or contaminated by A21a development.

## Numerical-threshold state after the 2026-09-10 incident

The earlier `a21a-thresholds-v1` values are **invalidated as a clean preregistration**. They were frozen after development results had been viewed from a lineage later proven to use a prohibited download-then-filter source path. See `A21A_REPRODUCIBILITY_INCIDENT_2026-09-10.md` and `A21A_NUMERICAL_THRESHOLD_PREREGISTRATION.md`.

The historical v1 values remain visible for auditability, but `procrun.a21a_thresholds` now fails closed on a mandatory `clean_preregistration_lineage` check. A21a therefore cannot pass even if a report satisfies every historical numerical value.

A new active threshold version may be frozen only after:

1. the pinned clean-v2 development baseline is used;
2. a fresh independent review is completed without reusing invalidated v1 labels;
3. the clean development analyses are reproduced; and
4. the new thresholds are frozen before any sealed final-holdout result is viewed.

No historical v1 value may be silently relabeled as the clean replacement preregistration.

There is deliberately **no minimum character count or sentence count** for an otherwise valid evidence result. Utility is judged by whether the wording correctly explains project relevance, not by its length.

## Gold-standard requirement

The final benchmark must be independently adjudicated from approved, zero-PII project-source text. For each benchmark case, gold annotation must identify one or more acceptable source spans, the source field/type and the source document they come from.

The benchmark must include both:

- positive cases where useful relevance/procurement-related source wording exists; and
- negative cases where no defensible evidence should be returned.

A convenience sample is not sufficient. Sampling must represent the production universe across wording length, domains, project types, ambiguity and available source structures.

## Customer-facing rule

Passing A21a means ProcRun may use source evidence as a validated primary product layer. It does **not** authorize claims that ProcRun's interpretation is correct. Such claims remain gated by A21b.

A21a is necessary but not sufficient for launch: all other applicable safety, source, operational and commercial release gates must also be green.

## Current decision label

Until the clean development lineage is independently reviewed, a new threshold preregistration is frozen, the final benchmark population is disjoint, and the sealed final benchmark passes the new active gate:

**A21a — EVIDENCE RETRIEVAL: NOT YET GREEN**
