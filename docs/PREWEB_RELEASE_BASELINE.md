# ProcRun pre-web release baseline

Status date: 2026-09-05
Status: **PASS — core product delivery is production-ready; customer application is the next phase.**

This document freezes the boundary between the completed non-web product and the customer-facing web product build.

## Completed non-web product

The accepted production path is:

`OpenCoesione -> FundingProject -> deterministic component extraction -> complete TED evidence universe -> conservative matching/state -> project runway -> append-only PostgreSQL ledger -> customer-safe JSONL`

Production acceptance evidence:

- dedicated Hetzner `procrun-prod` runtime;
- successful live run on 2026-09-04/05;
- 4,631 funded projects admitted from the approved OpenCoesione route;
- 176,540 TED notices retrieved completely across 708 pages;
- 81 projects with components published;
- 37 useful/resolved and 44 safely `UNRESOLVED`;
- production run manifest present;
- logical PostgreSQL backup restored and verified (`restore_verified=true`);
- provider backup enabled;
- PostgreSQL loopback-only; no unexpected public TCP listener;
- delivery and backup systemd timers enabled and active;
- production release promoted to `51c0071fe20011bb407d50c1df63a9d35ef68e76` before pre-web housekeeping;
- delivery CI green on that runtime code: compliance, no-contact audit, shell/PowerShell syntax, Ruff, mypy, Python tests and TED live contract.

Documentation-only/test-housekeeping commits after that release do not alter production-delivery semantics and do not require a repeat of the 176,540-record live ingestion.

## Frozen customer-safe data contract

`src/procrun/read_model.py` is the sole intelligence contract the customer application may consume. `READ_MODEL_VERSION` is `customer-runway-v1`.

The browser/API layer may receive only `RunwayProject` and its nested customer-safe models. The project contract contains operation code, project title/dates, approved funding, programme/region/NUTS, source URL, project state, cutoff date, components, deterministic version identifiers and content hash. Components contain category/label/state, cutoff date, exact project evidence, accepted procurement matches, coverage note and state explanation. Procurement matches contain notice identity/date/title/source URL, CPV codes, optional estimated value/NUTS/project reference and an exact validated evidence span.

The web layer must not read the raw source transport, beneficiary identity fields, buyer/contact identity, model prompts, unvalidated candidate text or the internal append-only ledger directly. `PublicModel(extra="forbid", frozen=True)` and read-model invariant checks are part of this boundary.

Component states are `OPEN`, `CLOSED`, `UNRESOLVED`; project states are `OPEN`, `PARTIAL`, `CLOSED`, `UNRESOLVED`. `OPEN` is allowed only under complete TED coverage and means exactly:

> **No relevant procurement found in TED as of DATE.**

It must never be shortened to a national or universal absence claim.

## Frozen source attribution for the web phase

Customer-facing methodology/source surfaces must identify both production sources and preserve transformation/non-endorsement language.

TED attribution:

> Source: Tenders Electronic Daily (TED), Publications Office of the European Union. ProcRun transforms and classifies the source data; the derived analysis is not an official EU publication or endorsement.

OpenCoesione attribution:

> Source: OpenCoesione, Lista beneficiari e operazioni 2021-2027, used under CC BY 4.0. ProcRun transforms and classifies the source data; the derived analysis is not an official OpenCoesione, Italian-government or EU publication or endorsement.

The OpenCoesione statement applies only to the exact approved 2021-2027 EU-cohesion operation-list publication family. The current live route is PR FESR Lombardia. The broad OpenCoesione API/Projects/Soggetti surfaces are not approved.

## Operational contract

The intelligence runtime remains a non-web backend. It exposes no ProcRun application port. Publication fails closed on source transport/schema failure, incomplete TED retrieval, invalid evidence/read-model invariants, ledger failure or zero resolved customer output. Last accepted output remains in place when a new run fails; failure must never be represented as a fresh successful publication.

Daily logical backup is restore-verified. Provider backup is an independent recovery path. Production database credentials remain outside Git. The customer web application must not receive direct PostgreSQL credentials.

## What belongs to the web product phase

The following are intentionally **not pre-web blockers** because they are components of the customer application itself and cannot be meaningfully completed independently of that application:

- customer-facing GUI and navigation;
- authentication/session/account implementation;
- Stripe account activation and subscription integration;
- pricing -> checkout -> subscription -> customer portal/webhook flow;
- VAT/invoicing implementation tied to the chosen payment/customer flow;
- customer Terms/Privacy pages and merchant identity presentation;
- customer-control-plane processor/DPA inventory as actual providers are selected;
- domain, TLS and public reverse-proxy/application deployment;
- customer-control-plane logging/cookie/analytics decisions;
- final rendered source-attribution/methodology presentation;
- final accessibility, responsive, security-header, authz and checkout tests.

These are launch gates inside the web phase, not prerequisites for permission to begin that phase. The permanent no-contact rule remains in force throughout.

## Web-phase non-negotiable boundaries

1. No customer/account/payment PII may enter the intelligence ledger, source pipeline or model context.
2. No analytics, advertising or session-replay SDK is enabled by default.
3. Authentication/account/billing data is a separate control plane.
4. Stripe or any other new external service must pass its executable compliance gate before production activation.
5. Source attribution and the exact TED-scoped OPEN wording must be present before public launch.
6. The existing `web/` fixture/shell is non-authoritative input only; web development may replace it freely while preserving the frozen product/data contracts above.

## Decision

**PRE-WEB RELEASE HOUSEKEEPING: PASS.**

There is no remaining source, ingestion, classification, evidence, persistence, backup, scheduling, intelligence-security or non-web operational blocker. The next authorized phase is the customer-facing web product build, including its auth/billing/legal/control-plane implementation and final launch validation.
