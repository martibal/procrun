# Portugal 2030 national fallback gate

Status date: 2026-09-02.

## Purpose

Kohesio/EU Knowledge Graph research did not produce a production-safe Portugal 2030 discovery route.
This gate defines the next investigation without weakening ProcRun's pre-receipt zero-PII boundary or
silently changing the component-engine contract.

No source in this document is production-approved and this document does not change `SOURCE_CONTRACTS`.

## Candidate: Mais Transparência project-search cards

The official Portugal 2030 project-search surface exposes project cards containing, at minimum:

- project title;
- operation code;
- expected completion date; and
- financing amount.

The observed project-search page does not expose beneficiary name/tax identifiers in each project card.
This makes the card surface materially safer than project-detail pages or the broad operations workbook.

However, two independent gates remain unresolved:

1. **Rights/access** — Mais Transparência presentation-site terms protect site contents and do not
   explicitly grant automated commercial reuse/scraping rights for the HTML route. The underlying AD&C
   data is also published through dados.gov.pt, whose platform terms describe state-published data as
   CC BY 4.0 by default unless otherwise specified, but that does not automatically establish permission
   for automated use of the separate presentation-site HTML route.
2. **Scope sufficiency** — project-search cards do not expose the project `Sumário`. ProcRun's component
   engine is evidence-span based; it may only extract components supported by exact source text and must
   leave ambiguous/unmatched scope unresolved.

Decision: **CONDITIONAL / research only**.

## Title-only discovery hypothesis

A title-only mode may be investigated, but it is not approved by this document.

The hypothesis is deliberately conservative:

- only the exact project title may enter the component extractor;
- no component may be inferred beyond phrases actually present in the title;
- no local-model expansion may invent missing project scope;
- if the title does not establish a component boundary, the project/component remains `UNRESOLVED`;
- title-only discovery may never improve an outcome from UNRESOLVED to OPEN merely because procurement
  evidence is absent;
- the Phase-0 classification oracle must not be used as proof that title-only extraction reproduces the
  original component evidence.

Before this mode can become a production option, ProcRun needs a curated PII-safe end-to-end replay that
compares title-only component extraction against the frozen scope-based decisions on the Phase-0 sample.
The acceptance criterion must be preregistered before the replay is run.

## Alternative safe-source requirement

Prefer a route that exposes the real project summary/scope with server-side field projection. A future
candidate is acceptable only if all of the following are proven before any project body is ingested:

1. project code/title/scope/funding/dates are available;
2. beneficiary/person/contact/tax fields are excluded before receipt;
3. commercial reuse rights apply to the exact source data;
4. automated access is documented or otherwise explicitly permitted for the exact route;
5. schema drift can be detected before persistence;
6. a small cross-programme Portugal 2030 fixture resolves successfully.

## Rights note for dados.gov.pt

Current dados.gov.pt terms define open data as freely reusable and redistributed data, including
commercial reuse, and state that data uploaded by state bodies is published under CC BY 4.0 unless a
contrary licence is specified. The PT2030 operations dataset metadata currently displays `Licença não
especificada` rather than an explicit alternate licence.

This is a stronger reuse signal than previously recorded, but it does not remove the data-safety block:
the only operation-level distribution currently identified is a broad XLSX containing beneficiary fields
and identifiers, with no server-side output-column projection. ProcRun therefore still must not download
that file and filter locally.

## Frozen next actions

1. Do not run any more Kohesio project/data probes unless the Commission later publishes a documented
   field-projection contract or a separately field-safe Portugal distribution.
2. Determine whether Mais Transparência has an officially documented machine-access route for project
   search results that preserves the project-card field surface and excludes beneficiary/person fields.
3. Separately determine whether exact-route commercial reuse/automation is permitted; do not infer this
   from public visibility alone.
4. If both gates pass, build a metadata/schema smoke probe before retrieving a page of project cards.
5. Only after transport/data safety are proven, preregister and run a title-only sufficiency replay.
6. If title-only coverage is materially insufficient, keep Portugal discovery blocked until a real
   field-projected scope source exists.
