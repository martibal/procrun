# ProcRun final build and release gates

Status: **WEB BUILD BLOCKED UNTIL REQUIRED PORTUGAL SOURCE CONTRACTS PASS FROM PUBLIC EVIDENCE ONLY**
Canonical product spec: `docs/PRODUCT_FOUNDATION_FINAL.md`

These gates are authoritative. Historical product files cannot override them.

## A0 — Pre-web completion rule

The user requires every plausible technical/data showstopper to be closed before UI implementation begins.

ProcRun validation is **zero-contact**:

- no interviews, surveys or customer/supplier outreach;
- no authority, source-owner or public-body contact;
- no bespoke clarification requests;
- no paid consultant, auditor or legal opinion as a substitute for source evidence;
- no private assurance or approval;
- only already-public, independently inspectable evidence and machine-verifiable behaviour may close a gate;
- silence is never permission.

Before A20 may become `WEB BUILD: GO`, all of the following must be complete:

- one funded-project source passes A1 entirely from public evidence;
- one complete-enough Portuguese national procurement source passes A2 entirely from public evidence;
- source-transfer validation passes for the funded-project source actually selected;
- A2/A3 source and zero-PII boundaries are enforced in code;
- canonical FundingProject -> component -> procurement -> state orchestration is covered by end-to-end tests;
- customer-safe read models are frozen and tested;
- component/project state ontology is internally consistent;
- deterministic hashes/version identifiers are available at the read boundary;
- database migrations apply from an empty PostgreSQL database and append-only invariants are tested;
- collectors fail closed on unknown fields, incomplete pagination, stale review, unapproved source or schema drift;
- incomplete required procurement coverage cannot produce `OPEN`;
- a live end-to-end acceptance replay passes on the approved source combination;
- CI is green;
- no known unresolved technical/data issue could force a browser-contract redesign after UI work begins.

## A1 — Funded-project source

A funded-project source may be approved only when RIGHTS, ACCESS, TRANSPORT, FREE-TEXT SAFETY, SCHEMA and COVERAGE are all established for the exact production route.

Required:

- explicit commercial reuse/derivative rights;
- publicly permitted automated recurring retrieval;
- no natural-person data can enter the intelligence plane before receipt;
- every retained free-text field has the same pre-receipt guarantee;
- no `download then filter` workaround;
- frozen schema/allowlist with fail-closed drift handling;
- sufficient funded-project coverage and temporal provenance.

`PRR Projects / dados.gov.pt` remains CONDITIONAL. Current public evidence does not close exact-route rights plus free-text safety. The former publisher-contact plan is retired because it violates A0.

A1 can close only if new public authoritative evidence appears or a different funded-project source passes the full contract without human-dependent clarification.

## A2 — Procurement source safety and coverage

TED Search API remains APPROVED for field-bounded procurement evidence and market context.

A Portuguese national procurement source must independently pass `docs/NATIONAL_PROCUREMENT_SOURCE_GATE.md` before it can satisfy national coverage for `OPEN`. Its approval must also be based entirely on public evidence and machine-verifiable behaviour.

Until national coverage is approved and completed, required-source coverage is incomplete and the classifier must return `UNRESOLVED`, never `OPEN` based on absence.

## A3 — Absolute zero-PII intelligence boundary

No natural-person data may be collected, stored or processed in the intelligence plane. Account, billing and support data live in a separate control plane and may not enter analytical ledger/model context.

## A4 — Canonical product object and state ontology

`funded project -> source-evidenced component -> procurement evidence -> conservative component state -> project aggregate state -> supplier runway`

Component states are exactly `OPEN`, `CLOSED`, `UNRESOLVED`.

Project states are exactly `OPEN`, `PARTIAL`, `CLOSED`, `UNRESOLVED`.

`PARTIAL` is a project-level aggregate state. A TED-only opportunity feed is not the canonical product.

## A5 — Evidence integrity

Every accepted positive component and procurement match retains exact source evidence, source identifier, observation cutoff, method/version and immutable hash/version reference.

No model/rule may invent source text, demand, procurement evidence or state.

Blanket claims such as `100% accurate`, `trust blindly` or `zero inference` are prohibited. `100% source-verified` may describe only a positive evidence object that actually satisfies the evidence contract.

## A6 — OPEN invariant

`OPEN` is not a source fact. It means only:

`No relevant procurement found in every required approved indexed source as of DATE.`

Incomplete coverage, review-band evidence or ambiguous component scope yields `UNRESOLVED`.

False OPEN is the highest-cost error.

## A7 — Matching hierarchy

Tier A/B evidence may close a component only under `MATCHING_RULES.md`. Tier C remains review-only. Semantic similarity alone never closes a component. Post-cutoff evidence never rewrites an earlier historical state.

## A8 — Component extraction

Deterministic extraction is primary. Supported domains/categories are frozen and versioned. Unmatched scope is retained and forces conservative abstention where necessary.

## A9 — Local model boundary

A production-approved local model may only propose a frozen category plus an exact source span from already-approved text. Deterministic validation must prove the span exists verbatim. The model cannot set component or procurement state.

The MVP does not depend on model fallback.

## A10 — Ledger/reproducibility

Source observations, extraction, candidate matching and classifications are append-only/versioned. Historical outputs retain cutoff, rule/model versions and SHA-256-linked evidence so results can be reconstructed.

## A11 — Customer-safe read model

Browser/API surfaces consume only the post-validation read model. No raw source response, beneficiary/contact/person field or unvalidated model output reaches the browser.

The read-model schema and deterministic content hash/version are implemented and regression-tested.

## A12 — Supplier relevance

Relevance is deterministic/profile-based and explainable. It may prioritize domain/category/CPV/geography/value preferences but cannot override evidence state and is never presented as win probability.

## A13 — Product UX

The customer-facing app centers on runway, not tender search:

- project/component feed;
- funded-project detail;
- component evidence/history;
- procurement evidence;
- saved items;
- market context;
- profile;
- customer-safe export;
- account shell.

## A14 — Trust UX

Every commercial runway item exposes project-scope evidence, procurement evidence where present, state wording, coverage status, observed/as-of timestamp and immutable version reference. Source facts and ProcRun conclusions are visually distinct.

## A15 — Market context integrity

TED market views disclose missingness. Funding aggregates remain disabled until A1 is green. Market context may not silently become the primary TED-only product.

## A16 — Commercial packaging

Launch package: **ProcRun Portugal — €149/month**. No permanent free tier. Sample/demo content must be synthetic or explicitly approved for publication.

## A17 — Unsupported claims

Do not claim complete bill of materials, every future purchase, guaranteed months-ahead lead time, complete procurement coverage, probabilistic GO/NO-GO, win probability, buyer-person intelligence or EU/source endorsement.

## A18 — Cost ceiling

Target recurring core infrastructure spend <= NOK 400/month; warning above NOK 400; architecture review required above NOK 500/month excluding volume-linked payment fees.

## A19 — Paid release

Before checkout, legal entity/merchant identity, terms, privacy notice, VAT/invoicing, processor inventory/DPAs, source attribution, TLS/secrets/least privilege, backup/restore and control-plane separation must be demonstrably green from applicable public requirements and implemented controls.

No external legal review is an allowed gate-closing mechanism under A0.

A1 and every source required for live `OPEN` coverage must also be production-approved.

## A20 — Authoritative web-build readiness

A20 is the only authoritative `GO` source for starting the web build.

**A20 WEB BUILD: BLOCKED.**

Internal technical hardening is largely complete, but the user's pre-build rule does not permit unresolved source contracts to be deferred until after UI work begins.

Current blockers:

1. no funded-project source is yet A1-approved entirely from public evidence;
2. no complete-enough Portuguese national procurement source is yet approved for absence-based `OPEN` coverage;
3. source-transfer validation cannot pass until a funded source is selected and approved;
4. live end-to-end acceptance cannot pass until the approved funded + procurement source combination exists.

**A20 LIVE FUNDED-PROJECT INGEST: BLOCKED BY A1.**

**A20 LIVE PORTUGAL OPEN CLASSIFICATION: BLOCKED BY NATIONAL SOURCE COVERAGE.**

**A20 PAID PRODUCTION: BLOCKED until A1 + national procurement-source gate + source-transfer/live acceptance + A19 are green.**

The next work is source qualification only. Do not start UI/web implementation and do not weaken the zero-contact, zero-PII, rights or coverage rules to obtain a source.

No other README/spec/history file may claim stronger readiness than A20.
