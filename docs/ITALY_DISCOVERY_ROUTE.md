# Italy 2021-2027 funded-project discovery gate

Status date: 2026-09-03.

This document freezes the current research decision for Italy. It does **not** approve a live source and does not add an entry to `SOURCE_CONTRACTS`.

## Product requirement

ProcRun may only ingest a funded-project route when commercial reuse, automated access and the exact **pre-receipt** field surface are all approved. Natural-person names, fiscal/tax identifiers, contact data and equivalent person identifiers are prohibited from the intelligence plane. Download-then-filter is not a valid mitigation.

The funded-project source must also contain enough project scope to support exact component evidence spans. Title-only discovery is not silently substituted for scope text.

## Candidate 1 — OpenCoesione relational `Progetti`

Phase-1 metadata was inspected without retrieving project records. The frozen workbook was:

- `https://opencoesione.gov.it/media/opendata/metadati_database_OC.xlsx`
- observed SHA-256: `464a55a9aa78d8f197e399714fdc8cd76c8970d46b0fa8ae172fe7d2c705ced6`
- observed size: 248,608 bytes.

The `Progetti` relation is structurally separated from `Soggetti`, but for the 2021-2027 cycle its metadata marks `OC_SINTESI_PROGETTO`, project start date and project end dates as data not currently collected. Therefore it remains **insufficient for current-cycle ProcRun scope** and cannot be promoted on title alone.

## Candidate 2 — OpenCoesione `/api/progetti`

The official API has strong reuse/access signals, but current documentation has not established a complete safe response schema or a server-side field projection that excludes subject/person surfaces before receipt. Historical implementation evidence shows project responses may link to `soggetto`/role data.

Decision: **do not call project records under the zero-PII boundary**.

## Candidate 3 — `Lista beneficiari e operazioni 2021-2027`

The exact beneficiary metadata resource was retrieved without fetching beneficiary/operation records:

- `https://opencoesione.gov.it/media/opendata/metadati_beneficiari.xls`
- observed SHA-256: `c1e3be23c8ba7c84bc18a1183bd2e6ac0044f966843d72403ce0725b7cd4b96a`
- observed size: 38,400 bytes.

The workbook exposes 17 fields. It explicitly proves the following pre-publication rules:

- `CodiceFiscaleBeneficiario_BeneficiaryTaxCode`: for an individual beneficiary, the tax identifier is not published and is replaced by `*CODICE FISCALE*`;
- `NomeBeneficiario_BeneficiaryName`: for an individual beneficiary, the name is not published and is replaced by `*INDIVIDUO*`;
- `TitoloProgetto_OperationName`: natural-person name/surname or tax identifier appearing in the supplied title is not published.

No email, phone, personal contact, personal social identifier or equivalent direct-person field is present in the 17-field metadata surface.

The route otherwise has strong product scope: `SintesiProgetto_OperationSummary`, start/end dates, eligible expenditure, EU co-financing rate, postcode/country, intervention category and update date.

### Final provenance review — `OperationSummary`

Documentation-only research was completed before any beneficiary/operation CSV was retrieved.

Authoritative evidence reviewed:

1. OpenCoesione's current `Lista beneficiari e operazioni 2021-2027` page states that the published minimum dataset includes operation name **and operation summary**, and that beneficiary name is published only for legal persons. The route is an open CSV, split by programme, updated bimonthly and licensed CC BY 4.0.
2. OpenCoesione's 2021-2027 communication guidelines map `Operation summary` to PUC2127 `SINTESI_PRG`. They explicitly state that `Operation name` must not contain names of natural persons, then describe `SINTESI_PRG` only as a maximum-1,300-character description of what the project does, its purpose and, where needed, territory. No equivalent exclusion, anonymisation or masking rule is stated for `SINTESI_PRG`.
3. Regulation (EU) 2021/1060 treats the short description of the operation as a distinct operation-data field. It does not establish a guarantee that arbitrary personal identifiers cannot occur in that free-text description before publication.
4. OpenCoesione's programme widgets republish the same operation/beneficiary lists; no documented server-side/source-side field projection was found that would allow ProcRun to request the record without `OperationSummary` before receipt.

The exact safety condition therefore remains unprovable from the source contract. This is not something ProcRun may resolve by downloading records and scanning the free text afterwards: that would itself receive and process potentially identifying data.

### Final decision for Candidate 3

- rights: **PASS**;
- automated/public access: **PASS**;
- structured beneficiary identity masking: **PASS**;
- operation-title natural-person rule: **PASS**;
- scope sufficiency: **PASS**;
- `OperationSummary` pre-receipt zero-PII guarantee: **FAIL / NOT ESTABLISHED**;
- source-side projection excluding `OperationSummary`: **NOT FOUND**;
- Phase-3 record smoke test: **PROHIBITED**;
- production eligibility: **REJECTED under the current zero-PII product requirement**.

This candidate may only be reconsidered if OpenCoesione/MEF later publishes a source-side guarantee covering `SINTESI_PRG`, or provides an official server-side projection that excludes the field before ProcRun receives a record. A local filter, post-download scanner or sample inspection is not sufficient.

## OpenCUP enrichment

OpenCUP remains rejected because available project surfaces can include beneficiary/person names and fiscal/tax identifiers in the same record, and no documented safe server-side projection has been established.

## Production status

No Italy funded-project source is production-approved yet.

| Route | Rights | Access | Data safety | Scope | Research decision |
| --- | --- | --- | --- | --- | --- |
| OpenCoesione relational `Progetti` | strong | strong | promising | **blocked for 2021-2027** | reject as current-cycle scope source |
| OpenCoesione `/api/progetti` | strong | strong | unresolved | unresolved | do not call project records |
| 2021-2027 beneficiary/operation list | **strong** | **strong** | **FAIL: summary pre-receipt safety unproven** | **strong** | **rejected under zero-PII boundary** |
| OpenCUP project/API | strong/open-data signal | conditional | **blocked** | strong | reject as enrichment |

Nothing in this document changes the executable production registry. The Italy research path must now move to a different source or a structurally safe source-side projection rather than attempting a beneficiary/operation CSV smoke test.
