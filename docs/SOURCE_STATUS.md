# ProcRun source status

Status date: 2026-09-06
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

| Source | Category | Status | Verification date | Schema evidence | Role / decision |
| --- | --- | --- | --- | --- | --- |
| TED Search API projected route | A | APPROVED / LIVE | 2026-09-05 | TED projected contract | MVP procurement evidence and TED-scoped negative-search coverage |
| OpenCoesione PR FESR Lombardia 2021-2027 operation-list ZIP/CSV | A | APPROVED / IMPLEMENTED / LIVE-ACCEPTED | 2026-09-04 | live 20-column transport header | Funded-project source; exact frozen route/schema |
| OpenCoesione all-program 2021-2027 ZIP | A source family | NOT ACTIVATED | 2026-09-05 | `https://opencoesione.gov.it/media/opendata/metadati_beneficiari.xls` | Official metadata is 38,400 bytes / 37.5 KiB but does not equal ProcRun's frozen 20-column transport contract; six exact runtime headers are absent or named differently. Previous bounded header probe also failed. |
| OpenCoesione PR FESR FSE+ Puglia 2021-2027 ZIP | A source family | NOT ACTIVATED | 2026-09-05 | `https://opencoesione.gov.it/media/opendata/metadati_beneficiari.xls` | Same official beneficiary metadata contract; not exact-equal to frozen 20-column runtime header. No data rows retrieved for this qualification. |
| OpenCoesione PR FESR Campania 2021-2027 ZIP | A source family | NOT ACTIVATED | 2026-09-05 | `https://opencoesione.gov.it/media/opendata/metadati_beneficiari.xls` | Same official beneficiary metadata contract; not exact-equal to frozen 20-column runtime header. No data rows retrieved. |
| OpenCoesione PR FESR Lazio 2021-2027 ZIP | A source family | NOT ACTIVATED | 2026-09-05 | `https://opencoesione.gov.it/media/opendata/metadati_beneficiari.xls` | Same official beneficiary metadata contract; not exact-equal to frozen 20-column runtime header. No data rows retrieved. |
| OpenCoesione PR FESR Emilia-Romagna 2021-2027 ZIP | A source family | NOT ACTIVATED | 2026-09-05 | `https://opencoesione.gov.it/media/opendata/metadati_beneficiari.xls` | Same official beneficiary metadata contract; not exact-equal to frozen 20-column runtime header. No data rows retrieved. |
| OpenCoesione PR FESR Liguria 2021-2027 ZIP | A source family | NOT ACTIVATED | 2026-09-05 | `https://opencoesione.gov.it/media/opendata/metadati_beneficiari.xls` | Same official beneficiary metadata contract; not exact-equal to frozen 20-column runtime header. No data rows retrieved. |
| OpenCoesione PR FESR Veneto 2021-2027 ZIP | A source family | NOT ACTIVATED | 2026-09-05 | `https://opencoesione.gov.it/media/opendata/metadati_beneficiari.xls` | Same official beneficiary metadata contract; not exact-equal to frozen 20-column runtime header. No data rows retrieved. |
| Broader OpenCoesione API / Projects / Soggetti routes | B for ProcRun transport | BLOCKED | 2026-09-05 | n/a | Not covered by bounded operation-list approval |
| PRR Projects on dados.gov.pt | B | PERMANENTLY BLOCKED | 2026-09-05 | n/a | Does not satisfy required safety contract |
| Mais Transparência project surfaces | B | PERMANENTLY BLOCKED | 2026-09-05 | n/a | Human-authored project/beneficiary surface |
| PT2030 operations bulk workbook | B | PERMANENTLY BLOCKED | 2026-09-05 | n/a | Broad identity-bearing transport; no download-then-filter |
| Portal BASE / APIBase2 current route | B | PERMANENTLY BLOCKED | 2026-09-05 | n/a | Broad identity-bearing response; no approved projection |
| Poland public EU-funds project surfaces reviewed | B | REJECTED | 2026-09-05 | n/a | No exact safe machine route established from public documentation |

## OpenCoesione production acceptance

Canonical qualification record: `docs/OPENCOESIONE_A1_QUALIFICATION.md`.

The collector validates the exact approved publication schema and route, fails the batch on contract/schema violation, and maps only admitted non-person fields into `FundingProject`. Source-only beneficiary identity fields never enter the canonical/customer-safe object.

The dedicated production runtime has successfully transferred and processed the live Lombardia source. Accepted production evidence: 4,631 funded projects; complete Italy TED universe of 176,540 notices across 708 pages; 81 projects with components; 37 useful/resolved and 44 safely unresolved; customer-safe JSONL and PostgreSQL run manifest.

### 2026-09-05 full-family schema-document qualification

OpenCoesione's central 2021-2027 beneficiary/operation page links the public schema workbook `metadati_beneficiari.xls`. The workbook downloaded by the schema-only CI qualifier is exactly 38,400 bytes (37.5 KiB), matching the repeated 37.5 KB signal that motivated this check.

That signal does **not** prove equality with ProcRun's live transport contract. The workbook contains the 17-field regulatory/metadata model, while the live Lombardia CSV frozen in `src/procrun/collectors/opencoesione.py` has 20 ordered transport columns. Exact comparison found these frozen runtime headers absent under their exact names in the workbook:

- `CostoTotale_TotalCost`
- `Ciclo_Period`
- `ObiettivoSpecifico_SpecificObjective`
- `DataInizioOperazione_OperationStartDate` (workbook uses `DataInizioProgetto_OperationStartDate`)
- `DataFineOperazione_OperationEndDate` (workbook uses `DataFineProgetto_OperationEndDate`)
- `Paese_Country` (workbook uses `StatoMembro_Country`)

Therefore the all-program file and the six prioritised regional routes do not satisfy the instruction's exact field-name/order/count criterion from schema documentation alone. They remain non-live. This is a **schema-document-to-runtime-contract mismatch**, not evidence that their underlying CSV files necessarily differ from Lombardia.

No candidate data ZIP was downloaded to resolve the mismatch, because ProcRun's permanent pre-receipt boundary forbids using row-bearing data as the discovery mechanism for an unqualified route. No new `require_live_source()` entry was added, so the instruction to run a full regression after each newly activated source was not triggered.

Exact live OpenCoesione production coverage remains **PR FESR Lombardia 2021-2027 only**. Customer-facing text must not describe ProcRun's funded-project coverage as all of Italy or as multi-region coverage.

INTERREG and lower-priority regional/national candidates were not promoted in this round because the higher-priority candidates already failed the mandatory exact schema-document gate.

## TED production contract and MVP OPEN

TED Search API remains approved with server-side field projection, bounded pagination and schema validation.

For the MVP, `OPEN` means exactly:

> **No relevant procurement found in TED as of DATE.**

It does not mean that no procurement exists outside TED. `procrun.coverage` exposes only TED coverage for MVP OPEN and rejects broader scopes.

## Zero-PII rule

> **Do not receive a broad response containing prohibited fields and discard them afterwards.**

No natural-person data may enter the intelligence plane. Account/billing/support PII belongs to the separate customer control plane built during the web phase.

## 2026-09-06 source-boundary incident

Status: **REMEDIATION IN PROGRESS — CUSTOMER-FACING UNIONCAMERE USE REMOVED**

During investigation of whether the approved PR FESR Lombardia source could support more precise project geography, an ad hoc diagnostic script downloaded the approved OpenCoesione Lombardia ZIP and printed all non-empty fields for one identified operation row to an interactive production-server terminal. This included the source-only field `NomeBeneficiario_BeneficiaryName`.

This diagnostic practice was outside the intended source-safety discipline. The approved runtime contract itself was not changed: beneficiary identity remains source-only and is not mapped into `FundingProject` or the customer-safe read model. Future diagnostics must not print complete row contents. Schema exploration must use public schema documentation, and any row-level diagnostic that is already within an approved route must use an explicit allowlist of admitted non-identity fields.

The same investigation then introduced `Milano province` into the web branch using a separate Unioncamere Lombardia funding-decision PDF. **Unioncamere is not an approved ProcRun source.** It entered customer-facing code without RIGHTS / ACCESS / DATA SAFETY qualification and therefore violated the source-gate rule. The Unioncamere-derived location and source reference have been removed. Any future consideration of Unioncamere requires a full source qualification from the beginning; prior temporary use creates no presumption of approval.

`CodicePostale_Postcode` is one of the approved 20 OpenCoesione Lombardia transport columns and is not source-only. However, the observed value in the inspected operation was not a normal five-digit Italian CAP. Its semantics remain unresolved. ProcRun must not derive or expose more precise customer geography from that field until official schema documentation establishes its format and an explicit customer-safe mapping is approved. Customer-facing geography therefore remains `Lombardia, Italy`.

Persistence of the terminal output has not yet been established. No assumption is made that stdout was or was not retained by shell/session/audit logging. Before any deletion or cleanup, the production host's relevant shell/session/audit logging must be checked and the result added to this incident record. Logs must not be deleted blindly before that verification.

### Closure criteria

The incident may be marked closed only when:

1. no customer-facing Unioncamere-derived field or source reference remains;
2. production-host shell/session/audit logging has been checked and the persistence result recorded;
3. `CodicePostale_Postcode` remains unused for precise geography unless its official documented semantics and approved mapping are established;
4. future diagnostic practice is constrained to schema-level inspection and explicit admitted-field allowlists.
