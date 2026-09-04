# Pre-web showstopper closure status

Status: **WEB BUILD BLOCKED UNTIL THE COMPLETE NON-WEB DELIVERY CHAIN IS LAUNCH-READY**

A20 in `docs/BUILD_GATES.md` remains the only authoritative readiness gate. This file is a supporting checklist and may never weaken A20.

## Permanent sequencing rule

Web implementation is the final build phase. It may not start or continue while any source, runtime, live-ingest, pipeline, persistence, export, operational, compliance or non-visual release dependency remains unresolved.

Fixture/shell web code created before this rule was restored is frozen and non-authoritative. It is not evidence of readiness and is not permission to continue web development.

## 1. Funded-project source A1

**Status: SOURCE CONTRACT APPROVED; LIVE DELIVERY BLOCKED BY RUNTIME ACCEPTANCE.**

The exact OpenCoesione 2021-2027 EU-cohesion operation-list publication family is approved from public evidence for the bounded route documented in `OPENCOESIONE_A1_QUALIFICATION.md`. The currently pinned live pilot is PR FESR Lombardia.

The broad OpenCoesione API, Projects/Soggetti surfaces and arbitrary additional fields remain outside the approved contract.

The fail-closed collector and canonical `FundingProject` mapping are implemented. Beneficiary identity fields never enter the canonical analytical object.

Live source-transfer is not accepted yet. GitHub-hosted Azure runners return HTTP 403 even for the official OpenCoesione publication landing page, so GitHub Actions is rejected as the production source-transfer runtime. The approved source contract itself is not invalidated by that network-specific block.

Closure requires a successful automated source-transfer on an approved non-GitHub production runtime against the exact same frozen route and schema.

## 2. Procurement source and OPEN boundary

**Status: APPROVED FOR THE MVP.**

TED Search API is the approved procurement-evidence source and the complete declared search universe for the MVP negative-search conclusion.

The only allowed MVP `OPEN` meaning is:

> **No relevant procurement found in TED as of DATE.**

A Portuguese national procurement source is **not** required for this bounded MVP state. The product must never shorten TED-scoped absence into national absence or imply coverage of purely national/below-threshold procurement outside TED.

Any incomplete TED retrieval, unresolved scope boundary or ambiguous matching yields `UNRESOLVED` rather than `OPEN`.

## 3. Live end-to-end delivery

**Status: BLOCKED BY LIVE OPENCOESIONE RUNTIME ACCEPTANCE.**

The internal canonical path is already exercised with deterministic fixtures:

`FundingProject -> component extraction -> TED evidence -> candidate matching -> component state -> project aggregation -> customer-safe read model -> deterministic content hash`

Before web GO, the same path must complete on real OpenCoesione data from the approved production runtime and persist its accepted provenance/state through the production ledger/read boundary.

A fixture replay is not a substitute for this live acceptance.

## 4. Component fallback

**Status: DETERMINISTIC-ONLY MVP; SAFE ABSTENTION IS THE PRODUCTION CONTRACT.**

No local model is production-approved. The current MVP therefore does not depend on model fallback.

Deterministic extraction may produce a state only where the scope boundary is resolved under the frozen component rules. Unmatched or ambiguous scope remains `UNRESOLVED`; it cannot create `OPEN`.

The local Ministral candidate remains benchmark-only. It is not a hidden launch dependency unless the product contract is changed to require model-resolved scope before launch.

Live acceptance must nevertheless demonstrate that the approved real-data route produces a nonzero useful deterministic customer output; otherwise the product is not delivery-ready even though it fails safely.

## 5. Persistence and reconstruction

**Status: IMPLEMENTED AND REGRESSION-TESTED; PRODUCTION-RUNTIME ACCEPTANCE STILL REQUIRED.**

The append-only PostgreSQL ledger, immutable source/evidence versions, exact evidence spans, migration-from-empty coverage, reconstruction hashes and storage-budget safeguards are implemented and tested.

Before web GO, migrations, write/reconstruction and backup/restore must also be exercised on the selected production runtime. Test-container success alone does not close operational readiness.

## 6. Runtime and operations

**Status: BLOCKED.**

GitHub-hosted runners are rejected for OpenCoesione source-transfer. ProcRun already has an approved Hetzner Cloud service contract for EU VPS hosting, making a dedicated ProcRun runtime the current production target.

Required before web GO:

1. dedicated ProcRun runtime provisioned without sharing Urd Atlas/Trendanalytics infrastructure;
2. source-transfer and full delivery job scheduled automatically;
3. database reachable only through the intended private/local boundary;
4. secrets absent from Git and logs;
5. schema/drift/compliance failures stop publication fail-closed;
6. backup and restore path demonstrably works;
7. operational runbook and health/failure semantics are frozen.

## 7. Non-web release controls

**Status: NOT YET CLOSED.**

All controls that can be completed without the final rendered web interface must be ready before A20 WEB BUILD becomes GO. Final presentation-only checks may remain for the web phase, but no backend, source, billing-contract, legal-content, operational or security dependency may be deferred behind web implementation.

Stripe/account-specific activation is not part of the current source/runtime fix and must not be touched merely to unblock OpenCoesione. It is assessed separately when the rest of the delivery chain reaches that gate.

## Current blocker order

1. production runtime for exact OpenCoesione source-transfer;
2. live OpenCoesione -> TED -> runway -> ledger/read-model acceptance;
3. production persistence plus backup/restore and operational acceptance;
4. remaining non-web release controls;
5. full compliance/regression/CI and repository-status reconciliation;
6. only then: **A20 WEB BUILD: GO**.

## Final consequence

**Do not build the web now.**

A20 changes to WEB BUILD GO only when the web interface is truthfully the sole remaining launch work.