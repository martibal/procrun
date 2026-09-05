# OpenCoesione A1 source qualification

Status: **APPROVED SOURCE CONTRACT — EXACT 2021-2027 EU COHESION OPERATION-LIST ROUTE ONLY**
Runtime activation status: **PR FESR Lombardia 2021-2027 ONLY; OTHER SAME-FAMILY ROUTES REQUIRE SEPARATE TECHNICAL ACCEPTANCE**
Review date: 2026-09-05

This decision applies only to the bounded public ZIP/CSV operation/beneficiary lists published by OpenCoesione for EU-funded national and regional 2021-2027 programmes. It does **not** approve the general OpenCoesione Projects database, general API responses, subject/entity datasets, project-detail HTML, or any broader route.

## Permanent validation constraint

Source qualification is public-evidence-only and has no human-dependent fallback. If already-public evidence cannot close a source contract, the route is rejected or blocked. No future activation step depends on a reply, permission, assurance or bespoke interpretation from a source owner or other person.

## Source-family boundary versus runtime activation

Approved source family:

- publisher: OpenCoesione / MEF-RGS-IGRUE;
- publication: `Lista beneficiari e operazioni 2021-2027`;
- programme universe: national and regional 2021-2027 programmes financed with EU cohesion funds, exactly as represented by the publisher's operation-list page;
- refresh claim: bimonthly, as stated by OpenCoesione;
- admitted intelligence fields: operation/project identifier, CUP where present, operation name, operation summary, start/end date, total/eligible expenditure, EU co-financing rate, programme/fund/objective/category, non-person aggregate geography, list-update date and source reference;
- beneficiary identity is not admitted to the `FundingProject` analytical object.

Source-family approval does **not** make every programme ZIP or the all-program ZIP live automatically. Each runtime route must independently pass transport acceptance and exact frozen-header validation before any data row is admitted.

Current live runtime route:

- `PR FESR Lombardia 2021-2027` only.

Official same-family routes checked on 2026-09-05 but **not activated**:

- all-program ZIP: `https://opencoesione.gov.it/it/opendata/beneficiari/2021-2027/beneficiari_2021-2027.zip`;
- Puglia programme ZIP: `https://opencoesione.gov.it/it/opendata/beneficiari/2021-2027/beneficiari_PR_FESR_FSE%2B_PUGLIA.zip`.

Both were tested with a bounded, header-only HTTP Range probe that refuses to read a response body unless the server returns HTTP 206 for the exact requested prefix and then decompresses only through the first CSV line. Both failed before the header could be qualified. Therefore neither route was inspected by receiving data rows, neither is claimed to match the frozen schema, and neither is live. The result is a **transport/header-evidence failure**, not evidence of schema drift.

The existing clean-runner evidence that the all-program ZIP can return HTTP 403 remains consistent with this fail-closed decision.

## A1 decision matrix

### RIGHTS — APPROVED

OpenCoesione states that its datasets are released under CC BY 4.0 and permits reuse, modification, redistribution and commercial reuse subject to attribution.

Authoritative public evidence:

- `https://opencoesione.gov.it/en/licenza/`
- `https://opencoesione.gov.it/it/beneficiari_operazioni_2021_2027/`

### ACCESS — APPROVED AT SOURCE-FAMILY LEVEL

The 2021-2027 operation lists are intentionally published as open CSV files to enable reuse, processing and extraction. Runtime automation still has to pass ProcRun's exact technical transport gate; public availability alone is not runtime acceptance.

### TRANSPORT — APPROVED ONLY PER ACCEPTED RUNTIME ROUTE

The purpose-published 2021-2027 ZIP/CSV surface is the eligible transport class. ProcRun does not use the broad Projects/Soggetti relational database or a general API object and then filter it locally.

As of 2026-09-05, Lombardia is the only live-accepted runtime route. The all-program and Puglia routes remain non-live because their bounded pre-row header probes did not complete successfully.

### FREE-TEXT SAFETY — APPROVED WITH DOCUMENTED RESIDUAL RISK

The RGS monitoring vademecum defines `TITOLO_PROGETTO` and `SINTESI_PROG` as project title and project summary and instructs administrations populating ReGiS that these fields must not contain information attributable to natural persons, including name, tax code, telephone number or email address.

**This is a data-provider instruction and publication rule, not a technical database constraint.** ProcRun therefore does not describe natural-person leakage as categorically impossible. The residual-risk profile is the same kind of documented source-contract risk accepted for other approved public sources: the public rule is authoritative, the collector is schema-bounded and fail-closed, and any observed contract violation stops ingestion rather than being normalised away.

For the current 2021-2027 cycle, OpenCoesione's own operation-list page directly states that the published information includes beneficiary name **only for legal persons** (`nome del beneficiario (solo persone giuridiche)`). This is therefore **confirmed for the 2021-2027 publication surface**, not inferred from the 2014-2020 cycle.

No other human-authored free-text field is approved by this decision.

Authoritative public evidence:

- `https://opencoesione.gov.it/media/uploads/20241203_vademecum-monitoraggio-puc-rgs-vers10.pdf`
- `https://opencoesione.gov.it/it/beneficiari_operazioni_2021_2027/`
- `https://opencoesione.gov.it/media/uploads/linee-guida_comunicazione-e-opencoesione_v2_0.pdf`

### SCHEMA — FROZEN 20-COLUMN TRANSPORT CONTRACT

OpenCoesione/RGS documentation describes a 17-field regulatory publication set, while the live approved Lombardia CSV transport contains **20 ordered columns**. ProcRun's actual runtime contract is the exact 20-column tuple frozen in `src/procrun/collectors/opencoesione.py`; missing, renamed, reordered or additional columns fail before any row is admitted.

The two beneficiary identity columns are source-schema fields but are never mapped into the admitted `OpenCoesioneOperation`/`FundingProject` analytical object. The additional programme/cycle transport columns likewise do not widen the admitted PII boundary.

No other programme route may be called schema-compatible merely because it belongs to the same publication family. Exact equality with the frozen 20-column transport header must be demonstrated before activation.

### COVERAGE — SOURCE FAMILY BROADER THAN CURRENT LIVE COVERAGE

OpenCoesione states that the complete publication family covers beneficiaries and operations of all national and regional 2021-2027 programmes financed with EU funds and is updated bimonthly.

ProcRun's **current live funded-project coverage is narrower: PR FESR Lombardia 2021-2027 only.** Customer and analytical claims must use the live runtime coverage, not the broader source-family universe.

Even if more programme routes become live later, this source family still does **not** mean all Italian public investment, all nationally financed FSC activity, all procurement, or every project in Italy.

## Runtime controls

Before network retrieval the collector must pass `require_live_source("opencoesione_2021_2027_operations")` and the exact requested runtime URL must be explicitly admitted by the source contract. For an activated route the collector then:

1. checks the approved ZIP route and response type;
2. requires exactly one CSV member;
3. decodes UTF-8/UTF-8-BOM only;
4. compares the complete ordered 20-column header set to the frozen contract before row admission;
5. rejects extra/missing/renamed/reordered fields;
6. stages all rows and admits none if any row fails;
7. requires a uniform list-update date across the batch;
8. records observation time, source URL, list-update date and SHA-256 of the source payload.

A candidate route that cannot prove the header contract without crossing the pre-row evidence boundary remains non-live. ProcRun does not broaden retrieval merely to discover whether it might be safe.

## Privacy boundary

Prohibited:

- general OpenCoesione API ingestion into the intelligence plane;
- `Soggetti` / entity datasets outside the exact approved operation-list publication;
- project-detail HTML;
- arbitrary additional text fields;
- download of a broader unapproved dataset followed by local PII filtering;
- retaining beneficiary identity in the analytical `FundingProject` object.

## 2026-09-05 coverage-expansion result

Research PR #55 rechecked the all-program route first and Puglia second, using only public documentation and machine-verifiable network behavior. The correct Puglia source was the OpenCoesione-hosted programme ZIP, not the previously considered regional `dati.puglia.it` portal.

Result:

- all-program ZIP: **NOT ACTIVATED — bounded pre-row header qualification failed**;
- PR FESR FSE+ Puglia ZIP: **NOT ACTIVATED — bounded pre-row header qualification failed**;
- Lombardia: **remains the sole live OpenCoesione programme route**;
- INTERREG: not assessed in this round.

No human contact, permission request, source-owner clarification or download-then-filter fallback was used.

## Formal conclusion

**A1 PUBLIC-EVIDENCE SOURCE-FAMILY QUALIFICATION: PASS for `OpenCoesione 2021-2027 EU cohesion operation-list ZIP/CSV` only.**

**Runtime activation: PASS for PR FESR Lombardia 2021-2027 only as of 2026-09-05.**

The all-program and Puglia routes remain fail-closed and non-live until already-public, pre-row machine evidence can independently satisfy the exact transport/header gate. Their non-activation does not reduce or reopen the already accepted Lombardia production path.

Portugal PRR and related Category-B routes remain permanently blocked. This OpenCoesione decision does not revive them and does not alter the TED-scoped MVP OPEN contract.
