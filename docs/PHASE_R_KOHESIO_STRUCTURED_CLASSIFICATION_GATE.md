# Phase R — Kohesio / EU Knowledge Graph structured-classification gate

Status: **BLOCKED — AUTOMATED PROPERTY-METADATA ACCESS NOT AVAILABLE FROM QUALIFICATION RUNNER**

Reviewed: 2026-09-12

## Purpose

The frozen Phase R coverage diagnostic established that the currently admitted OpenCoesione fields cannot materially close the structured-signal gap. Kohesio / EU Knowledge Graph was therefore evaluated as the next candidate, limited strictly to controlled structured classification metadata such as category/field of intervention, sector or equivalent project classification.

This is distinct from the previously blocked use of Kohesio free-text summary data. No summary, project row, beneficiary value or item entity was requested by this gate.

## Permanent constraints

No human or source-owner contact is permitted. Download-then-filter processing is prohibited. ProcRun must prove RIGHTS, ACCESS and DATA SAFETY before receiving row-level candidate data.

## Stage 1 — property metadata only

The qualification action was restricted to the public Wikibase property API and `wbsearchentities` with `type=property`.

Frozen search concepts:

- category of intervention;
- intervention category;
- intervention field;
- field of intervention;
- category intervention;
- project category;
- project sector;
- project subsector.

The probe prohibited Q/item entities, project rows, SPARQL result rows, beneficiary or organisation values, project summaries and other free text.

## Observed access result

Two bounded attempts were made from GitHub-hosted qualification runners.

1. Initial property-only GET request returned HTTP 403 before any property payload was received.
2. A second run retried the same read-only Wikibase action as form-encoded POST, using the same frozen `type=property` parameters. Both GET and POST returned HTTP 403 before any property payload was received.

No project/item query, SPARQL query, broad property walk or row-level fallback was attempted.

The diagnostic workflow now records this condition as `BLOCKED_AUTOMATED_METADATA_ACCESS` while preserving the zero-row safety boundary.

## Gate assessment

| Gate | Result | Reason |
|---|---|---|
| Candidate semantic relevance | PLAUSIBLE | Kohesio's structured project model is relevant to intervention/category classification. |
| Automated metadata ACCESS | **FAIL / NOT AVAILABLE ON QUALIFICATION ROUTE** | Public Wikibase property requests returned HTTP 403 for both GET and POST from the automated qualification runner. |
| Exact structured property | NOT ESTABLISHED | No property payload was received, so ProcRun will not guess a property ID. |
| DATA SAFETY | PASS FOR QUALIFICATION ONLY | No project, beneficiary, organisation, contact or free-text row data was received. |
| Production row ingest | **NOT APPROVED** | RIGHTS, ACCESS and exact pre-receipt projection are not all proven. |

## Decision

`KOHESIO_STRUCTURED_CLASSIFICATION = BLOCKED_AUTOMATED_METADATA_ACCESS`

ProcRun will not attempt project-row access or use a broad item/property walk to work around the access failure. It will not contact the source owner. The route may be reconsidered only if already-public machine access changes sufficiently to allow the frozen metadata-only qualification to succeed without weakening the safety boundary.

Phase R therefore moves to the next different already-public structured-source candidate. The 40% coverage target remains unchanged and must not be reached by relaxing evidence or privacy constraints.
