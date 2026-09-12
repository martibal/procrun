# Phase R — Kohesio / EU Knowledge Graph structured-classification gate

Status: **QUALIFICATION IN PROGRESS — METADATA ONLY**

Reviewed: 2026-09-12

## Purpose

The frozen Phase R coverage diagnostic established that the currently admitted OpenCoesione fields cannot materially close the structured-signal gap. The next candidate is Kohesio / EU Knowledge Graph, but only for controlled structured classification metadata such as category/field of intervention, sector or equivalent project classification.

This is distinct from the previously blocked use of Kohesio free-text summary data. No summary, project row, beneficiary value or item entity is approved by this gate.

## Permanent constraints

No human or source-owner contact is permitted. Download-then-filter processing is prohibited. ProcRun must prove RIGHTS, ACCESS and DATA SAFETY before receiving row-level candidate data.

## Stage 1 — property metadata only

The first qualification action is restricted to the public Wikibase property API and `wbsearchentities` with `type=property`.

Allowed search concepts are frozen to:

- category of intervention;
- intervention category;
- intervention field;
- field of intervention;
- category intervention;
- project category;
- project sector;
- project subsector.

The probe must not request:

- Q/item entities;
- project rows;
- SPARQL result rows;
- beneficiary or organisation values;
- project summaries or other free text.

The emitted artifact may contain property IDs, labels and descriptions only.

## Decision rule

1. If no explicit structured classification property is found, close Kohesio for this Phase R route and move to the next candidate.
2. If a plausible explicit property is found, do **not** approve production ingestion yet. First verify RIGHTS and anonymous machine ACCESS from already-public documentation.
3. Only after those gates pass may a second, separately preregistered control projection be considered. That projection must request an exact project identifier plus the single approved structured property and must exclude beneficiary, organisation, contact and free-text properties before receipt.
4. Any inability to prove server-side projection or output safety closes the route. No broad item/property walk is permitted as fallback.

The Phase R 40% coverage target remains unchanged; source qualification must not weaken the evidence or privacy contract to reach it.
