# Phase R — Regione Lombardia Socrata structured-classification gate

Status: **QUALIFICATION IN PROGRESS — METADATA ONLY**

Reviewed: 2026-09-12

## Purpose

The Phase R coverage diagnostic established that the currently admitted OpenCoesione publication fields cannot materially close the structured-signal gap. The next candidate is the official Regione Lombardia Socrata dataset `q78n-g3m9`, **Beneficiari e operazioni finanziate dal PR FESR Lombardia 2021-2027**.

The dataset is materially relevant because its published schema includes the project join key `CUP` plus structured programme fields such as priority, specific objective, action and operation code. The same dataset also includes beneficiary identity fields, which ProcRun must never receive.

This gate therefore asks one narrow question:

> Can ProcRun use the Socrata API to request only a frozen safe classification allowlist, server-side, before receipt?

## Public evidence already established

The official Regione Lombardia dataset page identifies dataset `q78n-g3m9` and documents 23 columns including:

- `cup`;
- `priorita`;
- `obiettivo_specifico`;
- `azione`;
- `codice_bando`;
- `codice_operazione`;
- beneficiary fields including `nome_del_beneficiario` and `codice_del_beneficiario`.

The Socrata SODA/SoQL documentation explicitly documents server-side `SELECT` / `$select`, including selecting only a specified subset of columns. Every Socrata dataset exposes a SODA API endpoint.

These facts make this route structurally different from the blocked OpenCoesione API route: a documented pre-receipt output projection mechanism exists in the platform contract. Dataset-specific metadata and anonymous access must still be reproduced before any row-level request is allowed.

## Permanent constraints

No human or source-owner contact is permitted. No registration-dependent workflow is allowed. Download-then-filter is prohibited.

No row-level request may be made in Stage 1. Metadata may identify column names and types, but must not contain beneficiary values or project rows.

## Stage 1 — dataset metadata only

The first live qualification action may request only the public Socrata view metadata for `q78n-g3m9`.

The probe must verify:

1. anonymous metadata access;
2. dataset identity;
3. presence of the deterministic `cup` join key;
4. presence of the frozen safe classification fields;
5. presence of forbidden beneficiary fields in the source schema, proving why projection is mandatory;
6. absence of any row payload in the qualification artifact.

The probe must not request `/resource/q78n-g3m9.json`, exports, OData rows or any project record.

## Frozen safe row allowlist for a later control request

If Stage 1 passes, a separately preregistered Stage 2 control request may select only:

- `cup`;
- `priorita`;
- `obiettivo_specifico`;
- `azione`;
- `codice_bando`;
- `codice_operazione`.

No project title, project description, beneficiary field, organisation field, person field, address, contact field or uncontrolled free text is admitted by this gate.

## Explicit forbidden fields

At minimum, the following published source columns are forbidden from every ProcRun row response:

- `nome_del_beneficiario`;
- `codice_del_beneficiario`.

Any additional identity-bearing, contact, address or uncontrolled free-text field discovered in metadata must also be excluded before receipt.

## Decision rule

1. If the metadata endpoint is anonymously accessible and confirms the frozen safe and forbidden columns, Stage 1 passes.
2. A Stage 1 pass does **not** authorize production ingestion. It authorizes only one separately preregistered Stage 2 server-side `$select` control request.
3. Stage 2 must prove that the response keys are exactly the safe allowlist and that no forbidden/unexpected field is received.
4. Any projection drift, extra field, access requirement or schema ambiguity closes the route fail-closed.
5. If the route passes Stage 2, measure deterministic CUP overlap with the frozen 4,305-project corpus before changing production classification coverage.

The Phase R 40% target remains unchanged and must not weaken the privacy or evidence contract.
