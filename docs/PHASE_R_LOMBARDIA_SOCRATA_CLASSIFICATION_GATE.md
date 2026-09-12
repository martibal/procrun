# Phase R — Regione Lombardia Socrata structured-classification gate

Status: **STAGE 2 PASS — AGGREGATE CUP/COVERAGE MEASUREMENT AUTHORIZED**

Reviewed: 2026-09-12

## Purpose

The Phase R coverage diagnostic established that the currently admitted OpenCoesione publication fields cannot materially close the structured-signal gap. The candidate is the official Regione Lombardia Socrata dataset `q78n-g3m9`, **Beneficiari e operazioni finanziate dal PR FESR Lombardia 2021-2027**.

The dataset is materially relevant because its published schema includes the project join key `CUP` plus structured programme fields and an explicit intervention-type code. The same dataset also includes beneficiary identity fields, which ProcRun must never receive.

This gate asks one narrow question:

> Can ProcRun use the Socrata API to request only a frozen safe classification allowlist, server-side, before receipt?

## Public evidence established

The official Regione Lombardia dataset page identifies dataset `q78n-g3m9`. The Socrata SODA/SoQL documentation explicitly documents server-side `SELECT` / `$select`, including selecting only a specified subset of columns. Every Socrata dataset exposes a SODA API endpoint.

These facts make this route structurally different from the blocked OpenCoesione API route: a documented pre-receipt output projection mechanism exists in the platform contract.

A prior A21a Lombardia/Socrata probe remains valid and blocked use of the uncontrolled project-description field `descrizione_operazione`. This Phase R route does not reopen that field. It admits only the structured allowlist below.

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

These are source-defined intervention taxonomy fields rather than project narrative and were admitted before the first row-level request.

The same metadata explicitly confirmed forbidden source fields including:

- `nome_del_beneficiario`;
- `codice_del_beneficiario`;
- `indirizzo`;
- project narrative fields such as `operazione_finanziata` and `descrizione_operazione`.

Their presence is why server-side projection is mandatory.

## Frozen safe row allowlist

The only admitted Socrata row fields are:

- `cup`;
- `priorita`;
- `obiettivo_specifico`;
- `azione`;
- `codice_bando`;
- `codice_operazione`;
- `codice_tipologia_intervento`;
- `descrizione_tipologia`.

No other source field is permitted in any response.

## Stage 2 result — one-row projection control

Workflow `lombardia-socrata-projection`, run `34694396394`, made one bounded SODA request with server-side `$select` and `$limit=1`.

Artifact: `lombardia-socrata-projection`  
Artifact ID: `10297808890`  
Artifact digest: `sha256:6aada698ef9071210f6973fffedfcc12e0ce39a4be3fd64645656b18f8f927de`

Observed result:

- HTTP 200;
- exactly 1 row received;
- `server_side_select_used = true`;
- `select_star_used = false`;
- no beneficiary, project narrative or address fields requested;
- response keys were exactly the eight-field safe allowlist;
- `unexpected_keys = []`;
- `stage2_result = PASS_PROJECTION`.

The projected source row included `codice_tipologia_intervento = 21` and the controlled taxonomy label `Sviluppo dell'attività delle PMI e internazionalizzazione, compresi gli investimenti produttivi`, demonstrating that the structured intervention-type field is populated in real data without receiving any forbidden field.

## Stage 3 — aggregate CUP overlap and coverage measurement

Stage 2 authorizes one diagnostic over the frozen Phase R corpus. Stage 3 may:

1. reproduce the exact frozen OpenCoesione source SHA-256 `35dc073ec9e5e06201080bc949a9da19dfd3366deee3524417491e2b2fd21c6a` and 4,305 logical projects;
2. receive Regione Lombardia rows only through the same eight-field server-side `$select` allowlist;
3. join only on exact normalized CUP;
4. emit aggregate counts only — no row-level customer/project artifact;
5. report CUP overlap, intervention-code coverage, conflicts/duplicates and incremental structured-signal ceiling versus the existing 133/4,305 baseline.

If one CUP maps to conflicting structured classifications in the Lombardia source, that CUP must be counted as ambiguous and excluded from safe uplift rather than resolved heuristically.

Stage 3 is measurement only. It must not change `INTERVENTION_FIELD_MAP`, production classification, customer output or source contracts.

## Decision rule

1. Stage 1 is **PASS**.
2. Stage 2 is **PASS**.
3. Stage 3 determines whether the route can materially expand safe structured coverage on the frozen corpus.
4. No production semantics may change until the measured intervention taxonomy has a deterministic mapping review and its isolated uplift is documented.
5. Any projection drift, extra field, source-hash drift or CUP ambiguity fails closed.

The Phase R 40% target remains unchanged and must not weaken the privacy or evidence contract.
