# ProcRun source status

Status date: 2026-09-05
Canonical product spec: `docs/PRODUCT_FOUNDATION_FINAL.md`
Authoritative readiness gate: `docs/BUILD_GATES.md` A20

## Production rule

Every live source must be registered in `procrun.source_contracts` and pass `require_live_source()` before retrieval. Approval uses already-public evidence only. If human contact would be required to resolve a source gate, the source is rejected.

## Category A/B classification

### Category A — eligible for no-contact qualification

The exact production route is publicly bounded before receipt and satisfies rights, access, schema, coverage and data-safety requirements.

### Category B — permanently ineligible under current rules

The required response cannot satisfy ProcRun's pre-receipt data-safety/source-contract boundary. Such sources are closed, not waiting for human clarification.

## Current source registry decision

| Source | Category | Status | Role / decision |
| --- | --- | --- | --- |
| TED Search API projected route | A | APPROVED / LIVE | MVP procurement evidence and TED-scoped negative-search coverage |
| OpenCoesione PR FESR Lombardia 2021-2027 operation-list ZIP/CSV | A | APPROVED / IMPLEMENTED / LIVE-ACCEPTED | Funded-project source; exact frozen route/schema |
| OpenCoesione all-program 2021-2027 ZIP | A source family | NOT ACTIVATED | Official same-family complete list, but bounded header-only CI probe could not qualify the frozen runtime header without proceeding to the response rows. Fail-closed; existing clean-runner HTTP 403 evidence remains unresolved. |
| OpenCoesione PR FESR FSE+ Puglia 2021-2027 ZIP | A source family | NOT ACTIVATED | Rechecked against the correct `opencoesione.gov.it` route. Bounded header-only CI probe failed before the frozen header could be qualified, so no rows were received and the route remains non-live. |
| Broader OpenCoesione API / Projects / Soggetti routes | B for ProcRun transport | BLOCKED | Not covered by bounded operation-list approval |
| PRR Projects on dados.gov.pt | B | PERMANENTLY BLOCKED | Does not satisfy required safety contract |
| Mais Transparência project surfaces | B | PERMANENTLY BLOCKED | Human-authored project/beneficiary surface |
| PT2030 operations bulk workbook | B | PERMANENTLY BLOCKED | Broad identity-bearing transport; no download-then-filter |
| Portal BASE / APIBase2 current route | B | PERMANENTLY BLOCKED | Broad identity-bearing response; no approved projection |
| Poland public EU-funds project surfaces reviewed | B | REJECTED | No exact safe machine route established from public documentation |

## OpenCoesione production acceptance

Canonical qualification record: `docs/OPENCOESIONE_A1_QUALIFICATION.md`.

The collector validates the exact approved publication schema and route, fails the batch on contract/schema violation, and maps only admitted non-person fields into `FundingProject`. Source-only beneficiary identity fields never enter the canonical/customer-safe object.

The dedicated production runtime has successfully transferred and processed the live Lombardia source. Accepted production evidence: 4,631 funded projects; complete Italy TED universe of 176,540 notices across 708 pages; 81 projects with components; 37 useful/resolved and 44 safely unresolved; customer-safe JSONL and PostgreSQL run manifest.

### 2026-09-05 Italy coverage-expansion probe

OpenCoesione publicly describes the 2021-2027 publication family as covering all national and regional programmes. That source-family approval is broader than the currently activated production route, but it does not by itself authorize a runtime transport that has not passed the frozen technical contract.

PR #55 tested the official all-program ZIP and the official Puglia programme ZIP using a fail-closed HTTP Range probe. The probe requests only bytes 0-262143, refuses to read the body unless the server returns HTTP 206 for that exact bounded range, and decompresses only far enough to reach the CSV header line. It never parses or emits a data row.

Both routes failed this bounded pre-row qualification. Therefore neither route is claimed to have a matching schema, neither was downloaded for row inspection, and neither is activated. This is a transport/header-evidence failure, **not** evidence that either source has a different schema.

Exact live OpenCoesione production coverage remains **PR FESR Lombardia 2021-2027 only**. Customer-facing text must not describe ProcRun's funded-project coverage as all of Italy.

INTERREG files were not assessed in this round.

## TED production contract and MVP OPEN

TED Search API remains approved with server-side field projection, bounded pagination and schema validation.

For the MVP, `OPEN` means exactly:

> **No relevant procurement found in TED as of DATE.**

It does not mean that no procurement exists outside TED. `procrun.coverage` exposes only TED coverage for MVP OPEN and rejects broader scopes.

## Zero-PII rule

> **Do not receive a broad response containing prohibited fields and discard them afterwards.**

No natural-person data may enter the intelligence plane. Account/billing/support PII belongs to the separate customer control plane built during the web phase.
