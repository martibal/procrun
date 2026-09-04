# ProcRun final build and release gates

Status: **WEB BUILD APPROVED; TED-SCOPED LIVE PROCUREMENT CLASSIFICATION APPROVED; FUNDED-PROJECT INGEST REMAINS FAIL-CLOSED UNTIL A1 PASSES**
Canonical product spec: `docs/PRODUCT_FOUNDATION_FINAL.md`

These gates are authoritative. Historical product files cannot override them.

## A0 — Validation rule

ProcRun validation is zero-contact: no interviews, surveys, outreach, authority/source-owner contact, customer contact, bespoke clarification, paid consultant/auditor/legal opinion or private assurance may close a source gate. Only already-public independently inspectable evidence and machine-verifiable behaviour may do so. Silence is never permission.

## A1 — Funded-project source

Live funded-project ingest requires an approved Category A source with RIGHTS, ACCESS, TRANSPORT, FREE-TEXT SAFETY, SCHEMA and COVERAGE established for the exact production route.

PRR Projects and Mais Transparência are Category B and permanently closed to the intelligence plane under the current rules. They are not waiting for clarification.

OpenCoesione is the leading Category A replacement candidate. Official monitoring documentation explicitly constrains project title and summary against sensitive natural-person information and provides codified CUP-based monitoring structures, but exact machine-route qualification and source-transfer/live acceptance must pass before activation.

## A2 — Procurement source and MVP coverage

TED Search API is APPROVED for field-bounded procurement evidence, market context and MVP negative-search classification.

The permanent MVP `OPEN` definition is:

> **No relevant procurement found in TED as of DATE.**

This is not a claim that no procurement exists outside TED, including purely national or below-threshold Portuguese procedures. Every customer-facing OPEN state must expose the TED coverage boundary.

BASE/IMPIC, full DRE and Part L RSS are not required to make this bounded claim and remain disabled unless independently approved under A3.

## A3 — Absolute zero-PII intelligence boundary

No natural-person data may be collected, stored or processed in the intelligence plane. Account, billing and support data are a separate control plane. Broad-response receipt followed by filtering is prohibited.

## A4 — Evidence/state integrity

Every positive evidence object retains source identity, exact evidence, observation cutoff, method/version and immutable reference. `OPEN` is a bounded search conclusion, never a source fact. Incomplete TED pagination/retrieval or ambiguous matching yields `UNRESOLVED`.

Component states remain `OPEN`, `CLOSED`, `UNRESOLVED`; project aggregate states remain `OPEN`, `PARTIAL`, `CLOSED`, `UNRESOLVED` when funded-project functionality is active. Any OPEN-derived project state inherits the explicit TED qualifier.

## A5 — Customer-safe boundary

Browser/API/export surfaces consume only validated customer-safe read models. No raw source payload, beneficiary/contact/person field or unvalidated model output reaches browser code.

## A6 — Product/build scope

Web shell, authentication, account/billing skeleton, TED ingest/evidence, component/relevance code, saved opportunities, market context and customer-safe CSV export may be built now. Funded-project live screens remain fixture-only until A1 passes and must be clearly non-live.

## A7 — Unsupported claims

Do not claim complete Portuguese procurement coverage, complete bill of materials, every future purchase, guaranteed lead time, win probability, buyer-person intelligence or source/EU endorsement. TED-scoped absence must never be shortened into national absence.

## A8 — Paid release controls

Before checkout, A19 operational/legal controls must be green. Paid TED-scoped functionality does not require a funded-project source, but no funded-project feature may be represented as live until A1 plus source-transfer/live acceptance are green.

## A19 — Paid release

Before checkout: legal entity/merchant identity, terms, privacy notice, VAT/invoicing, processor inventory/DPAs, source attribution, TLS/secrets/least privilege, backup/restore and control-plane separation must be demonstrably green from applicable public requirements and implemented controls. No external legal review is an allowed gate-closing mechanism.

## A20 — Authoritative readiness

A20 is the only authoritative `GO` source for starting the web build.

**A20 WEB BUILD: GO.**

**A20 LIVE PORTUGAL OPEN CLASSIFICATION: APPROVED (TED-SCOPED).**

Exact definition: **No relevant procurement found in TED as of DATE.** This does not establish absence outside TED.

**A20 LIVE FUNDED-PROJECT INGEST: BLOCKED BY A1 CATEGORY-A SOURCE QUALIFICATION.**

**A20 TED-SCOPED PRODUCT RELEASE: TECHNICALLY SOURCE-ELIGIBLE; CHECKOUT STILL REQUIRES A19 + GREEN CI.**

Funded-project source qualification continues in parallel and is an expansion gate, not a blocker for the TED-scoped MVP.

No other README/spec/history file may claim broader coverage than this A20 decision.