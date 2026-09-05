# Pre-web showstopper closure status

Status: **CLOSED — PRE-WEB RELEASE HOUSEKEEPING PASS; WEB PRODUCT BUILD AUTHORIZED.**

A20 in `docs/BUILD_GATES.md` is the authoritative readiness gate. The frozen handoff contract is `docs/PREWEB_RELEASE_BASELINE.md`.

## Closed gates

### Funded-project source

**PASS.** The exact OpenCoesione 2021-2027 EU-cohesion operation-list publication family is approved. The current live route is PR FESR Lombardia. Broad OpenCoesione API/Projects/Soggetti routes remain outside the contract.

### Procurement source and OPEN boundary

**PASS.** TED Search API is the declared MVP procurement-evidence universe. `OPEN` means exactly:

> **No relevant procurement found in TED as of DATE.**

Incomplete retrieval or ambiguous matching yields `UNRESOLVED`.

### Live end-to-end delivery

**PASS.** Dedicated production runtime completed OpenCoesione -> FundingProject -> component extraction -> complete TED evidence -> conservative matching/state -> runway -> append-only PostgreSQL -> customer-safe JSONL on real data.

Accepted run: 4,631 funded projects; 176,540 TED notices / 708 pages; 81 projects with components; 37 useful/resolved; 44 safely unresolved.

### Component fallback

**PASS FOR MVP CONTRACT.** Deterministic-only extraction with safe abstention is the production contract. No local model is required for launch. Ambiguous scope remains `UNRESOLVED`.

### Persistence and reconstruction

**PASS.** Append-only ledger and customer-safe read boundary are implemented; production manifest exists; logical backup was restored and verified.

### Runtime and operations

**PASS.** Dedicated Hetzner runtime, provider backup, loopback-only PostgreSQL, no unexpected public TCP listener, fail-closed publication, and active delivery/backup timers are verified.

### Customer-safe contract and attribution

**PASS / FROZEN.** `customer-runway-v1` is the sole intelligence contract for the customer application. TED/OpenCoesione attribution and non-endorsement wording are frozen in `docs/PREWEB_RELEASE_BASELINE.md`.

## Historical 403

The GitHub-hosted OpenCoesione HTTP 403 is historical evidence only. GitHub-hosted CI is not used as the production source-transfer runtime. The dedicated production runtime passed the same frozen source contract without widening the route or weakening the zero-PII boundary.

## Web handoff

**A20 WEB BUILD: GO.**

The next phase is the customer-facing product: GUI/UX, authentication/account control plane, Stripe/subscription flow if used, VAT/invoicing implementation, Terms/Privacy and merchant identity presentation, domain/TLS, customer-control-plane privacy/logging, rendered attribution/methodology and final launch/security testing.

Those are web-phase launch controls, not unresolved pre-web showstoppers.
