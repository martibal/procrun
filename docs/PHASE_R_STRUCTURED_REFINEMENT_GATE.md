# Phase R — structured refinement gate

Status: **COMPLETE — PROCEED TO PUBLIC ACTION/CALL DEFINITION QUALIFICATION**

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

The diagnostic emits aggregate counts only and measures, for each observed intervention code:

1. project count;
2. distinct `azione` values and their counts;
3. distinct `codice_bando` values and their counts;
4. whether one broad intervention code is concentrated in a small number of stable action/call identifiers or remains structurally broad;
5. the maximum project population that could be reviewed through deterministic structured combinations without using free text.

No CUP list or project-level artifact is emitted.

## Frozen result

Workflow: `lombardia-socrata-coverage` run #3.

Artifact: `lombardia-socrata-structured-coverage`, SHA-256 `a3025c6fa71d9e8c3b0dd680690a1cee6457dd33c993897db937ececf17a7a94`.

The high-volume broad intervention codes do refine into a small number of stable structured groups:

- `013`: 573 projects -> action `1.2.3` only -> one observed call code;
- `010`: 277 projects -> action `1.1.4` only -> one observed call code;
- `012`: 65 projects -> action `1.1.3` only -> one observed call code;
- `023`: 560 projects -> action `1.4.1` only -> three observed call codes;
- `021`: 2,293 projects -> actions `1.3.1`, `1.3.2`, `1.3.3` -> nine observed call codes;
- `067`: 142 projects -> action `2.6.2` only -> two observed call codes.

This is a positive structural-refinement result: the broad intervention layer does not remain irreducibly broad. The already-approved `azione` and `codice_bando` fields provide deterministic cohort identifiers worth qualifying further.

## Public-definition spot check

Public Regione Lombardia / PR FESR material confirms that the action identifiers themselves have explicit programme definitions. Examples include:

- `1.2.3`: support for accelerating the digital transformation of SME business models;
- `1.3.1`: support for internationalisation of Lombardy SMEs and attraction of foreign investment;
- `1.3.3`: support for SME investment;
- `1.4.1`: support for skills development for industrial transition and enterprise sustainability;
- `2.6.2`: circular-economy measures including waste prevention, recycling and material recovery.

These definitions are still programme/action scopes, not automatically procurement components. They therefore justify a dedicated definition-qualification gate, not immediate production mapping.

## Decision

**GO to the next diagnostic gate: public action/call definition qualification.**

The next gate must:

1. use only public official programme/action/call metadata or documentation;
2. avoid beneficiary lists, application lists, award lists, contact/person fields and uncontrolled project rows;
3. determine whether each high-volume action/call identifier defines a procurement-relevant scope narrowly enough to support deterministic component rules;
4. measure potential coverage uplift before any `ComponentDomain`, phrase rule, CPV rule or production mapping is changed;
5. keep broad grant/support actions unmapped if their official scope does not imply a stable procurement component family.

No production mapping, `ComponentDomain`, phrase rule, CPV rule, OPEN/CLOSED state or customer output changes in this gate.

The Phase R 40% target remains a commercial/coverage gate; it does not override evidence, privacy or no-contact constraints.
