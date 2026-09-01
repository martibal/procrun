# Phase A source status

Status date: 2026-09-01.

## Decision summary

Production source use is now enforced in code by `procrun.source_contracts`. A network collector must call `require_live_source()` before retrieval. Anything other than `APPROVED` fails closed.

Current registry:

| Source | Status | Production implication |
| --- | --- | --- |
| TED Search API | APPROVED | May be implemented with explicit server-side field projection and schema-drift rejection. |
| Portugal 2030 project search | CONDITIONAL | Do not implement live retrieval yet. |
| Portugal 2030 full project detail | BLOCKED | Must not be ingested. |
| AD&C/dados.gov.pt PT2030 operations bulk file | BLOCKED | Must not be downloaded and filtered after receipt. |
| Portal BASE / IMPIC | CONDITIONAL | Requires exact schema audit before implementation. |

## Portugal 2030 project discovery

The official Mais Transparência project-search surface currently exposes useful project cards including project title, operation code, expected completion date and funding amount. It reports roughly 23,609 funded projects.

Official surface:

`https://transparencia.gov.pt/pt/fundos-europeus/pt2030/beneficiarios-projetos/pesquisar/projeto/`

This is not enough to approve a collector. The rendered/searchable surface does not establish a complete project scope field or defensible historical `first_seen_at`, and transport-level zero-PII safety has not been proven for the exact retrieval route.

### Blocked routes

The full project-detail page contains beneficiary content in the same response and is therefore blocked.

The official PT2030 approved-operations dataset is distributed as a bulk workbook. Government material confirms Mais Transparência is based on AD&C open data from dados.gov.pt, but public availability does not satisfy the product boundary. The broad bulk file may not be downloaded into the intelligence environment and column-filtered afterwards.

## A1/A2 gate

**Portugal 2030 live collector remains blocked pending proof.**

A production route must demonstrate all of the following before its registry status may change to `APPROVED`:

1. prohibited beneficiary/contact/tax-identifier fields cannot enter the response received by the collector;
2. the required project identity, funding, dates and project-scope fields are available through the approved route(s);
3. a defensible `first_seen_at` can be recorded without using project start date as a proxy;
4. schema drift is detectable before persistence;
5. the exact retrieval method and field contract are frozen in tests/documentation.

For newly observed projects, local observation time may later serve as first-seen provenance once a safe discovery transport is approved. Historical backfills without defensible source snapshot dates must remain `temporal_provenance=UNRESOLVED` and cannot support historical lead-time claims.

## TED

TED remains approved in principle because its Search API supports an explicit requested-fields projection. Production implementation must still use the frozen allowlist and reject unexpected fields before normalization or persistence.

## Rule

Public availability is not sufficient. A source is production-safe only when prohibited data cannot enter the intelligence pipeline in the first place.
