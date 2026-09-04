# ProcRun final build and release gates

Status: **WEB BUILD ACTIVE; TED-SCOPED LIVE PROCUREMENT CLASSIFICATION APPROVED; OPENCOESIONE A1 SOURCE CONTRACT + FAIL-CLOSED COLLECTOR IMPLEMENTED; LIVE FUNDED-PROJECT ACTIVATION AWAITS TRANSFER/E2E ACCEPTANCE + GREEN CI**
Canonical product spec: `docs/PRODUCT_FOUNDATION_FINAL.md`

These gates are authoritative. Historical product files cannot override them.

## A0 — Permanent validation rule

ProcRun has no human-dependent validation path. No interview, outreach, authority/source-owner contact, customer contact, bespoke clarification, paid consultant/auditor/legal opinion or private assurance may close a source gate. Only already-public independently inspectable evidence and machine-verifiable behaviour may do so. Silence is never permission. If contact would be the only remaining route to approval, the source is rejected.

## A1 — Funded-project source

**A1 SOURCE QUALIFICATION: PASS for the exact OpenCoesione 2021-2027 EU-cohesion operation-list publication family.**

The approval is deliberately narrow. It applies to the purpose-published `Lista beneficiari e operazioni 2021-2027` ZIP/CSV surface. It does not approve the general OpenCoesione API, broad Projects/Soggetti database, project-detail HTML or arbitrary additional text fields.

Public evidence establishes CC BY 4.0 commercial reuse, automated public CSV access, the 2021-2027 beneficiary-name restriction to legal persons, the RGS instruction that project title/summary must not contain natural-person information, a defined operation-list schema and the stated 2021-2027 EU-cohesion programme universe.

The RGS privacy rule is a provider/publication instruction, not a technical database constraint. Residual source-contract risk therefore remains explicit; observed violations fail closed rather than being filtered after receipt.

The production collector is implemented and registered. It pins the current PR FESR Lombardia transfer route, validates the exact ordered 17-column schema before row admission, rejects missing/additional/reordered fields, rejects whole batches on row failure, prevents redirect outside the frozen route, records source hash/timestamps, and maps only admitted non-person fields into `FundingProject`.

Remaining activation gates are only:

1. live source-transfer against the pinned route;
2. canonical end-to-end acceptance into the funded-project pipeline/read boundary;
3. green CI.

Portugal PRR, Mais Transparência and PT2030 remain Category B and permanently closed. No human clarification path exists.

## A2 — Procurement source and MVP coverage

TED Search API is APPROVED for field-bounded procurement evidence, market context and MVP negative-search classification.

The permanent MVP `OPEN` definition is:

> **No relevant procurement found in TED as of DATE.**

This is not a claim that no procurement exists outside TED, including purely national or below-threshold procedures. Every customer-facing OPEN state must expose this boundary.

The production coverage code exposes only `CoverageScope.TED`; attempts to construct a broader OPEN scope fail closed. API/UI fixture surfaces use the same wording and disclaimer.

## A3 — Absolute zero-PII intelligence boundary

No natural-person data may be collected, stored or processed in the intelligence plane. Account, billing and support data are a separate control plane. Broad-response receipt followed by filtering is prohibited.

## A4 — Evidence/state integrity

Every positive evidence object retains source identity, exact evidence, observation cutoff, method/version and immutable reference. `OPEN` is a bounded search conclusion, never a source fact. Incomplete TED pagination/retrieval or ambiguous matching yields `UNRESOLVED`.

Component states are `OPEN`, `CLOSED`, `UNRESOLVED`. Project aggregate states are `OPEN`, `PARTIAL`, `CLOSED`, `UNRESOLVED` when funded-project functionality is active. Any OPEN-derived state inherits the TED qualifier.

## A5 — Customer-safe boundary

Browser/API/export surfaces consume only validated customer-safe read models. No raw source payload, beneficiary identity field or unvalidated model output reaches browser code.

## A6 — Product/build scope

The Next.js web application may be developed now against fixtures/customer-safe read models. Current build scope includes application navigation/design system, supplier profile onboarding shell, opportunity feed/detail with evidence chain, market context, saved opportunities, customer-safe CSV export and account/billing shell.

Fixture data must be visibly labelled non-live. Italian funded-project output may not be represented as live until the A1 activation gates above pass.

## A7 — Unsupported claims

Do not claim complete Portuguese procurement coverage, complete Italian public-investment coverage, complete bill of materials, every future purchase, guaranteed lead time, win probability, buyer-person intelligence or source/EU endorsement. TED-scoped absence must never be shortened into national absence. OpenCoesione coverage must remain limited to the approved 2021-2027 EU-cohesion operation-list universe.

## A8 — Paid release controls

Before checkout, A19 operational/legal controls and green CI are required. Paid TED-scoped functionality does not require Italian funded-project activation.

## A19 — Paid release

Before checkout: legal entity/merchant identity, terms, privacy notice, VAT/invoicing, processor inventory/DPAs, source attribution, TLS/secrets/least privilege, backup/restore and control-plane separation must be demonstrably green from applicable public requirements and implemented controls. No external legal review is an allowed gate-closing mechanism.

## A20 — Authoritative readiness

A20 is the only authoritative readiness source.

**A20 WEB BUILD: GO / ACTIVE.**

**A20 LIVE PORTUGAL OPEN CLASSIFICATION: APPROVED (TED-SCOPED).**

Exact definition: **No relevant procurement found in TED as of DATE.** This does not establish absence outside TED.

**A20 OPENCOESIONE A1 SOURCE QUALIFICATION: APPROVED (EXACT 2021-2027 EU-COHESION OPERATION-LIST ROUTE).**

**A20 OPENCOESIONE COLLECTOR + FROZEN SCHEMA: IMPLEMENTED, FAIL-CLOSED.**

**A20 LIVE FUNDED-PROJECT INGEST: BLOCKED ONLY BY LIVE SOURCE-TRANSFER + END-TO-END ACCEPTANCE + GREEN CI.**

**A20 TED-SCOPED PRODUCT RELEASE: TECHNICALLY SOURCE-ELIGIBLE; CHECKOUT STILL REQUIRES A19 + GREEN CI.**

No other README/spec/history file may claim broader coverage than this A20 decision.
