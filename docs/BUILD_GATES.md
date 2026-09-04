# ProcRun final build and release gates

Status: **WEB BUILD BLOCKED UNTIL FULL DELIVERY-READINESS IS GREEN; TED-SCOPED LIVE PROCUREMENT CLASSIFICATION APPROVED; OPENCOESIONE A1 SOURCE CONTRACT + FAIL-CLOSED COLLECTOR IMPLEMENTED; LIVE OPENCOESIONE SOURCE-TRANSFER CURRENTLY FAILS WITH HTTP 403 FROM GITHUB-HOSTED RUNTIME**
Canonical product spec: `docs/PRODUCT_FOUNDATION_FINAL.md`
Sequencing rule: `docs/DELIVERY_READINESS_GATE.md`

These gates are authoritative. Historical product files cannot override them.

## A0 — Permanent validation rule

ProcRun has no human-dependent validation path. No interview, outreach, authority/source-owner contact, customer contact, bespoke clarification, paid consultant/auditor/legal opinion or private assurance may close a source gate. Only already-public independently inspectable evidence and machine-verifiable behaviour may do so. Silence is never permission. If contact would be the only remaining route to approval, the source is rejected.

## A1 — Funded-project source

**A1 SOURCE QUALIFICATION: PASS for the exact OpenCoesione 2021-2027 EU-cohesion operation-list publication family.**

The approval is deliberately narrow. It applies to the purpose-published `Lista beneficiari e operazioni 2021-2027` ZIP/CSV surface. It does not approve the general OpenCoesione API, broad Projects/Soggetti database, project-detail HTML or arbitrary additional text fields.

Public evidence establishes CC BY 4.0 commercial reuse, automated public CSV publication, the 2021-2027 beneficiary-name restriction to legal persons, the RGS instruction that project title/summary must not contain natural-person information, a defined operation-list schema and the stated 2021-2027 EU-cohesion programme universe.

The RGS privacy rule is a provider/publication instruction, not a technical database constraint. Residual source-contract risk therefore remains explicit; observed violations fail closed rather than being filtered after receipt.

The production collector is implemented and registered. It pins the current PR FESR Lombardia transfer route, validates the exact ordered 17-column schema before row admission, rejects missing/additional/reordered fields, rejects whole batches on row failure, prevents redirect outside the frozen route, records source hash/timestamps, and maps only admitted non-person fields into `FundingProject`.

Current live-transfer result: **FAIL-CLOSED / HTTP 403** from the GitHub-hosted runtime before ZIP/schema validation. Browser-like headers did not remove the block. That transport attempt was rejected and not merged.

Remaining activation gates:

1. successful live source-transfer from an approved automated no-contact runtime against the same frozen source contract;
2. canonical end-to-end acceptance into the funded-project pipeline and customer-safe read boundary;
3. production drift/schema monitoring acceptance;
4. green CI.

Portugal PRR, Mais Transparência and PT2030 remain Category B and permanently closed. No human clarification path exists.

## A2 — Procurement source and MVP coverage

TED Search API is APPROVED for field-bounded procurement evidence, market context and MVP negative-search classification.

The permanent MVP `OPEN` definition is:

> **No relevant procurement found in TED as of DATE.**

This is not a claim that no procurement exists outside TED, including purely national or below-threshold procedures. Every customer-facing OPEN state must expose this boundary.

The production coverage code exposes only `CoverageScope.TED`; attempts to construct a broader OPEN scope fail closed.

## A3 — Absolute zero-PII intelligence boundary

No natural-person data may be collected, stored or processed in the intelligence plane. Account, billing and support data are a separate control plane. Broad-response receipt followed by filtering is prohibited.

## A4 — Evidence/state integrity

Every positive evidence object retains source identity, exact evidence, observation cutoff, method/version and immutable reference. `OPEN` is a bounded search conclusion, never a source fact. Incomplete TED pagination/retrieval or ambiguous matching yields `UNRESOLVED`.

Component states are `OPEN`, `CLOSED`, `UNRESOLVED`. Project aggregate states are `OPEN`, `PARTIAL`, `CLOSED`, `UNRESOLVED` when funded-project functionality is active. Any OPEN-derived state inherits the TED qualifier.

## A5 — Customer-safe boundary

Browser/API/export surfaces may consume only validated customer-safe read models. No raw source payload, beneficiary identity field or unvalidated model output may reach browser code.

## A6 — Permanent sequencing rule

**Web implementation is the final build phase and is BLOCKED until the entire non-web delivery chain is launch-ready.**

At the instant A20 changes `WEB BUILD` to `GO`, there must be no unresolved source, transport, live-ingest, canonical-pipeline, coverage, persistence/export, operational, billing/control-plane or release-control dependency other than the web interface itself.

Fixture/shell web work created before this rule was restored is non-authoritative and frozen. It must not be treated as a completed launch component or as permission to continue customer-facing web development.

## A7 — Unsupported claims

Do not claim complete Portuguese procurement coverage, complete Italian public-investment coverage, complete bill of materials, every future purchase, guaranteed lead time, win probability, buyer-person intelligence or source/EU endorsement. TED-scoped absence must never be shortened into national absence. OpenCoesione coverage must remain limited to the approved 2021-2027 EU-cohesion operation-list universe.

## A8 — Release controls before web GO

All non-web release controls must be launch-ready before web implementation begins. This includes applicable merchant/legal identity, terms/privacy content, VAT/invoicing design, processor inventory/DPAs, source attribution, TLS/secrets/least privilege, backup/restore, control-plane separation, billing backend contracts and operational runbooks. No external legal review is an allowed gate-closing mechanism.

## A19 — Launch readiness excluding final web interface

A19 is no longer a post-web checkout gate. **A19 must be green before A20 WEB BUILD can become GO**, except for controls that inherently require the final rendered web interface and can only be validated after that interface exists. Those final presentation checks may not conceal any unresolved backend, legal-content, billing, source or operational dependency.

## A20 — Authoritative readiness

A20 is the only authoritative readiness source.

**A20 WEB BUILD: BLOCKED — FULL DELIVERY-READINESS NOT YET GREEN.**

**A20 LIVE PORTUGAL OPEN CLASSIFICATION: APPROVED (TED-SCOPED).**

Exact definition: **No relevant procurement found in TED as of DATE.** This does not establish absence outside TED.

**A20 OPENCOESIONE A1 SOURCE QUALIFICATION: APPROVED (EXACT 2021-2027 EU-COHESION OPERATION-LIST ROUTE).**

**A20 OPENCOESIONE COLLECTOR + FROZEN SCHEMA: IMPLEMENTED, FAIL-CLOSED.**

**A20 OPENCOESIONE LIVE SOURCE-TRANSFER: BLOCKED — CURRENT GITHUB-HOSTED RUNTIME RECEIVES HTTP 403 BEFORE ZIP/SCHEMA VALIDATION.**

**A20 LIVE FUNDED-PROJECT INGEST: BLOCKED BY LIVE SOURCE-TRANSFER + END-TO-END ACCEPTANCE + GREEN CI.**

**A20 PRODUCT LAUNCH READINESS: BLOCKED.**

Web build may change to GO only when A20 can truthfully state that all non-web product delivery and release dependencies are green and the web interface is the sole remaining launch work.

No other README/spec/history file may claim broader readiness or coverage than this A20 decision.
