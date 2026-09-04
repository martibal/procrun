# OpenCoesione A1 source qualification

Status: **APPROVED SOURCE CONTRACT — EXACT 2021-2027 EU COHESION OPERATION-LIST ROUTE ONLY**
Review date: 2026-09-04

This decision applies only to the bounded public CSV operation/beneficiary lists published by OpenCoesione for EU-funded national and regional 2021-2027 programmes. It does **not** approve the general OpenCoesione Projects database, general API responses, subject/entity datasets, project-detail HTML, or any broader route.

## Non-negotiable validation constraint

ProcRun source qualification is zero-contact. No interview, outreach, authority/source-owner contact, customer contact, bespoke assurance, paid consultant/auditor/legal opinion or private clarification may close this gate. Only already-public, independently inspectable evidence and machine-verifiable behaviour may do so. Silence is never permission.

## Exact production boundary

Approved source surface:

- publisher: OpenCoesione / MEF-RGS-IGRUE;
- publication: `Lista beneficiari e operazioni 2021-2027`;
- transport: publisher-hosted HTTPS CSV operation lists divided by operational programme, or the publisher-hosted complete-list CSV when the same published schema/contract applies;
- programme universe: national and regional 2021-2027 programmes financed with EU cohesion funds, exactly as represented by the publisher's operation-list page;
- refresh claim: bimonthly, as stated by OpenCoesione;
- retained intelligence fields are limited to operation/project identifier where present, operation name, operation summary, start date, end date, eligible expenditure/value, EU co-financing information, programme/fund/category, country/postcode or other non-person aggregate geography, list-update date, and canonical source reference;
- beneficiary identity is not required by ProcRun and must not be retained. The approved publication contract states that beneficiary names on this surface are published only for legal persons.

The collector must reject any route or schema that expands beyond this frozen publication surface.

## A1 decision matrix

### RIGHTS — APPROVED

OpenCoesione states that its datasets are released under CC BY 4.0 and expressly explains that reuse, modification, redistribution and commercial reuse are permitted subject to attribution.

Authoritative public evidence:

- `https://opencoesione.gov.it/en/licenza/`
- `https://opencoesione.gov.it/it/beneficiari_operazioni_2021_2027/`

Required attribution: identify OpenCoesione / MEF-RGS-IGRUE as source and distinguish ProcRun-derived analysis from the source publication.

### ACCESS — APPROVED

The operation lists are intentionally published as open CSV files to enable reuse, processing and extraction. They are available through public HTTPS publication without requiring a private or human approval path. OpenCoesione also documents public anonymous machine access generally, but the approved ProcRun route does not depend on authenticated API access.

Authoritative public evidence:

- `https://opencoesione.gov.it/it/beneficiari_operazioni_2021_2027/`
- `https://opencoesione.gov.it/en/api-opencoesione/` (supporting machine-access policy only; not the approved ingest route)

### TRANSPORT — APPROVED FOR THE EXACT CSV ROUTE

The approved route is a purpose-published 2021-2027 operation-list CSV surface with a regulatory minimum field set. ProcRun does not need to receive the broad Projects/Soggetti relational database or a general API object and filter it afterwards.

The general OpenCoesione API and broad project database remain outside this approval because their complete response surfaces are broader than ProcRun needs.

### FREE-TEXT SAFETY — APPROVED FOR OPERATION NAME + SUMMARY

The RGS monitoring vademecum defines `TITOLO_PROGETTO` and `SINTESI_PROG` as project title and synthetic project description and explicitly instructs that those fields must not contain sensitive information attributable to natural persons, including name, tax code, telephone number or email address.

The OpenCoesione 2021-2027 operation-list publication identifies operation name and operation summary as fields sourced from MEF-RGS-IGRUE monitoring data. On the same publication surface, beneficiary name is stated to be published only for legal persons.

Authoritative public evidence:

- `https://opencoesione.gov.it/media/uploads/20241203_vademecum-monitoraggio-puc-rgs-vers10.pdf` — AP00 project registry section (`TITOLO_PROGETTO`, `SINTESI_PROG`)
- `https://opencoesione.gov.it/it/beneficiari_operazioni_2021_2027/`

No other human-authored free-text field is approved by this decision.

### SCHEMA — APPROVED SUBJECT TO FAIL-CLOSED IMPLEMENTATION

The source publishes a defined regulatory minimum field set and links metadata for the operation-list format. ProcRun must freeze the exact CSV header allowlist before live activation. Unknown, missing, renamed or additional fields cause pre-processing rejection before any row is admitted to the intelligence pipeline.

Schema approval here is an approval of the documented source contract. Live activation still requires the collector regression tests that enforce it.

### COVERAGE — APPROVED FOR THE STATED ITALIAN 2021-2027 EU-COHESION UNIVERSE

OpenCoesione states that the complete list covers beneficiaries/operations of all national and regional 2021-2027 programmes financed with EU funds and is updated bimonthly.

This does **not** mean all Italian public investment, all nationally financed FSC activity, all procurement, or every project in Italy. Customer and analytical claims must retain the exact source universe.

Authoritative public evidence:

- `https://opencoesione.gov.it/it/beneficiari_operazioni_2021_2027/`

## Privacy boundary

The following are prohibited for this source contract:

- general OpenCoesione API ingestion into the intelligence plane;
- `Soggetti` / beneficiary/entity datasets outside the exact approved operation-list publication;
- project-detail HTML;
- arbitrary additional text fields;
- download of a broader dataset followed by local PII filtering;
- retaining beneficiary names even when they are legal persons, because they are unnecessary to the ProcRun analytical contract.

## Drift / failure behaviour

Before live activation, the collector must:

1. pin the approved publication family and programme-universe manifest;
2. validate expected content type and CSV structure before row processing;
3. compare headers to a frozen allowlist;
4. fail closed on any unknown/additional field, missing required field or route change;
5. record source observation time, source list-update date and content hash;
6. reject stale or incomplete programme coverage rather than silently treating it as complete;
7. keep raw payloads outside browser/API/customer surfaces;
8. re-run source review on the normal compliance-review cadence.

## Formal conclusion

**A1 PUBLIC-EVIDENCE SOURCE QUALIFICATION: PASS for `OpenCoesione 2021-2027 EU cohesion operation-list CSV` only.**

The source-contract blocker is therefore closed for this exact Italian expansion route. Live funded-project ingestion is **not yet activated**: collector registration, frozen-header tests, source-transfer validation and live end-to-end acceptance remain implementation/acceptance gates.

Portugal PRR remains permanently blocked Category B. This OpenCoesione decision does not revive or weaken that route, and it does not alter the TED-scoped Portugal MVP.