# Italy 2021-2027 funded-project discovery gate

Status date: 2026-09-10.

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

### Provenance review — `OperationSummary`

Documentation-only research was completed before any beneficiary/operation CSV was retrieved.

Authoritative evidence reviewed:

1. OpenCoesione's current `Lista beneficiari e operazioni 2021-2027` page states that the published minimum dataset includes operation name **and operation summary**, and that beneficiary name is published only for legal persons. The route is an open CSV, split by programme, updated bimonthly and licensed CC BY 4.0.
2. OpenCoesione's 2021-2027 communication guidelines map `Operation summary` to PUC2127 `SINTESI_PRG`. They explicitly state that `Operation name` must not contain names of natural persons, then describe `SINTESI_PRG` as a maximum-1,300-character description of what the project does, its purpose and, where needed, territory. Read in isolation, this document did **not** state an equivalent exclusion, anonymisation or masking rule for `SINTESI_PRG`.
3. Regulation (EU) 2021/1060 treats the short description of the operation as a distinct operation-data field. It does not itself establish a guarantee that arbitrary personal identifiers cannot occur in that free-text description before publication.
4. OpenCoesione's programme widgets republish the same operation/beneficiary lists; no documented general server-side/source-side field projection was found that would make the broad OpenCoesione project route independently safe.
5. **Ragioneria Generale dello Stato, `Vademecum per il Monitoraggio`, versione 1.0, dicembre 2024, AP00 — Anagrafica progetto** is the more direct technical source for the ReGiS/PUC project-field definitions. It states that the fields `TITOLO_PROGETTO` and `SINTESI_PROG` must not contain sensitive information attributable to natural persons, including name, fiscal code, telephone number or email address. This later source qualification therefore supersedes the earlier conclusion that no pre-receipt rule for `SINTESI_PROG` had been established.

The distinction between evidence sources matters. The communication guidelines remain relevant for publication semantics and field mapping, but the monitoring vademecum is the stronger source for what may be entered into the underlying project fields. The earlier `FAIL / NOT ESTABLISHED` conclusion for `SINTESI_PROG` was correct on the narrower evidence set available at that time; it is no longer the current conclusion for a route whose field identity is proven to be the vademecum-governed `SINTESI_PROG`.

### Subsequent bounded source qualification

Later A21a source qualification established one bounded OpenCoesione route:

`https://opencoesione.gov.it/it/opendata/beneficiari/2021-2027/beneficiari_PR_FESR_LOMBARDIA.zip`

For this route, the field mapping and the Vademecum Monitoraggio rule jointly support pre-receipt admission of `TITOLO_PROGETTO` and `SINTESI_PROG` under ProcRun's zero-PII contract. This does **not** reopen the general OpenCoesione `/api/progetti` route, the project-search CSV, or any other source surface whose exact fields and pre-receipt contract have not separately been qualified.

The bounded Lombardia source also exposes an important product limitation: in the observed live data, `SINTESI_PROG` is textually identical to `TITOLO_PROGETTO`. It therefore does not provide a richer project-description fallback. Under A21a semantics the customer-facing source type must remain truthful: when the only distinct project wording is the title, ProcRun may surface `Project title`; it may not upgrade the evidence using programme objective/context or generated prose.

### Current decision for Candidate 3

The previous blanket rejection of Candidate 3 on the ground that `SINTESI_PROG` lacked a source-side PII rule is **superseded**.

Current status is intentionally split:

- rights: **PASS**;
- automated/public access: **PASS** for the bounded published programme archive;
- structured beneficiary identity masking: **PASS**;
- `TITOLO_PROGETTO` natural-person rule: **PASS**;
- `SINTESI_PROG` pre-receipt natural-person rule: **PASS where field identity is proven against the Vademecum Monitoraggio contract**;
- bounded `PR FESR LOMBARDIA` route: **QUALIFIED for A21a source-wording use**;
- general OpenCoesione project/API/search surfaces: **NOT REOPENED / require independent qualification**;
- richer-description fallback on the qualified Lombardia route: **NOT AVAILABLE because `SINTESI_PROG` duplicates `TITOLO_PROGETTO`**;
- production eligibility of the broad Candidate 3 family: **NOT GRANTED by this document**.

No raw source may be downloaded merely to test whether an unqualified route is safe. Qualification must continue to be established before receipt from authoritative field/content contracts.

## Candidate 4 — OpenBDAP / MOP public-works project data

The next independent national source family investigated was the Ragioneria Generale dello Stato's OpenBDAP `Monitoraggio Opere Pubbliche` (MOP) dataset. The review remained documentation/catalogue-only and did not request a MOP project row.

OpenBDAP publishes the national `Progetti Opere Pubbliche MOP - Totale` dataset and regional variants. The official dataset description covers project identity/status, CUP classification, financial measures and procedural dates. The catalogue exposes reusable machine-readable distributions and identifies MOP datasets as CC BY / free reuse with attribution.

The official project metadata PDF documents the broad project surface. It includes, among other fields:

- `Codice Locale Progetto`;
- `Codice CUP`;
- `Descrizione CUP Integrale`, described as the integral description of the public-investment project;
- CUP status and validity dates;
- `Descrizione Titolare`;
- `Codice Fiscale Titolare`;
- intervention nature/type, sector, subsector and category;
- planned/effective procedural dates;
- financial measures.

The broad CSV/XML/JSON distributions are therefore **ineligible** because they can include a fiscal/tax identifier in the same project record. ProcRun may not receive such a response and remove the field afterwards.

### OData transport finding

OpenBDAP exposes an OData transport for project datasets. External implementation evidence confirms the deployed route family uses `ODataProxy/MdData('<dataset-id>@rgs')/DataRows` and supports query parameters such as `$filter`, `$skip` and `$top`. OpenBDAP's own public API page, however, documents the catalogue API rather than a field-projection contract for the MOP OData service.

No authoritative MOP-specific documentation was found that proves the exact national project endpoint supports a stable server-side `$select` contract with fail-closed unknown-field behaviour. That projection gate therefore remains **UNPROVEN**. No `DataRows` request was made merely to test it.

### Final scope-safety review — `Descrizione CUP Integrale`

The scope gate is independently decisive even if server-side projection were later proven.

The current official CUP user manual contains a GDPR warning for free-entry descriptive project fields. It instructs users that personal data must not be entered unless explicitly required and that sensitive/special-category data must never be entered. Critically, the same warning states that responsibility for the CUP information entered rests solely with the subjects requesting the code.

That is an input instruction, not a source-side guarantee. The reviewed documentation does **not** establish automated validation, pre-publication anonymisation or masking that would guarantee a submitted `Descrizione CUP Integrale` cannot contain a natural-person name or equivalent identifier.

Under ProcRun's absolute pre-receipt zero-PII boundary, an instruction to upstream users is insufficient when the source itself does not guarantee enforcement before publication. ProcRun also cannot download descriptions and scan them after receipt, because receiving the potentially identifying text would already violate the boundary.

The structured CUP taxonomy (`Tipologia Intervento`, sector, subsector and category) is safer, but it is categorical metadata rather than project-specific scope text. It cannot substitute for the exact source spans required by the component engine without weakening the locked product contract.

Therefore the only currently identified MOP field with plausible project-specific scope is not sufficiently source-guaranteed for ProcRun, while excluding it leaves scope insufficient.

### Coverage caveat

OpenBDAP states that the `Interventi UE` view covers only part of Structural-Fund interventions: investment projects increasing physical or technological capital. This is directionally aligned with ProcRun's infrastructure/equipment wedge but is not complete Italy 2021-2027 cohesion coverage. OpenBDAP also states that CUPs monitored through ReGiS are no longer monitored in BDAP from December 2024.

Coverage would therefore remain a separate blocker even if data safety were solved.

### Final decision for Candidate 4

- rights: **PASS at catalogue level**;
- automated/public access: **PROMISING / OData exposed**;
- broad distribution data safety: **FAIL** because prohibited identifier fields are present;
- server-side field projection: **UNPROVEN**;
- project-specific scope field: `Descrizione CUP Integrale`;
- scope pre-receipt zero-PII guarantee: **FAIL / NOT ESTABLISHED**;
- structured taxonomy as scope replacement: **INSUFFICIENT for exact component evidence spans**;
- Italy 2021-2027 coverage sufficiency: **FAIL / PARTIAL-SOURCE RISK**;
- project-row smoke test: **PROHIBITED**;
- production eligibility: **REJECTED under the current zero-PII and scope requirements**.

Candidate 4 may only be reconsidered if RGS/DIPE publishes a source-side guarantee or enforced publication control for the project description, or if an official field-bounded source provides equally detailed project scope without prohibited data. Proving `$select` alone would not make the route eligible.

## OpenCUP enrichment

OpenCUP remains rejected because available project surfaces can include beneficiary/person names and fiscal/tax identifiers in the same record, and no documented safe server-side projection has been established.

## Production status

No broad Italy funded-project source family is production-approved by this discovery document. A later A21a qualification has admitted the bounded `PR FESR LOMBARDIA` archive for source-wording validation only; that narrower result must not be generalized to unqualified OpenCoesione surfaces.

| Route | Rights | Access | Data safety | Scope | Research decision |
| --- | --- | --- | --- | --- | --- |
| OpenCoesione relational `Progetti` | strong | strong | promising | **blocked for 2021-2027** | reject as current-cycle scope source |
| OpenCoesione `/api/progetti` | strong | strong | unresolved | unresolved | do not call project records |
| 2021-2027 beneficiary/operation list — broad family | **strong** | **strong** | **qualified only where exact field contract is proven** | **strong in schema; variable in live wording** | **no blanket production approval** |
| `PR FESR LOMBARDIA` bounded archive | **strong** | **strong** | **PASS for admitted project title/summary fields** | **title-level only in observed live data** | **qualified for A21a source-wording use** |
| OpenBDAP / MOP project data | **strong** | **promising** | **FAIL: scope text not source-guaranteed PII-safe** | **insufficient if description excluded** | **rejected under zero-PII/scope boundary** |
| OpenCUP project/API | strong/open-data signal | conditional | **blocked** | strong | reject as enrichment |

Nothing in this document changes the executable production registry. Any production promotion must remain separately gated, source-bounded, and hash-anchored.