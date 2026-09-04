# ProcRun source status

Status date: 2026-09-04
Canonical product spec: `docs/PRODUCT_FOUNDATION_FINAL.md`
Authoritative readiness gate: `docs/BUILD_GATES.md` A20

## Production rule

Every live source must be registered in `procrun.source_contracts` and pass `require_live_source()` before retrieval. A source may be approved only from already-public evidence; if human contact would be required to resolve a gate, the source is rejected. No contact-dependent approval path exists.

## Category A/B classification

### Category A — eligible for no-contact qualification

The exact production route is publicly bounded before receipt: structured/codified fields or server-side projection, and any required human-authored text has an authoritative public pre-publication rule excluding natural-person information. Category A eligibility is not automatic approval; rights, access, schema, coverage and safety must still pass.

### Category B — permanently ineligible under current rules

The required response contains human-authored free text or identity-bearing surfaces without a public pre-publication safety guarantee and without a safe server-side projection. Such sources are closed, not waiting. A later public technical-contract change may create a new Category A candidate, but ProcRun never requests that change or assurance.

## Current source registry decision

| Source | Category | Status | Role / decision |
| --- | --- | --- | --- |
| TED Search API projected route | A | APPROVED | MVP procurement evidence, market context and TED-scoped negative-search coverage |
| OpenCoesione PR FESR Lombardia 2021-2027 operation-list ZIP/CSV | A | APPROVED / IMPLEMENTED | Pinned funded-project transfer route; collector is fail-closed, live activation awaits transfer/E2E + green CI |
| Broader OpenCoesione API / Projects / Soggetti routes | B for ProcRun transport | BLOCKED | Not required and not covered by the bounded operation-list approval |
| PRR Projects on dados.gov.pt | B | PERMANENTLY BLOCKED | Required project text lacks the public pre-publication safety contract ProcRun requires |
| Mais Transparência project surfaces | B | PERMANENTLY BLOCKED | Human-authored project/beneficiary surface |
| PT2030 operations bulk workbook | B | PERMANENTLY BLOCKED | Broad identity-bearing transport; no download-then-filter |
| Portal BASE / APIBase2 current route | B | PERMANENTLY BLOCKED | Broad identity-bearing response; no approved projection |
| Poland public EU-funds project surfaces reviewed | B | REJECTED | No exact safe machine route established from public documentation |

## OpenCoesione exact approved route

Canonical qualification record: `docs/OPENCOESIONE_A1_QUALIFICATION.md`.

Public evidence establishes for the 2021-2027 operation-list publication:

- CC BY 4.0 reuse including commercial use with attribution;
- public machine-readable ZIP/CSV publication;
- beneficiary name published only for legal persons for the current 2021-2027 cycle;
- RGS instruction that project title and summary must not contain information attributable to natural persons, including name, tax code, telephone or email;
- a defined regulatory field surface;
- the stated national/regional 2021-2027 EU-cohesion programme universe and bimonthly update cadence.

The RGS privacy instruction is a provider/publication rule, not a database constraint. This residual risk is explicit. ProcRun does not claim leakage is technically impossible; a detected source-contract/schema violation stops the batch.

### Implemented collector boundary

`src/procrun/collectors/opencoesione.py` currently pins the PR FESR Lombardia per-program ZIP/CSV transfer route because the all-program ZIP was not reliably retrievable from clean CI. The collector:

1. requires the approved source contract before network retrieval;
2. pins the approved URL and rejects redirect outside it;
3. requires a ZIP/octet-stream response containing exactly one CSV;
4. validates the exact ordered 17-field header contract before row admission;
5. fails on missing, added, renamed or reordered fields;
6. stages the full batch and returns nothing when any row fails;
7. records observation timestamp, source URL, update date and payload SHA-256;
8. maps only admitted non-person fields into `FundingProject` and never retains beneficiary name/fiscal code.

Remaining activation work is **live source-transfer + canonical end-to-end acceptance + green CI**. Other programme routes require their own transfer acceptance before they can extend coverage.

## TED production contract and MVP OPEN

TED Search API remains approved with server-side field projection, bounded pagination and schema validation.

For the MVP, `OPEN` means exactly:

> **No relevant procurement found in TED as of DATE.**

It does not mean that no procurement exists outside TED. `procrun.coverage` exposes only the TED coverage scope for MVP OPEN and rejects broader scopes.

## Zero-PII rule

> **Do not receive a broad response containing prohibited fields and discard them afterwards.**

No natural-person data may enter the intelligence plane. Account/billing/support PII is a separate control plane.
