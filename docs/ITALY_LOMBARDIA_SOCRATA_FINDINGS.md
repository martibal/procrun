# Regione Lombardia Socrata route findings

Status date: 2026-09-03.

This note records a metadata/documentation-only review of Regione Lombardia's PR FESR 2021-2027 funded-operation dataset. It does not approve a production source and no project row was requested.

## Candidate

Official dataset:

`Beneficiari e operazioni finanziate dal PR FESR Lombardia 2021-2027`

Dataset identifier: `q78n-g3m9`.

The official catalogue describes the dataset as the Article 49 list of beneficiaries and operations for PR FESR Lombardia 2021-2027. The catalogue currently exposes 23 columns and a built-in Socrata/SODA API surface.

Relevant documented fields include:

- `nome_del_fondo`;
- `obiettivo_specifico`;
- `azione`;
- `nome_del_bando`;
- `codice_bando`;
- `nome_del_beneficiario`;
- `codice_del_beneficiario`;
- `operazione_finanziata`;
- `id_pratica`;
- `cup`;
- `codice_operazione`;
- `descrizione_operazione`;
- operation start/end dates.

The catalogue description for `NOME_DEL_BENEFICIARIO` explicitly says it is the name of the enterprise **or natural person** receiving the contribution. Therefore an unrestricted record is prohibited under ProcRun's zero-personal-data boundary.

## Server-side projection gate

This route materially differs from the national bulk-file candidates because the Socrata platform provides a documented server-side query projection. Socrata's SODA/SoQL documentation defines `SELECT` as the mechanism for choosing the output fields returned by the API. Every Socrata dataset has a dataset-specific API endpoint.

For ProcRun's architectural gate this is sufficient to establish that the platform class supports pre-receipt field projection in principle. A future production contract could therefore explicitly select only an allowlisted set and omit beneficiary identity fields before the response body is received.

Current gate:

- server-side field projection mechanism: **PASS / DOCUMENTED BY PLATFORM**;
- broad-record safety: **FAIL**;
- row smoke test: **NOT YET AUTHORISED** because scope safety remains unresolved.

No project row was fetched merely to prove behaviour already documented by the platform.

## Scope-text gate

Projection alone is not enough. ProcRun requires sufficiently granular project-specific scope that can support exact component evidence spans.

The strongest candidate fields are `operazione_finanziata` and `descrizione_operazione`. The latter is explicitly described as the project description. Current official dataset metadata does not establish a pre-publication anonymisation, masking or validation rule guaranteeing that these free-text fields cannot contain a natural-person name, fiscal identifier, contact detail or equivalent identifying text.

The safer fields (`obiettivo_specifico`, `azione`, `nome_del_bando`, classification/coding fields and dates) describe programme, call and intervention structure. They are useful for discovery and filtering, but they have not been shown to provide project-specific component evidence with exact source spans. Treating them as a replacement for project description would weaken the locked component-evidence contract.

Therefore:

- project-specific scope exists: **PASS**;
- project-specific scope pre-receipt zero-PII guarantee: **FAIL / NOT ESTABLISHED**;
- structured safe fields as exact scope replacement: **INSUFFICIENT / UNPROVEN**.

ProcRun may not receive the project text and scan it afterwards. That would violate the pre-receipt boundary.

## Coverage gate

This dataset covers PR FESR Lombardia 2021-2027 only. It is a regional programme source, not an Italy-wide discovery source. Even if the scope-safety gate were later solved, equivalent routes would have to be established for other programmes/regions or combined with another complete source family.

Coverage status: **PARTIAL / REGIONAL ONLY**.

## Final decision

- rights/publication basis: **PROMISING / official Article 49 open-data publication**;
- automated access: **PASS / Socrata API exposed**;
- server-side output projection: **PASS at platform-contract level**;
- broad record data safety: **FAIL** because beneficiary can be a natural person;
- projected structured fields: **potentially safe but scope-insufficient**;
- project-text zero-PII guarantee: **FAIL / NOT ESTABLISHED**;
- coverage: **PARTIAL / Lombardia only**;
- project-row smoke test: **PROHIBITED pending scope-safety proof**;
- production eligibility: **REJECTED under the current zero-PII and scope requirements**.

This candidate is notable because it proves that regional Socrata portals can solve the transport/projection problem that blocked national bulk distributions. It does **not** solve the independent free-text scope-safety problem.

The route may only be reconsidered if Regione Lombardia publishes an enforceable pre-publication sanitisation guarantee for the project scope fields, or exposes an equally granular project-scope field whose contract excludes personal data before receipt.
