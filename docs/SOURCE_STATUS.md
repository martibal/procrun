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
| Broader OpenCoesione API / Projects / Soggetti routes | B for ProcRun transport | BLOCKED | Not covered by bounded operation-list approval |
| PRR Projects on dados.gov.pt | B | PERMANENTLY BLOCKED | Does not satisfy required safety contract |
| Mais Transparência project surfaces | B | PERMANENTLY BLOCKED | Human-authored project/beneficiary surface |
| PT2030 operations bulk workbook | B | PERMANENTLY BLOCKED | Broad identity-bearing transport; no download-then-filter |
| Portal BASE / APIBase2 current route | B | PERMANENTLY BLOCKED | Broad identity-bearing response; no approved projection |
| Poland public EU-funds project surfaces reviewed | B | REJECTED | No exact safe machine route established from public documentation |

## OpenCoesione production acceptance

Canonical qualification record: `docs/OPENCOESIONE_A1_QUALIFICATION.md`.

The collector validates the exact approved publication schema and route, fails the batch on contract/schema violation, and maps only admitted non-person fields into `FundingProject`. Source-only beneficiary identity fields never enter the canonical/customer-safe object.

The dedicated production runtime has successfully transferred and processed the live source. Accepted production evidence: 4,631 funded projects; complete Italy TED universe of 176,540 notices across 708 pages; 81 projects with components; 37 useful/resolved and 44 safely unresolved; customer-safe JSONL and PostgreSQL run manifest.

Other OpenCoesione programme routes require their own explicit source/transport acceptance before they can extend coverage.

## TED production contract and MVP OPEN

TED Search API remains approved with server-side field projection, bounded pagination and schema validation.

For the MVP, `OPEN` means exactly:

> **No relevant procurement found in TED as of DATE.**

It does not mean that no procurement exists outside TED. `procrun.coverage` exposes only TED coverage for MVP OPEN and rejects broader scopes.

## Zero-PII rule

> **Do not receive a broad response containing prohibited fields and discard them afterwards.**

No natural-person data may enter the intelligence plane. Account/billing/support PII belongs to the separate customer control plane built during the web phase.
