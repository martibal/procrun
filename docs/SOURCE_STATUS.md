# ProcRun source status

Status date: 2026-09-04
Canonical product spec: `docs/PRODUCT_FOUNDATION_FINAL.md`
Authoritative readiness gate: `docs/BUILD_GATES.md` A20

## Production rule

Every live source must be registered in `procrun.source_contracts` and pass `require_live_source()` before network retrieval. A route is usable only when RIGHTS, ACCESS and DATA SAFETY are all APPROVED. Public availability alone is insufficient.

## Category A/B classification

This classification applies to every future intelligence-source review.

### Category A — eligible for no-contact qualification

A source is Category A only when the exact production route can be bounded from public evidence before receipt: structured machine-generated or strictly codified fields, or an authoritative server-side field projection, with no human-authored free text entering the intelligence plane unless that text has an explicit public pre-publication zero-natural-person guarantee.

Typical examples include TED projected metadata, EUR-Lex metadata, Eurostat/statistical series, codified trade statistics and blockchain ledger data. Category A is eligibility for qualification, not automatic approval: rights, automated access, schema, coverage and safety still have to pass.

### Category B — permanently ineligible under the current zero-contact/zero-PII rules

A source is Category B when the required production response contains human-authored free text or identity-bearing surfaces from a publisher that does not publicly guarantee pre-publication exclusion/anonymisation for every consumed field and does not expose a safe server-side projection.

Category B sources are not `waiting for clarification`. They are closed to the intelligence plane unless the publisher later changes its already-public technical/data contract enough to make an exact route Category A. ProcRun never contacts the publisher to obtain that change or assurance.

## Current source registry decision

| Source | Category | Overall | Role / decision |
| --- | --- | --- | --- |
| TED Search API projected route | A | APPROVED | MVP procurement evidence, market context and TED-scoped negative-search coverage |
| PRR Projects on dados.gov.pt | B | PERMANENTLY BLOCKED | Human-authored project title/scope route lacks exact public pre-publication safety contract |
| Mais Transparência project detail HTML | B | PERMANENTLY BLOCKED | Human-authored project detail plus beneficiary surface |
| PT2030 operations bulk workbook | B | PERMANENTLY BLOCKED | Broad route; no download-then-filter |
| Portal BASE / APIBase2 | B for current route | BLOCKED | Identity-bearing/broad response; no safe projection |
| OpenCoesione 2021-2027 EU cohesion operation-list CSV | A | APPROVED SOURCE CONTRACT | Exact bounded Italian funded-operation route; live activation still requires collector registration, frozen-schema tests, source-transfer validation and live acceptance |
| General OpenCoesione API / broad Projects database | B for ProcRun transport | BLOCKED | Broader response surface is not required and is not approved by the operation-list decision |
| Poland public project-register/story surfaces reviewed 2026-09-04 | B | REJECTED | Public project material is human-authored narrative; no exact pre-receipt zero-person machine route established |

## PRR final decision

PRR Projects and equivalent Mais Transparência project surfaces are **Category B — permanently closed for the intelligence plane under the current rules**. They are no longer preferred candidates and no human clarification path exists.

The canonical `FundingProject` interface remains source-agnostic so an approved Category A source can implement it without changing downstream component, evidence or read-model contracts.

## Italy — OpenCoesione exact approved route

The exact approved source contract is documented in `docs/OPENCOESIONE_A1_QUALIFICATION.md`.

The approved transport is **not** the general OpenCoesione API or broad relational project database. It is the purpose-published 2021-2027 EU-cohesion `Lista beneficiari e operazioni` CSV publication surface.

Public evidence closes the six A1 dimensions for that exact route:

- **RIGHTS:** OpenCoesione data are CC BY 4.0; OpenCoesione explicitly permits reuse, modification, redistribution and commercial reuse with attribution.
- **ACCESS:** the operation lists are publicly published as open CSV specifically for reuse, processing and extraction; no human approval or authenticated API is required for this route.
- **TRANSPORT:** the route is a bounded regulatory operation-list publication and does not require receipt of the broad Projects/Soggetti database followed by filtering.
- **FREE-TEXT SAFETY:** RGS monitoring rules state that `TITOLO_PROGETTO` and `SINTESI_PROG` must not contain sensitive information attributable to natural persons, expressly including name, tax code, phone number and email. The operation-list publication states beneficiary names are published only for legal persons.
- **SCHEMA:** the operation-list publication has a defined regulatory minimum field set and linked metadata; production implementation must freeze the exact CSV header allowlist and fail closed on drift.
- **COVERAGE:** OpenCoesione states that the complete list covers all national and regional 2021-2027 programmes financed with EU funds and is updated bimonthly.

The coverage claim is intentionally narrow: this is the Italian 2021-2027 EU-cohesion operation universe represented by that publication. It is not a claim about all Italian public investment, all FSC/national funding, or all Italian procurement.

**A1 public-evidence qualification: PASS for the exact OpenCoesione 2021-2027 EU-cohesion operation-list CSV route.**

### Activation state

Source qualification and live activation are separate gates. The source is now approved on the documentary/public-evidence contract, but live ingest remains disabled until all of the following are implemented and green:

1. source-contract registry entry for the exact operation-list route;
2. fixed programme-universe manifest / approved URL family;
3. content-type and frozen-header validation before row processing;
4. fail-closed handling for any unknown/additional/missing field or route change;
5. source observation timestamp, list-update date and content hash provenance;
6. source-transfer validation against the canonical `FundingProject` contract;
7. live end-to-end acceptance;
8. green CI.

Beneficiary identity is not part of the ProcRun analytical contract and must not be retained even where the source publishes a legal-person beneficiary.

## Poland — public EU-funds project surfaces: Category B / rejected for this route

The reviewed Polish public EU-funds project pages expose narrative human-authored project goals/descriptions and beneficiary information. Public open-data standards encourage reusable structured publication, but the reviewed project surfaces do not establish an exact machine route with a pre-publication zero-natural-person guarantee for all project text ProcRun would need.

**Conclusion:** rejected under Category B for funded-project intelligence unless a different already-public projected/codified machine route is found later.

## TED production contract and MVP OPEN

TED Search API remains approved with explicit server-side field projection, bounded pagination, schema validation and no prohibited buyer/contact/supplier-person fields in the retained response surface.

For the MVP, `OPEN` means exactly:

> **No relevant procurement found in TED as of DATE.**

It does not mean that no procurement exists outside TED, including purely national or below-threshold Portuguese procedures.

## Zero-PII rule

> **Do not receive a broad response containing prohibited fields and discard them afterwards.**

No natural-person data may enter the intelligence plane. Account/billing/support PII is a separate control plane and is not an exception.

## Activation procedure

A Category A source becomes live-usable only through one reviewed implementation change containing the approved documentary contract, frozen route/schema/allowlist, fail-closed collector tests, review-expiry policy, source-transfer validation where applicable, updated A20 state and green CI.

Until the OpenCoesione activation steps above pass, downstream funded-project features remain fixture-driven. TED-scoped procurement functionality is independently production-eligible under its existing approved contract.