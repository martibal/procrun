# Italy Puglia PR FESR/FSE+ 2021-2027 route findings

Status date: 2026-09-03.

This note records a metadata-only review of Regione Puglia's open-data route for the PR Puglia FESR/FSE+ 2021-2027 beneficiary/project list. It does not approve a source and does not change `SOURCE_CONTRACTS`.

## Product gate

ProcRun requires both a pre-receipt zero-PII field surface and project-specific scope rich enough to support exact component evidence spans. Title-only discovery is not an acceptable replacement for project description/scope text.

## Official metadata surface

The official Regione Puglia dataset is `Elenco Beneficiari PR PUGLIA FESR e FSE+ 2021 2027`, dataset identifier `beneficizripr2127`. The resource is published as CSV and the portal exposes a Data API affordance. The dataset page reports Regione Puglia as publisher/owner and a CC0 1.0 licence.

The resource metadata exposes the following columns:

- `denominazione_programma`
- `fondo`
- `denominazione_asse`
- `beneficiario`
- `titolo_progetto`
- `totale_finanziamento_pubblico_euro`
- `codice_istat_regione`
- `regione`
- `codice_istat_provincia`
- `provincia`
- `codice_istat_comune`
- `comune`
- `cap`

Critically, the metadata contains **no project summary, project description, operation summary, intervention description or equivalent project-specific scope field**.

## Safety and transport

The broad resource contains a `beneficiario` field. Under ProcRun's absolute zero-PII requirement, a broad row must not be fetched merely to determine whether beneficiary values happen to be organisations or natural persons.

The portal presents a Data API, but transport projection does not need to be experimentally verified for this candidate because the scope gate fails independently: even a perfectly field-bounded response would expose only `titolo_progetto` plus programme, fund, axis, finance and geography fields.

No CSV body, Data API project row or preview row was requested as part of this review.

## Scope decision

`titolo_progetto` is useful discovery metadata, but it is not enough for ProcRun's component engine. Programme/axis/fund and geography fields are categorical context, not project-specific evidence text. Without an operation summary or description, ProcRun cannot produce exact component evidence spans without weakening the locked product contract.

Therefore this route is rejected on scope before a project-data call is authorised.

## Final decision

- rights: **PASS / CC0 1.0 at dataset level**;
- public machine-readable access: **PASS / CSV with Data API affordance**;
- broad-row zero-PII safety: **NOT APPROVED because `beneficiario` is present**;
- server-side field projection: **NOT REQUIRED TO RESOLVE because scope fails independently**;
- project-specific scope text: **FAIL / NOT PRESENT IN OFFICIAL METADATA**;
- title-only replacement: **PROHIBITED**;
- coverage: **PARTIAL / Puglia regional programme only**;
- project-row/file smoke test: **PROHIBITED**;
- production eligibility: **REJECTED for insufficient project scope**.

This route should only be reconsidered if Regione Puglia publishes a richer project-specific description/scope field and that field is proven safe before receipt. A separate source could theoretically provide the missing scope, but such a join would require its own source contract and cannot be assumed here.
