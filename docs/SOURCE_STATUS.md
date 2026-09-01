# Phase A/B source status

Status date: 2026-09-01.

## Decision summary

Production source use is enforced in code by `procrun.source_contracts`. A network collector must call `require_live_source()` before retrieval. Anything other than `APPROVED` fails closed.

Current registry:

| Source | Status | Production implication |
| --- | --- | --- |
| TED Search API | APPROVED | Live collector implemented with frozen server-side field projection and schema-drift rejection. |
| Portugal 2030 project search | CONDITIONAL | Do not implement live retrieval yet. |
| Portugal 2030 full project detail | BLOCKED | Must not be ingested. |
| AD&C/dados.gov.pt PT2030 operations bulk file | BLOCKED | Must not be downloaded and filtered after receipt. |
| Portal BASE / IMPIC APIBase2 | BLOCKED | Documented response surface is broader than the MVP allowlist and no output-field projection is documented. |

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

## TED production contract

Official documentation:

- `https://docs.ted.europa.eu/api/latest/search.html`
- `https://docs.ted.europa.eu/ODS/latest/reuse/search-api.html`
- `https://docs.ted.europa.eu/ODS/latest/reuse/field-list.html`

Frozen transport:

- endpoint: `POST https://api.ted.europa.eu/v3/notices/search`;
- pagination: `ITERATION` only for complete walks;
- default page size: 100, hard maximum: 250;
- hard TED field-cell budget: 10,000 per page;
- response completion: an empty `notices` page plus count reconciliation;
- `timedOut != false`, missing continuation token, count mismatch or `max_pages` exhaustion means incomplete coverage and must never support an `OPEN` conclusion;
- raw response bodies and iteration tokens are not persisted by the collector.

Frozen requested fields:

- `publication-number`
- `publication-date`
- `notice-title`
- `description-proc`
- `classification-cpv`
- `contract-nature`
- `procedure-type`
- `estimated-value-proc`
- `estimated-value-cur-proc`
- `result-value-notice`
- `result-value-cur-notice`
- `place-of-performance-city-proc`
- `place-of-performance-subdiv-proc`
- `buyer-name`
- `eu-funds-financing-id-lot`
- `eu-funds-identifier`

TED automatically attaches `links`; this is accepted only as transport metadata and is not copied into the canonical record. Unknown envelope fields or notice fields fail closed before normalization.

The field list deliberately excludes buyer contact person/email/phone/touchpoint fields, supplier/winner fields, street addresses and business identifiers. `buyer-name` is retained only as the contracting-authority organisation name required for evidence matching.

Currency values are mapped into canonical `*_eur` fields only when TED explicitly reports `EUR`. The current canonical ledger stores integer EUR amounts, so fractional values are withheld rather than silently rounded; this can be revisited through an explicit schema migration.

## Portal BASE / IMPIC decision

Official references audited on 2026-09-01:

- `https://www.base.gov.pt/Base4/pt/documentacao/formas-de-obter-dados-sobre-os-contratos-publicos/`
- `https://www.base.gov.pt/APIBase2`

The IMPIC documentation states that API access is token-authorised and daily, but that the fields returned by the API are the same as the files published through dados.gov.pt. The documented API endpoints accept search/filter parameters such as contract ID, procedure ID, announcement number, CPV, year and entity NIF; no server-side output field projection is documented.

The official response example includes `adjudicatarios` entries that combine supplier identifiers with names. Supplier/adjudicatario data and tax identifiers are outside the MVP intelligence allowlist. Because the documented API route cannot be constrained to prevent those fields from entering the response, APIBase2 is **BLOCKED** under the pre-receipt zero-PII rule.

This decision does not claim that every future IMPIC route is unusable. A new, separately documented route may be reconsidered only if it supports a field-bounded response that excludes prohibited fields before receipt. Until then, no BASE collector may be implemented.

## Rule

Public availability is not sufficient. A source is production-safe only when prohibited data cannot enter the intelligence pipeline in the first place.
