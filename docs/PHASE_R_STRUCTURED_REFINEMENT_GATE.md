# Phase R — structured refinement gate

Status: **DIAGNOSTIC ONLY**

Reviewed: 2026-09-12

## Why this gate exists

The qualified Regione Lombardia Socrata route provides a safe structured intervention code for 4,178 of the frozen 4,305 Phase R projects, but the current five-domain ProcRun taxonomy can use only 142 projects (3.2985%). The intervention-code review closed broad codes such as `021`, `013`, `023`, `010` and `067` against the current taxonomy rather than weakening the evidence contract.

A direct taxonomy expansion is not automatically valid. Codes such as SME development, digitalisation, skills and research are programme purposes, not deterministic procurement components. Renaming them as ProcRun domains would increase nominal coverage without proving what is likely to be procured.

Before any taxonomy change, this gate therefore tests whether already-approved structured fields can refine the broad intervention codes deterministically.

## Admitted inputs

Only fields already proven safe by the Lombardia Socrata projection gate may be used:

- `cup`;
- `priorita`;
- `obiettivo_specifico`;
- `azione`;
- `codice_bando`;
- `codice_operazione`;
- `codice_tipologia_intervento`;
- `descrizione_tipologia`.

No beneficiary field, project title, project narrative, organisation field, address, contact field or new source is admitted.

The frozen OpenCoesione corpus must still reproduce exactly:

- project count: `4,305`;
- source SHA-256: `35dc073ec9e5e06201080bc949a9da19dfd3366deee3524417491e2b2fd21c6a`.

## Measurement

The diagnostic must emit aggregate counts only. It must measure, for each observed intervention code:

1. project count;
2. distinct `azione` values and their counts;
3. distinct `codice_bando` values and their counts;
4. whether one broad intervention code is concentrated in a small number of stable action/call identifiers or remains structurally broad;
5. the maximum project population that could be reviewed through deterministic structured combinations without using free text.

No CUP list or project-level artifact may be emitted.

## Decision rule

- If a high-volume broad intervention code splits into a small number of stable `azione` or `codice_bando` groups, the next gate may qualify the **public definitions** of those structured identifiers before any mapping is proposed.
- A combination is not a ProcRun domain merely because it is frequent. Its official definition must identify a procurement-relevant scope narrowly enough to support deterministic component rules.
- If the broad codes remain broad after `azione`/`codice_bando` refinement, taxonomy expansion does not solve the Phase R coverage problem under the current product semantics.
- No production mapping, `ComponentDomain`, phrase rule, CPV rule, OPEN/CLOSED state or customer output changes in this gate.

The Phase R 40% target remains a commercial/coverage gate; it does not override evidence, privacy or no-contact constraints.
