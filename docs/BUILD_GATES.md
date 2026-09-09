# ProcRun final build and release gates

Status: **WEB PRODUCT BUILD AUTHORIZED; CLASSIFICATION ENGINE PRODUCT VALIDATION NOT YET GREEN.**
Canonical product spec: `docs/PRODUCT_FOUNDATION_FINAL.md`
Pre-web baseline: `docs/PREWEB_RELEASE_BASELINE.md`
Sequencing rule: `docs/DELIVERY_READINESS_GATE.md`
Classification product-validation gate: `docs/CLASSIFICATION_ENGINE_VALIDATION_GATE.md`

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

Web implementation is authorized because the complete non-web delivery chain has passed production acceptance. This sequencing decision does **not** constitute empirical product validation of classification correctness under A21.

The existing fixture/shell web code remains non-authoritative; authorization to begin web development does not retroactively validate it.

## A7 — Unsupported claims

Do not claim complete Portuguese procurement coverage, complete Italian public-investment coverage, complete bill of materials, every future purchase, guaranteed lead time, win probability, buyer-person intelligence or source/EU endorsement. TED-scoped absence must never be shortened into national absence. OpenCoesione coverage remains limited to the approved 2021-2027 EU-cohesion operation-list universe.

## A8 — Pre-web delivery controls

**PASS.** All controls that genuinely belong to the non-web delivery chain are closed:

- approved source contracts and permanent no-contact rule;
- zero-PII intelligence boundary;
- live source transfer and complete TED retrieval;
- deterministic component/runway implementation and safe abstention behaviour;
- frozen customer-safe read model and source attribution text;
- append-only PostgreSQL persistence and run manifest;
- dedicated production runtime and secrets outside Git;
- PostgreSQL loopback-only and no unexpected public listener;
- provider backup plus verified logical backup/restore;
- active delivery and backup timers;
- fail-closed operational semantics;
- compliance/no-contact/static/type/test/TED-contract CI.

A8 proves delivery readiness and implementation integrity. It does **not** replace the A21 empirical classification-engine product-validation gate.

Customer application concerns — auth, Stripe, subscriptions, VAT/invoicing implementation, merchant identity presentation, Terms/Privacy pages, customer-control-plane processors, domain/TLS, cookies/logging and final rendered attribution — are part of the authorized web product phase. They remain mandatory before public paid launch, but are not prerequisites for starting that phase.

No external legal review or human response is an allowed gate-closing mechanism.

## A19 — Launch readiness excluding customer web application and empirical classification validation

**A19 PRE-WEB RELEASE READINESS: PASS.**

The non-web intelligence delivery path is operationally production-ready. Empirical classification-engine product validation is separately governed by A21 and remains open until its frozen real-project benchmark passes.

The production delivery evidence was established on runtime release `51c0071fe20011bb407d50c1df63a9d35ef68e76`. Subsequent housekeeping or validation-harness changes require green repository CI but not a repeat of the 176,540-notice production ingest unless classification/source semantics themselves require it.

## A20 — Web-build authorization and delivery readiness

A20 remains authoritative for web-build authorization, source/delivery readiness and the operational production path. It does not override A21 on empirical classification correctness.

**A20 WEB BUILD: GO — CUSTOMER APPLICATION DEVELOPMENT IS AUTHORIZED.**

**A20 LIVE PORTUGAL OPEN CLASSIFICATION: APPROVED (TED-SCOPED).**

Exact definition: **No relevant procurement found in TED as of DATE.** This does not establish absence outside TED.

**A20 OPENCOESIONE A1 SOURCE QUALIFICATION: APPROVED (EXACT 2021-2027 EU-COHESION OPERATION-LIST ROUTE).**

**A20 OPENCOESIONE COLLECTOR + FROZEN SCHEMA: IMPLEMENTED, FAIL-CLOSED.**

**A20 OPENCOESIONE LIVE SOURCE-TRANSFER: PASS ON DEDICATED PRODUCTION RUNTIME.**

**A20 LIVE FUNDED-PROJECT INGEST + CUSTOMER-SAFE DELIVERY: PASS.**

**A20 PRODUCTION RUNTIME + BACKUP/RESTORE + SCHEDULING: PASS.**

**A20 PRE-WEB RELEASE HOUSEKEEPING: PASS.**

Web development may proceed. A20 may not be cited as evidence that the classification engine has passed the independent real-project gold-standard benchmark.

## A21 — Classification-engine empirical product validation

**A21 CLASSIFICATION ENGINE PRODUCT VALIDATION: NOT YET GREEN.**

Authoritative specification: `docs/CLASSIFICATION_ENGINE_VALIDATION_GATE.md`.

A21 is the sole hard pass/fail gate for claims that ProcRun's final classification engine is empirically validated as the core paid product. Implementation completeness, unit tests, live production ingestion and green A20 delivery controls do not close A21.

A21 requires, among other frozen conditions:

- at least 200 real funded projects, or the complete qualifying universe if smaller;
- a disjoint >=25% general holdout;
- independent pre-frozen gold-standard components, evidence and states;
- complete adjudication of the dedicated release-candidate OPEN population;
- zero observed false OPEN;
- <=1% false CLOSED on holdout;
- >=95% exact ProjectState and ComponentState accuracy;
- >=95% component recall and >=98% component precision;
- 100% accepted CLOSED-match precision on holdout;
- 100% cutoff and coverage fail-closed integrity;
- a frozen adversarial suite with no Critical failure;
- three identical deterministic runs; and
- permanent regression gating after first GO.

If the same causal mechanism produces false OPEN in two separately frozen evaluation rounds, that mechanism is retired from OPEN-producing use and must fail closed to `UNRESOLVED` unless a new explicitly versioned mechanism later passes fresh independent validation.

The older local-model/component benchmark remains a continuous quality/diagnostic surface. It is not a competing final-classification release gate.

No file may claim **PRODUCT VALIDATED — CLASSIFICATION ENGINE: GO** until A21 itself is green.
