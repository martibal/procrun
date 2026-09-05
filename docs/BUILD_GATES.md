# ProcRun final build and release gates

Status: **WEB BUILD REMAINS BLOCKED ONLY BY REMAINING NON-WEB RELEASE CONTROLS; TED-SCOPED LIVE PROCUREMENT CLASSIFICATION APPROVED; OPENCOESIONE A1 LIVE DELIVERY + PRODUCTION RUNTIME ACCEPTED; FINAL DELIVERY CI GREEN**
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

The production collector is implemented and registered. It pins the approved PR FESR Lombardia transfer route, validates the exact frozen schema before row admission, rejects missing/additional/reordered fields, rejects whole batches on row failure, prevents redirect outside the frozen route, records source hash/timestamps, and maps only admitted non-person fields into `FundingProject`.

**Live production acceptance: PASS.** The dedicated Hetzner runtime completed the full OpenCoesione -> TED -> deterministic runway -> PostgreSQL ledger -> customer-safe JSONL chain on 2026-09-04/05. The accepted run processed 4,631 funded projects, completed the Italy TED universe at 176,540 notices across 708 pages, published 81 projects with components, produced 37 useful/resolved projects and 44 safely unresolved projects, and exited cleanly.

The production runtime also passed logical PostgreSQL backup + scratch restore verification (`restore_verified=true`), retained a production run manifest, exposed PostgreSQL on loopback only, exposed no unexpected public TCP listener, and has both delivery and backup systemd timers enabled and active.

The current production release is `51c0071fe20011bb407d50c1df63a9d35ef68e76`. Final CI on that commit is green for compliance, permanent no-contact audit, shell/PowerShell syntax, Ruff, mypy, Python tests and the live TED contract. Customer-facing web CI remains intentionally skipped until A20 WEB BUILD becomes GO.

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

**Web implementation is the final build phase and is BLOCKED until the entire non-web delivery chain and all non-web release controls are launch-ready.**

The source, transport, live-ingest, canonical-pipeline, coverage, persistence/export and production-runtime portions of that rule are now green. Web remains blocked until the remaining A8/A19 release controls are closed.

Fixture/shell web work created before this rule was restored is non-authoritative and frozen. It must not be treated as a completed launch component or as permission to continue customer-facing web development.

## A7 — Unsupported claims

Do not claim complete Portuguese procurement coverage, complete Italian public-investment coverage, complete bill of materials, every future purchase, guaranteed lead time, win probability, buyer-person intelligence or source/EU endorsement. TED-scoped absence must never be shortened into national absence. OpenCoesione coverage must remain limited to the approved 2021-2027 EU-cohesion operation-list universe.

## A8 — Release controls before web GO

All non-web release controls must be launch-ready before web implementation begins. This includes applicable merchant/legal identity, terms/privacy content, VAT/invoicing design, processor inventory/DPAs, source attribution, TLS/secrets/least privilege, backup/restore, control-plane separation, billing backend contracts and operational runbooks. No external legal review is an allowed gate-closing mechanism.

Runtime/security controls already accepted: dedicated production host, provider backups enabled, logical backup/restore verified, PostgreSQL loopback-only, no unexpected public listener, secrets outside Git, fail-closed publication, active scheduled delivery/backup timers and green CI.

Remaining A8 work is limited to the non-web commercial/control-plane/release package that does not inherently require a rendered web interface.

## A19 — Launch readiness excluding final web interface

A19 must be green before A20 WEB BUILD can become GO, except for controls that inherently require the final rendered web interface and can only be validated after that interface exists. Those final presentation checks may not conceal any unresolved backend, legal-content, billing, source or operational dependency.

**A19 DELIVERY/RUNTIME SUBGATE: PASS.**

**A19 NON-WEB RELEASE-CONTROL SUBGATE: OPEN.** Merchant/legal identity, terms/privacy content, VAT/invoicing design, processor/DPA inventory, source-attribution packaging, billing backend contracts/control-plane separation and final operational/release runbook reconciliation must be closed before A20 WEB BUILD becomes GO.

## A20 — Authoritative readiness

A20 is the only authoritative readiness source.

**A20 WEB BUILD: BLOCKED — REMAINING NON-WEB RELEASE CONTROLS NOT YET GREEN.**

**A20 LIVE PORTUGAL OPEN CLASSIFICATION: APPROVED (TED-SCOPED).**

Exact definition: **No relevant procurement found in TED as of DATE.** This does not establish absence outside TED.

**A20 OPENCOESIONE A1 SOURCE QUALIFICATION: APPROVED (EXACT 2021-2027 EU-COHESION OPERATION-LIST ROUTE).**

**A20 OPENCOESIONE COLLECTOR + FROZEN SCHEMA: IMPLEMENTED, FAIL-CLOSED.**

**A20 OPENCOESIONE LIVE SOURCE-TRANSFER: PASS ON DEDICATED PRODUCTION RUNTIME.**

**A20 LIVE FUNDED-PROJECT INGEST + CUSTOMER-SAFE DELIVERY: PASS.**

**A20 PRODUCTION RUNTIME + BACKUP/RESTORE + SCHEDULING + FINAL DELIVERY CI: PASS.**

**A20 PRODUCT LAUNCH READINESS: BLOCKED ONLY BY REMAINING NON-WEB RELEASE CONTROLS AND THE FINAL WEB INTERFACE.**

Web build may change to GO only when A19 confirms that the remaining non-web release-control package is green and the web interface is truthfully the sole remaining launch work.

No other README/spec/history file may claim broader readiness or coverage than this A20 decision.
