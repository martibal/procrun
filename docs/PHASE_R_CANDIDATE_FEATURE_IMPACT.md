# Phase R — candidate structural-feature impact gate

Status: **DIAGNOSTIC ONLY**

Reviewed: 2026-09-12

## Purpose

The candidate CPV specificity gate showed that the qualified digital and waste/circular CPV unions each cover roughly 5–6% of the Italy TED universe. CPV is therefore usable only as a non-decisive structural feature.

This gate measures what would happen under the existing conservative matching contract if the two candidate project cohorts were combined with those CPV families and the already-qualified structured TED fields.

## Frozen candidate cohorts

- `digital_transformation`: intervention `013` + action `1.2.3` = 573 projects;
- `waste_circular_economy`: intervention `067` + action `2.6.2` = 142 projects.

The frozen OpenCoesione source must reproduce exactly:

- project count: `4,305`;
- SHA-256: `35dc073ec9e5e06201080bc949a9da19dfd3366deee3524417491e2b2fd21c6a`.

## TED inputs

For each candidate domain, the diagnostic collects only notices inside the already-qualified candidate CPV union and requests only:

- `publication-number`;
- `publication-date`;
- `classification-cpv`;
- `eu-funds-identifier`;
- `place-of-performance-subdiv-proc`.

TED may inject `links`; it is accepted as non-PII transport metadata and never persisted.

The diagnostic does not request title, scope description, buyer identity, contact information, value, address or municipality.

## Measurements

For each candidate domain the aggregate artifact measures:

1. number of candidate projects;
2. size of the matching candidate-CPV TED universe;
3. projects with an exact CUP match in TED `eu-funds-identifier`;
4. projects with at least one compatible NUTS + candidate-CPV notice;
5. projects with either exact project reference or geography + candidate CPV;
6. projects with such a structural candidate inside the project's published execution window.

No CUP, notice identifier or row-level result is emitted in the artifact.

## Why this matters

The frozen matching contract protects OPEN asymmetrically. An exact project reference is sufficient to create a plausible candidate requiring review. Without an exact identifier, CPV/category plus geography can also block OPEN even when exact source wording is unavailable. Such candidates route to UNRESOLVED; they do not manufacture CLOSED.

A candidate taxonomy is therefore not commercially useful merely because 715 projects can be assigned a structured domain. If the broad candidate rules cause most projects to acquire generic geography + CPV candidates, the practical result could be a large increase in UNRESOLVED rather than useful classification.

## Decision rule

- A meaningful exact-reference rate is strong evidence that the candidate domain can be advanced toward deterministic project-to-procurement matching.
- A high geography + CPV rate combined with a low exact-reference rate is a warning that the candidate domain would mostly create unresolved candidates under current matching semantics.
- No candidate domain enters production from this gate.
- No OPEN/CLOSED/UNRESOLVED rule changes from this gate.
- If the candidate feature set is too broad, the next action is to narrow structural evidence, not to weaken the matching contract.
