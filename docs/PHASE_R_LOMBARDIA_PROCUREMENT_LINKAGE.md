# Phase R — Lombardia direct procurement linkage

Status: **DIAGNOSTIC ONLY — PRODUCTION USE NOT YET APPROVED**

## Product question

The current Phase R baseline classifies only 133 of 4,305 frozen Lombardia projects from approved
structured project metadata. A €149/month product cannot rely on that coverage alone.

This diagnostic tests a materially different value proposition: direct linkage between a funded
project and observable procurement activity using the public project identifier `CUP`.

Regione Lombardia publishes the `ESITI DI GARA OSSERVATORIO REGIONALE` dataset through Socrata. The
catalogue documents `CUP`, `CODICE_CPV`, procurement status/type and other procurement metadata. The
dataset also contains personal-data-bearing fields, so ProcRun must never receive an unrestricted row.

## Frozen safety projection

The diagnostic requests only these fields server-side:

- `numero_esito`
- `numero_bando`
- `provincia`
- `comune`
- `tipologia_appalto`
- `stato_bando`
- `settore`
- `codice_cpv`
- `numero_lotti`
- `n_lotto`
- `cup`

It does **not** request contracting-officer identity, fiscal identifiers, awardee/participant identity,
or procurement free text. Any response field outside the frozen allowlist fails the run.

This diagnostic does not alter the existing A21a free-text decision. Regione Lombardia project free
text remains blocked for verbatim-evidence ingestion under the absolute zero-PII contract.

## Measurement

On the exact frozen 4,305-project OpenCoesione corpus, measure:

1. funded projects carrying a CUP;
2. funded CUPs directly present in the regional procurement-outcome dataset;
3. how many baseline-unresolved projects gain direct procurement linkage;
4. how many linked projects carry CPV classification;
5. procurement-row multiplicity and observable status values.

Only aggregate results are emitted as the workflow artifact. No row-level procurement data is
persisted by the diagnostic.

## Decision rule

This route is worth further qualification only if direct CUP linkage creates a material customer-value
uplift over the current 133-project structured-classification ceiling. A successful measurement would
not automatically convert a whole project to `CLOSED`: one project can contain multiple procurement
needs. The defensible fact would instead be that procurement activity is directly observed for the
same funded project, with CPV/status metadata where available.

If overlap is weak, reject the route and continue the source/value search. If overlap is strong, the
next step is a dedicated RIGHTS / ACCESS / DATA SAFETY production-source qualification followed by a
customer model for project-to-procurement lifecycle facts and change alerts.
