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
| OpenCoesione monitored project route | A-CANDIDATE | QUALIFICATION CANDIDATE | Public monitoring rules explicitly constrain project title and summary against sensitive natural-person information; exact route/schema/coverage still requires source-contract qualification |
| Poland public project-register/story surfaces reviewed 2026-09-04 | B | REJECTED | Public project material is human-authored narrative; no exact pre-receipt zero-person machine route established |

## PRR final decision

PRR Projects and equivalent Mais Transparência project surfaces are **Category B — permanently closed for the intelligence plane under the current rules**. They are no longer preferred candidates and no human clarification path exists.

The canonical `FundingProject` interface remains source-agnostic so a future Category A source can implement it without changing downstream component, evidence or read-model contracts.

## Alternative-country funded-project assessment

### Italy — OpenCoesione: Category A candidate, not yet production-approved

Public OpenCoesione/RGS monitoring documentation materially changes the free-text assessment. The current monitoring vademecum defines the project registry structure `AP00` with `TITOLO_PROGETTO` and `SINTESI_PROG` and explicitly instructs that neither field may contain sensitive information attributable to natural persons, including name, tax code, telephone or email. Earlier official monitoring guidance also specifies natural-person beneficiaries as `Individuo` and prohibits natural-person names in operation titles.

The same monitoring protocol is highly structured around CUP and codified project/financial/procedural structures; current RGS documentation includes the `AFFIDAMENTO_TRAMITE_CIG` field in the obligation structure, showing a codified project-to-procurement relationship surface.

**Conclusion:** OpenCoesione is the first replacement route that passes the Category A/B *eligibility* screen for the project text needed by ProcRun. It is not silently production-approved: the exact machine distribution, commercial reuse, automated access, retained field allowlist, coverage and drift contract must still be frozen and tested before live ingest.

### Poland — public EU-funds project surfaces: Category B / rejected for this route

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

A Category A funded-project candidate becomes APPROVED only through one reviewed change containing authoritative rights/access/data-safety evidence, frozen route/schema/allowlist, fail-closed collector tests, review-expiry policy, source-transfer validation where applicable, updated A1/A20 state and green CI.

Until then, downstream funded-project features use the canonical interface and fixtures. TED-scoped procurement functionality is independently production-eligible under its existing approved contract.