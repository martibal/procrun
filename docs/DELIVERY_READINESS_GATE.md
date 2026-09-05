# ProcRun delivery-readiness gate

## Permanent sequencing rule

Web implementation is the final product-development phase, not a parallel workstream.

The non-web intelligence product must be production-ready before authoritative customer-facing web work begins. That prerequisite is now satisfied.

The completed sequence is:

1. source contracts approved from public evidence only;
2. collectors implemented and fail-closed;
3. live source-transfer succeeded against real production sources;
4. canonical pipeline and customer-safe read model ran end-to-end on live inputs;
5. coverage semantics, OPEN boundaries, exports and persistence were verified;
6. regression, schema, compliance and no-contact gates passed;
7. production runtime, backup/restore and scheduling passed;
8. customer-safe contract, attribution and operational boundaries were frozen;
9. **customer-facing web product build is now authorized.**

## Current status

- TED source contract: **APPROVED**.
- TED-scoped OPEN semantics: **APPROVED**.
- OpenCoesione exact source contract: **APPROVED**.
- OpenCoesione collector/parser/schema: **IMPLEMENTED / FAIL-CLOSED**.
- OpenCoesione live source-transfer: **PASS on dedicated Hetzner production runtime**.
- Full live delivery: **PASS** — 4,631 funded projects -> 176,540 TED notices / 708 pages -> 81 projects with components -> 37 useful/resolved + 44 safely unresolved -> customer-safe JSONL + PostgreSQL manifest.
- Persistence/operations: **PASS** — verified logical restore, provider backup, PostgreSQL loopback-only, no unexpected public listener, active delivery/backup timers.
- Customer-safe intelligence contract: **FROZEN** as `customer-runway-v1`; see `docs/PREWEB_RELEASE_BASELINE.md`.
- Pre-web release housekeeping: **PASS**.
- Web product build: **GO** under A20.

The historical GitHub-hosted HTTP 403 is not a current blocker. GitHub Actions is not the production OpenCoesione transfer runtime.

## Web-phase scope

The customer application phase includes GUI/UX plus the control plane that exists because a customer application exists: authentication/session/account handling, Stripe/subscriptions if used, VAT/invoicing implementation, Terms/Privacy and merchant identity presentation, customer-control-plane processor inventory, domain/TLS, cookies/logging, rendered source attribution and final security/access/checkout testing.

These controls remain mandatory before public paid launch. They are intentionally not prerequisites for starting the web phase.

The permanent no-contact rule and zero-PII intelligence boundary remain unchanged throughout the web phase.
