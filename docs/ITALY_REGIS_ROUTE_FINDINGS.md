# Italy ReGiS / Italia Domani route findings

Status date: 2026-09-03.

This note records the completed documentation-only review of the Italia Domani / ReGiS PNRR project open-data route. It does not approve a live source and does not change `SOURCE_CONTRACTS`.

## Candidate

The official Italia Domani / ReGiS publication family exposes project-level PNRR data. Official government reporting states that open-data publications include project-level datasets and metadata and are distributed as CSV, JSON and Excel. The same reporting describes separate project, subject, location and procurement/award datasets.

For ProcRun, the important question is not whether the data are public, but whether the exact project response can exclude prohibited person/identifier fields before receipt while retaining sufficient project-specific scope.

## Broad project surface

Current public schema documentation for the Italia Domani `PNRR_Progetti` file identifies a broad project record containing, among other fields:

- CUP and local project code;
- `Titolo Progetto`;
- `Sintesi Progetto`;
- financial-source breakdowns;
- planned/effective dates and project status;
- `Soggetto Attuatore`;
- `Codice Fiscale Soggetto Attuatore`.

The broad project distribution is therefore not eligible for ProcRun's intelligence plane. A fiscal/tax identifier appears in the same project record, and ProcRun may not download the response and discard that field locally.

No official server-side output-field projection contract was found for this publication family. The documented public distribution model is file-based (CSV/JSON/Excel), not a field-bounded API contract comparable to TED Search API projection.

## Scope-text safety

The route also contains the project-specific text ProcRun would want: `Titolo Progetto` and `Sintesi Progetto`. However, no source-side publication rule was found that guarantees arbitrary natural-person names or equivalent identifiers cannot occur in those fields before publication.

This is independently important because public downstream views of ReGiS-derived project data demonstrate that project titles can contain strings that identify natural persons. ProcRun must not use downstream empirical scanning as a mitigation; it simply reinforces that an explicit source-side guarantee would be required before receipt.

Dropping both title/summary and identity fields would leave only categorical/financial metadata and would not meet the locked exact-component-evidence-span requirement.

## Rights and access

Official government reporting states that PNRR open datasets are published under CC BY 4.0 and in open machine-readable formats. Rights are therefore strong at the publication-family level, and automated file retrieval is technically straightforward.

Those strengths do not cure the pre-receipt data-safety problem.

## Final decision

- rights: **PASS at publication-family level**;
- automated/public access: **PASS for file distributions**;
- broad project data safety: **FAIL** because the project record includes `Codice Fiscale Soggetto Attuatore`;
- server-side field projection excluding prohibited fields: **NOT FOUND**;
- project-specific scope availability: **STRONG**;
- title/summary pre-receipt zero-PII guarantee: **FAIL / NOT ESTABLISHED**;
- download-then-filter mitigation: **PROHIBITED**;
- project-row/file smoke test: **PROHIBITED**;
- production eligibility: **REJECTED under the current zero-PII and scope requirements**.

No `PNRR_Progetti` CSV, JSON or Excel body was retrieved during this review.

The route may only be reconsidered if the publisher introduces a documented server-side field projection or a separately published field-safe project artifact, and the retained project-specific scope text has an enforceable pre-publication privacy guarantee.
