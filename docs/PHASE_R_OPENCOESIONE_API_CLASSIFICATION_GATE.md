# Phase R — OpenCoesione API structured-classification gate

Status: **QUALIFICATION IN PROGRESS — METADATA/OPTIONS ONLY**

Reviewed: 2026-09-12

## Purpose

The Phase R coverage diagnostic proved that the currently admitted 2021–2027 publication fields cannot materially close the structured-signal gap. OpenCoesione's public documentation separately describes a REST API and project classification surfaces including synthetic theme and CUP nature/type fields.

This gate asks whether that API can provide a project identifier plus only approved structured classification fields under ProcRun's pre-receipt zero-PII rule.

## Public evidence already established

OpenCoesione publicly states that:

- API data are released under CC-BY 4.0;
- anonymous access is available, subject to a published request-rate limit;
- project resources can be filtered by theme, nature or territory;
- project classification metadata include `oc_tema_sintetico`, `qsn_descr_tema_prioritario_ue`, `cup_descr_natura` and `cup_descr_tipologia`.

These statements support RIGHTS and anonymous ACCESS in principle. They do not establish a safe row-level response contract.

## Permanent constraints

No human or source-owner contact is permitted. Registration is neither required nor allowed for this qualification path. Download-then-filter is prohibited.

No project or subject row may be requested until the API itself proves, through already-public metadata or protocol behaviour, a server-side mechanism that restricts the response before receipt to an exact safe allowlist.

## Stage 1 — API metadata and protocol only

The first live qualification action may request only:

- the API root or documentation surface;
- HTTP `OPTIONS` or equivalent schema/metadata responses for the project resource;
- response headers and capability metadata.

It must not request:

- project list rows;
- project detail rows;
- subject/beneficiary resources;
- organisation/person/contact fields;
- project free text;
- CSV or database downloads.

The probe may record only status codes, allowed methods and metadata/documentation text needed to establish whether a server-side field projection mechanism exists.

## Frozen target allowlist

A future row-level control projection is eligible only if Stage 1 proves it can request no more than:

- one deterministic project identifier already present in ProcRun;
- `oc_tema_sintetico`;
- `qsn_descr_tema_prioritario_ue`;
- `cup_descr_natura`;
- `cup_descr_tipologia`;
- an exact CUP sector/subsector/category field only if explicitly documented by the API schema.

No identity-bearing or uncontrolled free-text field may be received.

## Decision rule

1. If the API exposes an explicit server-side field projection/select mechanism, freeze its syntax and exact safe allowlist before any row request.
2. If projection is not documented or cannot be proven without receiving a project row, close this route as `BLOCKED_NO_PRE_RECEIPT_PROJECTION`.
3. Do not infer undocumented query parameters and do not test broad project responses to discover their shape.
4. If the route closes, move to the next already-public structured candidate; do not weaken the privacy contract.

The Phase R 40% target remains unchanged.
