# Phase R — OpenCoesione API structured-classification gate

Status: **BLOCKED — NO PROVABLE PRE-RECEIPT PROJECTION**

Reviewed: 2026-09-12

## Purpose

The Phase R coverage diagnostic proved that the currently admitted 2021–2027 publication fields cannot materially close the structured-signal gap. OpenCoesione's public documentation separately describes a REST API and project classification surfaces including synthetic theme and CUP nature/type fields.

This gate asked whether that API could provide a project identifier plus only approved structured classification fields under ProcRun's pre-receipt zero-PII rule.

## Public evidence established

OpenCoesione publicly states that:

- API data are released under CC-BY 4.0;
- anonymous access is available, subject to a published request-rate limit;
- project resources can be filtered by theme, nature or territory;
- project classification metadata include `oc_tema_sintetico`, `qsn_descr_tema_prioritario_ue`, `cup_descr_natura` and `cup_descr_tipologia`.

These statements support RIGHTS and anonymous ACCESS in principle. They do not establish a safe row-level response contract.

## Permanent constraints

No human or source-owner contact is permitted. Registration is neither required nor allowed for this qualification path. Download-then-filter is prohibited.

No project or subject row may be requested until the API itself proves, through already-public metadata or protocol behaviour, a server-side mechanism that restricts the response before receipt to an exact safe allowlist.

## Stage 1 result — API metadata and protocol only

Workflow `opencoesione-api-metadata`, run `34694172937`, requested only API-root/documentation and `OPTIONS`-style protocol metadata. It received no project, project-detail, subject, beneficiary or download rows.

Observed responses:

- `GET https://opencoesione.gov.it/api/` → HTTP 403;
- `GET https://www.opencoesione.gov.it/api/` → HTTP 403;
- `OPTIONS https://opencoesione.gov.it/api/progetti/` → HTTP 403;
- `OPTIONS https://www.opencoesione.gov.it/api/progetti/` → HTTP 308.

No response exposed an `Allow` header or explicit `fields`, `select`, projection, include/exclude or equivalent pre-receipt output-selection mechanism.

Artifact: `opencoesione-api-metadata`  
Artifact ID: `10297448644`  
Artifact digest: `sha256:c51afc828f26929489009c1c9bfe43491116c9470a120cc7f185e02fe3298e1a`

The artifact recorded:

- `project_rows_requested = false`;
- `project_detail_requested = false`;
- `subject_rows_requested = false`;
- `beneficiary_data_requested = false`;
- `free_text_project_data_requested = false`;
- `downloads_requested = false`;
- `qualification_result = BLOCKED_NO_PRE_RECEIPT_PROJECTION`.

## Frozen target allowlist

A future row-level control projection would be eligible only if already-public evidence proves it can request no more than:

- one deterministic project identifier already present in ProcRun;
- `oc_tema_sintetico`;
- `qsn_descr_tema_prioritario_ue`;
- `cup_descr_natura`;
- `cup_descr_tipologia`;
- an exact CUP sector/subsector/category field only if explicitly documented by the API schema.

No identity-bearing or uncontrolled free-text field may be received.

## Gate assessment

| Gate | Result | Reason |
|---|---|---|
| RIGHTS | PASS in principle | OpenCoesione documents CC-BY 4.0 reuse. |
| Anonymous ACCESS | PASS in principle, not reproduced from Actions | Public documentation states anonymous API access, but the bounded hosted-runner probe received 403/308. |
| Structured classification relevance | PASS | Official documentation identifies theme and CUP nature/type classification fields. |
| Server-side field projection | **FAIL / NOT PROVEN** | Metadata/OPTIONS did not expose a provable output-selection mechanism. |
| Zero-PII before receipt | **NOT APPROVED** | No row request is permitted without the projection contract. |
| Human-contact-free closure | PASS | No registration or source-owner contact was attempted. |

## Decision

`OPENCOESIONE_API_CLASSIFICATION = BLOCKED_NO_PRE_RECEIPT_PROJECTION`

Do not infer undocumented query parameters and do not request broad project responses to discover their shape. No project row may be received under this route unless new already-public documentation establishes an explicit server-side output projection that can be frozen and tested fail-closed.

This closes the OpenCoesione API classification candidate under the current evidence. The Phase R 40% target remains unchanged; the next candidate must be a different already-public structured route that preserves the same pre-receipt privacy boundary.
