# Phase R — Regione Lombardia Socrata structured-classification gate

Status: **STAGE 1 PASS — STAGE 2 PROJECTION CONTROL AUTHORIZED**

Reviewed: 2026-09-12

## Purpose

The Phase R coverage diagnostic established that the currently admitted OpenCoesione publication fields cannot materially close the structured-signal gap. The candidate is the official Regione Lombardia Socrata dataset `q78n-g3m9`, **Beneficiari e operazioni finanziate dal PR FESR Lombardia 2021-2027**.

The dataset is materially relevant because its published schema includes the project join key `CUP` plus structured programme fields and an explicit intervention-type code. The same dataset also includes beneficiary identity fields, which ProcRun must never receive.

This gate asks one narrow question:

> Can ProcRun use the Socrata API to request only a frozen safe classification allowlist, server-side, before receipt?

## Public evidence already established

The official Regione Lombardia dataset page identifies dataset `q78n-g3m9`. The Socrata SODA/SoQL documentation explicitly documents server-side `SELECT` / `$select`, including selecting only a specified subset of columns. Every Socrata dataset exposes a SODA API endpoint.

These facts make this route structurally different from the blocked OpenCoesione API route: a documented pre-receipt output projection mechanism exists in the platform contract.

## Permanent constraints

No human or source-owner contact is permitted. No registration-dependent workflow is allowed. Download-then-filter is prohibited.

No project title, project description, beneficiary field, organisation field, person field, address, contact field or uncontrolled free text is admitted by this gate.

## Stage 1 result — dataset metadata only

Workflow `lombardia-socrata-metadata`, run `34694340540`, requested only:

`https://www.dati.lombardia.it/api/views/q78n-g3m9`

It received HTTP 200 public view metadata and **no dataset rows**.

Artifact: `lombardia-socrata-metadata`  
Artifact ID: `10297528880`  
Artifact digest: `sha256:8fc604e8d754f8356b8af904fb5969eb68fd35cb6b89b9c8beac764d338e6cba`

The artifact recorded:

- `view_metadata_only = true`;
- `row_endpoint_requested = false`;
- `project_rows_requested = false`;
- `beneficiary_values_requested = false`;
- `exports_requested = false`;
- `odata_rows_requested = false`;
- `stage1_result = PASS_METADATA`.

The metadata confirmed the deterministic join key and all initially frozen safe fields. It also exposed two additional structured classification fields:

- `codice_tipologia_intervento` — `CODICE_TIPOLOGIA_INTERVENTO`;
- `descrizione_tipologia` — `DESCRIZIONE_TIPOLOGIA_INTERVENTO`.

These are source-defined intervention taxonomy fields rather than project narrative. They are therefore admitted into the Stage 2 safe allowlist before the first row-level request.

The same metadata explicitly confirmed the presence of forbidden source fields including:

- `nome_del_beneficiario`;
- `codice_del_beneficiario`;
- `indirizzo`;
- project narrative fields such as `operazione_finanziata` and `descrizione_operazione`.

Their presence is why server-side projection is mandatory.

## Frozen Stage 2 safe row allowlist

The one permitted Stage 2 control request may select only:

- `cup`;
- `priorita`;
- `obiettivo_specifico`;
- `azione`;
- `codice_bando`;
- `codice_operazione`;
- `codice_tipologia_intervento`;
- `descrizione_tipologia`.

No other source field is permitted in the response.

## Stage 2 control contract

Stage 2 may make exactly one bounded SODA request against dataset `q78n-g3m9` using server-side `$select` and `$limit=1`.

The request must fail closed unless all of the following hold:

1. HTTP access succeeds anonymously;
2. at most one row is returned;
3. every response key belongs to the frozen safe allowlist;
4. no forbidden or unexpected key is received;
5. the response contains `cup` and at least one structured classification field;
6. the artifact stores only the already-approved safe projected values plus contract diagnostics.

A failure must not trigger a broader request, `SELECT *`, export, OData fallback or schema discovery through row data.

## Decision rule

1. Stage 1 is **PASS**.
2. A Stage 2 pass authorizes only the next aggregate overlap/coverage diagnostic against the frozen 4,305-project corpus; it does not by itself authorize production classification changes.
3. Any projection drift, extra field, access requirement or schema ambiguity closes the route fail-closed.
4. If Stage 2 passes, measure deterministic CUP overlap and incremental structured coverage before changing production semantics.

The Phase R 40% target remains unchanged and must not weaken the privacy or evidence contract.
