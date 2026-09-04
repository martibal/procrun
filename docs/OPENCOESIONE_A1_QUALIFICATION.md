# OpenCoesione A1 source qualification

Status: **APPROVED SOURCE CONTRACT — EXACT 2021-2027 EU COHESION OPERATION-LIST ROUTE ONLY**
Review date: 2026-09-04

This decision applies only to the bounded public ZIP/CSV operation/beneficiary lists published by OpenCoesione for EU-funded national and regional 2021-2027 programmes. It does **not** approve the general OpenCoesione Projects database, general API responses, subject/entity datasets, project-detail HTML, or any broader route.

## Permanent validation constraint

Source qualification is public-evidence-only and has no human-dependent fallback. If already-public evidence cannot close a source contract, the route is rejected or blocked. No future activation step depends on a reply, permission, assurance or bespoke interpretation from a source owner or other person.

## Exact production boundary

Approved source surface:

- publisher: OpenCoesione / MEF-RGS-IGRUE;
- publication: `Lista beneficiari e operazioni 2021-2027`;
- exact complete-list transport: `https://opencoesione.gov.it/it/opendata/beneficiari/2021-2027/beneficiari_2021-2027.zip` containing the publisher CSV;
- programme universe: national and regional 2021-2027 programmes financed with EU cohesion funds, exactly as represented by the publisher's operation-list page;
- refresh claim: bimonthly, as stated by OpenCoesione;
- admitted intelligence fields: operation/project identifier, CUP where present, operation name, operation summary, start/end date, total/eligible expenditure, EU co-financing rate, programme/fund/objective/category, non-person aggregate geography, list-update date and source reference;
- beneficiary identity is not admitted to the `FundingProject` analytical object.

The collector rejects any route or schema that expands beyond this frozen publication surface.

## A1 decision matrix

### RIGHTS — APPROVED

OpenCoesione states that its datasets are released under CC BY 4.0 and permits reuse, modification, redistribution and commercial reuse subject to attribution.

Authoritative public evidence:

- `https://opencoesione.gov.it/en/licenza/`
- `https://opencoesione.gov.it/it/beneficiari_operazioni_2021_2027/`

### ACCESS — APPROVED

The 2021-2027 operation lists are intentionally published as open CSV files to enable reuse, processing and extraction. The complete-list download is public and does not depend on authenticated or human-approved API access.

### TRANSPORT — APPROVED FOR THE EXACT ZIP/CSV ROUTE

The approved route is the purpose-published 2021-2027 operation-list ZIP/CSV surface with the regulatory minimum field set. ProcRun does not use the broad Projects/Soggetti relational database or a general API object and then filter it locally.

### FREE-TEXT SAFETY — APPROVED WITH DOCUMENTED RESIDUAL RISK

The RGS monitoring vademecum defines `TITOLO_PROGETTO` and `SINTESI_PROG` as project title and project summary and instructs administrations populating ReGiS that these fields must not contain information attributable to natural persons, including name, tax code, telephone number or email address.

**This is a data-provider instruction and publication rule, not a technical database constraint.** ProcRun therefore does not describe natural-person leakage as categorically impossible. The residual-risk profile is the same kind of documented source-contract risk accepted for other approved public sources: the public rule is authoritative, the collector is schema-bounded and fail-closed, and any observed contract violation stops ingestion rather than being normalised away.

For the current 2021-2027 cycle, OpenCoesione's own operation-list page directly states that the published information includes beneficiary name **only for legal persons** (`nome del beneficiario (solo persone giuridiche)`). This is therefore **confirmed for the 2021-2027 publication surface**, not inferred from the 2014-2020 cycle.

No other human-authored free-text field is approved by this decision.

Authoritative public evidence:

- `https://opencoesione.gov.it/media/uploads/20241203_vademecum-monitoraggio-puc-rgs-vers10.pdf`
- `https://opencoesione.gov.it/it/beneficiari_operazioni_2021_2027/`
- `https://opencoesione.gov.it/media/uploads/linee-guida_comunicazione-e-opencoesione_v2_0.pdf`

### SCHEMA — APPROVED, ENFORCED FAIL-CLOSED IN CODE

The documented 2021-2027 operation-list surface contains the 17 regulatory fields described by OpenCoesione/RGS. `src/procrun/collectors/opencoesione.py` freezes the exact ordered header contract and rejects missing, renamed, reordered or additional fields before any row is admitted. Row-level parse failure rejects the whole batch.

The two beneficiary identity columns are source-schema fields but are never mapped into the admitted `OpenCoesioneOperation`/`FundingProject` analytical object.

### COVERAGE — APPROVED FOR THE STATED ITALIAN 2021-2027 EU-COHESION UNIVERSE

OpenCoesione states that the complete list covers beneficiaries and operations of all national and regional 2021-2027 programmes financed with EU funds and is updated bimonthly.

This does **not** mean all Italian public investment, all nationally financed FSC activity, all procurement, or every project in Italy. Customer and analytical claims must retain the exact source universe.

## Runtime controls

Before network retrieval the collector must pass `require_live_source("opencoesione_2021_2027_operations")` and must match the frozen URL exactly. The collector then:

1. checks the approved ZIP route and response type;
2. requires exactly one CSV member;
3. decodes UTF-8/UTF-8-BOM only;
4. compares the complete ordered header set to the frozen contract before row admission;
5. rejects extra/missing/renamed/reordered fields;
6. stages all rows and admits none if any row fails;
7. requires a uniform list-update date across the batch;
8. records observation time, source URL, list-update date and SHA-256 of the source payload.

## Privacy boundary

Prohibited:

- general OpenCoesione API ingestion into the intelligence plane;
- `Soggetti` / entity datasets outside the exact approved operation-list publication;
- project-detail HTML;
- arbitrary additional text fields;
- download of a broader unapproved dataset followed by local PII filtering;
- retaining beneficiary identity in the analytical `FundingProject` object.

## Formal conclusion

**A1 PUBLIC-EVIDENCE SOURCE QUALIFICATION: PASS for `OpenCoesione 2021-2027 EU cohesion operation-list ZIP/CSV` only.**

The source contract is registered as APPROVED. The remaining activation gates are technical: live source-transfer execution against the exact publication, schema/drift validation on the real payload, end-to-end admission into the canonical `FundingProject` pipeline, and green CI.

Portugal PRR and related Category-B routes remain permanently blocked. This OpenCoesione decision does not revive them and does not alter the TED-scoped Portugal MVP.