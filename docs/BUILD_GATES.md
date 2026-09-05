# ProcRun final build and release gates

Status: **PRE-WEB RELEASE READINESS GREEN; WEB PRODUCT BUILD AUTHORIZED.**
Canonical product spec: `docs/PRODUCT_FOUNDATION_FINAL.md`
Pre-web baseline: `docs/PREWEB_RELEASE_BASELINE.md`
Sequencing rule: `docs/DELIVERY_READINESS_GATE.md`

These gates are authoritative. Historical product files cannot override them.

## A0 — Permanent validation rule

ProcRun has no human-dependent validation path. No interview, outreach, authority/source-owner contact, customer contact, bespoke clarification, paid consultant/auditor/legal opinion or private assurance may close a source gate. Only already-public independently inspectable evidence and machine-verifiable behaviour may do so. Silence is never permission. If contact would be the only remaining route to approval, the source is rejected.

## A1 — Funded-project source

**A1 SOURCE QUALIFICATION: PASS for the exact OpenCoesione 2021-2027 EU-cohesion operation-list publication family.**

The approval is deliberately narrow. It applies to the purpose-published `Lista beneficiari e operazioni 2021-2027` ZIP/CSV surface. It does not approve the general OpenCoesione API, broad Projects/Soggetti database, project-detail HTML or arbitrary additional text fields.

The production collector is fail-closed and maps only admitted non-person fields into `FundingProject`.

**Live production acceptance: PASS.** The dedicated Hetzner runtime completed the full OpenCoesione -> TED -> deterministic runway -> PostgreSQL ledger -> customer-safe JSONL chain on 2026-09-04/05: 4,631 funded projects, complete Italy TED universe of 176,540 notices / 708 pages, 81 published projects with components, 37 useful/resolved and 44 safely unresolved.

Portugal PRR, Mais Transparência and PT2030 remain Category B and permanently closed. No human clarification path exists.

## A2 — Procurement source and MVP coverage

TED Search API is APPROVED for field-bounded procurement evidence, market context and MVP negative-search classification.

The permanent MVP `OPEN` definition is:

> **No relevant procurement found in TED as of DATE.**

This is not a claim that no procurement exists outside TED, including purely national or below-threshold procedures. Every customer-facing OPEN state must expose this boundary. `CoverageScope` is TED-only and broader OPEN construction fails closed.

## A3 — Absolute zero-PII intelligence boundary

No natural-person data may be collected, stored or processed in the intelligence plane. Account, billing and support data belong to a separate customer control plane built during the web phase. Broad-response receipt followed by filtering is prohibited.

## A4 — Evidence/state integrity

Every positive evidence object retains source identity, exact evidence, observation cutoff, method/version and immutable reference. `OPEN` is a bounded search conclusion, never a source fact. Incomplete TED pagination/retrieval or ambiguous matching yields `UNRESOLVED`.

Component states are `OPEN`, `CLOSED`, `UNRESOLVED`. Project states are `OPEN`, `PARTIAL`, `CLOSED`, `UNRESOLVED`.

## A5 — Customer-safe boundary

**PASS / FROZEN.** `src/procrun/read_model.py`, version `customer-runway-v1`, is the sole intelligence contract intended for browser/API consumption. No raw source payload, beneficiary identity field, buyer/contact identity, model prompt or unvalidated candidate text may reach browser code. Exact fields and invariants are frozen in `docs/PREWEB_RELEASE_BASELINE.md`.

## A6 — Permanent sequencing rule

Web implementation is the final product-development phase. The complete non-web delivery chain is now production-ready, so the sequencing prerequisite is satisfied.

The existing fixture/shell web code remains non-authoritative; authorization to begin web development does not retroactively validate it.

## A7 — Unsupported claims

Do not claim complete Portuguese procurement coverage, complete Italian public-investment coverage, complete bill of materials, every future purchase, guaranteed lead time, win probability, buyer-person intelligence or source/EU endorsement. TED-scoped absence must never be shortened into national absence. OpenCoesione coverage remains limited to the approved 2021-2027 EU-cohesion operation-list universe.

## A8 — Pre-web release controls

**PASS.** All controls that genuinely belong to the non-web intelligence product are closed:

- approved source contracts and permanent no-contact rule;
- zero-PII intelligence boundary;
- live source transfer and complete TED retrieval;
- deterministic component/runway classification and safe abstention;
- frozen customer-safe read model and source attribution text;
- append-only PostgreSQL persistence and run manifest;
- dedicated production runtime and secrets outside Git;
- PostgreSQL loopback-only and no unexpected public listener;
- provider backup plus verified logical backup/restore;
- active delivery and backup timers;
- fail-closed operational semantics;
- compliance/no-contact/static/type/test/TED-contract CI.

Customer application concerns — auth, Stripe, subscriptions, VAT/invoicing implementation, merchant identity presentation, Terms/Privacy pages, customer-control-plane processors, domain/TLS, cookies/logging and final rendered attribution — are part of the authorized web product phase. They remain mandatory before public paid launch, but are not prerequisites for starting that phase.

No external legal review or human response is an allowed gate-closing mechanism.

## A19 — Launch readiness excluding customer web application

**A19 PRE-WEB RELEASE READINESS: PASS.**

The non-web intelligence product is production-ready. The remaining work is the customer-facing application and the controls inherently attached to that application.

The production delivery evidence was established on runtime release `51c0071fe20011bb407d50c1df63a9d35ef68e76`. Subsequent pre-web housekeeping changes are documentation/regression-gate changes and do not alter production-delivery semantics; they require green repository CI but not a repeat of the 176,540-notice production ingest.

## A20 — Authoritative readiness

A20 is the only authoritative readiness source.

**A20 WEB BUILD: GO — CORE PRODUCT DELIVERY IS PRODUCTION-READY. CUSTOMER APPLICATION IS THE SOLE REMAINING PRODUCT-DEVELOPMENT PHASE.**

**A20 LIVE PORTUGAL OPEN CLASSIFICATION: APPROVED (TED-SCOPED).**

Exact definition: **No relevant procurement found in TED as of DATE.** This does not establish absence outside TED.

**A20 OPENCOESIONE A1 SOURCE QUALIFICATION: APPROVED (EXACT 2021-2027 EU-COHESION OPERATION-LIST ROUTE).**

**A20 OPENCOESIONE COLLECTOR + FROZEN SCHEMA: IMPLEMENTED, FAIL-CLOSED.**

**A20 OPENCOESIONE LIVE SOURCE-TRANSFER: PASS ON DEDICATED PRODUCTION RUNTIME.**

**A20 LIVE FUNDED-PROJECT INGEST + CUSTOMER-SAFE DELIVERY: PASS.**

**A20 PRODUCTION RUNTIME + BACKUP/RESTORE + SCHEDULING: PASS.**

**A20 PRE-WEB RELEASE HOUSEKEEPING: PASS.**

**A20 PRODUCT LAUNCH READINESS: NOT YET COMPLETE — AUTHORIZED WEB PRODUCT PHASE REMAINS.**

Web development may now proceed. Public/paid launch remains blocked until the web-phase launch controls — including authentication/authorization, billing/Stripe if used, customer legal/privacy presentation, control-plane privacy, TLS/domain, source attribution, security and final end-to-end checkout/access tests — are green.

No other README/spec/history file may claim broader source coverage or launch readiness than this A20 decision.
