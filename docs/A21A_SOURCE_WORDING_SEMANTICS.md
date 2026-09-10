# A21a — Source wording semantics

**Status:** AUTHORITATIVE CLARIFICATION FOR PROCRUN 2.0 A21a

## Decision

A21a validates **source wording**, not document length.

The customer-facing evidence layer must show the best exact wording available in the approved project source that supports why the project is relevant. That wording may be either:

- a project title; or
- a longer project description / source excerpt when the approved source actually provides one.

A project title is valid source evidence when it is the actual authoritative wording supplied by the approved source. It must not be presented as a longer project description or as additional documentation that does not exist.

## Source type must be explicit

Every customer-facing source-evidence value must carry its actual source type. At minimum:

- `Project title`
- `Project description`

If the source description is identical to the title, ProcRun must not imply that two independent evidence surfaces exist. The customer may see the wording once, identified as `Project title`.

## A21a quality question

A21a therefore asks:

> Does ProcRun surface the correct, useful, verbatim source wording that supports the project's relevance, with correct provenance and source type?

It does **not** require every case to contain 1–3 full sentences. One exact title may be a successful evidence result when that is the strongest wording the approved source provides.

A longer description remains preferable when it exists and adds relevant information, but absence of a longer description is not by itself an A21a failure.

## Hard boundaries unchanged

This clarification does not relax any safety or provenance requirement:

- PII violations = 0;
- hallucinated or rewritten source evidence = 0;
- exact source-span integrity = 100%;
- correct source/provenance = 100%;
- no sealed A21b holdout access;
- no claim that source wording proves ProcRun's OPEN/CLOSED/UNRESOLVED interpretation.

## OpenCoesione Lombardia consequence

The live PR FESR Lombardia diagnostic found that the approved summary field is identical to the project title across the current 4,305-project logical universe. This does not invalidate the source for ProcRun 2.0. It means the customer-facing evidence type for those rows is `Project title`, unless a separately approved richer source becomes available later.

A21a must evaluate whether those titles are useful enough to explain project relevance. It must not fail them merely because they are titles rather than longer descriptions.
