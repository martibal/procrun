# Phase A/B source status

Status date: 2026-09-02. Terms/compliance re-review due: 2026-11-30.

## Production rule

Production source use is enforced by `procrun.source_contracts`. Every network collector must call
`require_live_source()` before retrieval.

A route is usable only when all three gates are approved:

1. **RIGHTS** — commercial reuse/derivative use is approved;
2. **ACCESS** — automated access through the exact route is approved;
3. **DATA SAFETY** — prohibited person/supplier fields can be excluded before receipt.

Anything else fails closed. Public availability is not sufficient.

Research candidates that have not established the complete transport, coverage and rights contract are
deliberately kept out of `SOURCE_CONTRACTS`; an unregistered route therefore also fails closed if
production code attempts to use it.

## Current registry

| Source | Overall | Rights | Access | Data safety | Production implication |
| --- | --- | --- | --- | --- | --- |
| TED Search API | APPROVED | APPROVED | APPROVED | APPROVED | Live collector implemented with frozen server-side projection and schema-drift rejection |
| Portugal 2030 / Mais Transparência project search | CONDITIONAL | CONDITIONAL | CONDITIONAL | CONDITIONAL | Human/reference discovery only; no live production collector |
| Portugal 2030 full project detail | BLOCKED | CONDITIONAL | CONDITIONAL | BLOCKED | Must not be ingested |
| AD&C/dados.gov.pt PT2030 operations bulk file | BLOCKED | CONDITIONAL | APPROVED | BLOCKED | Must not be downloaded and filtered after receipt |
| Portal BASE / IMPIC APIBase2 | BLOCKED | CONDITIONAL | CONDITIONAL | BLOCKED | No production calls |

### Research outcomes outside the live registry

| Candidate | Outcome | Rights | Access | Data safety | Result |
| --- | --- | --- | --- | --- | --- |
| European Commission Kohesio / EU Knowledge Graph SPARQL | RETIRED FOR CURRENT PT2030 | UNRESOLVED | VERIFIED FOR NARROW QUERY | VERIFIED FOR FROZEN PROJECTION | Known current operation `PACS-FC-01781200` returned zero rows. Do not broaden the graph query. |
| European Commission Kohesio 2021-2027 country project download | BLOCKED | PROMISING | UNVERIFIED | BLOCKED | Portugal-specific project export can contain beneficiary identifiers; download-then-filter is forbidden. |
| European Commission Kohesio `/projects` REST service | BLOCKED | PROMISING | UNVERIFIED | BLOCKED | Current frontend uses project filters + offset/limit/language but exposes no server-side output-field projection. |
| Mais Transparência project-search-card fallback | RESEARCH ONLY | CONDITIONAL | CONDITIONAL | PROMISING / UNVERIFIED | Card surface appears project-only, but exact-route automation/reuse and title-only scope sufficiency are unresolved. |

The research labels above are documentation labels, not `SourceStatus` enum values. None of these routes
is registered as a live production source.

See:

- `docs/PT2030_DISCOVERY_ROUTE.md`;
- `docs/KOHESIO_2021_DOWNLOAD_FINDINGS.md`;
- `docs/PT2030_NATIONAL_FALLBACK_GATE.md`.

## Portugal 2030 project discovery

No Portugal 2030 project-discovery route is production-approved.

### Mais Transparência project search

The project-search surface exposes useful human-visible cards with project title, operation code,
completion date and financing amount. The observed card surface does not require the full project-detail
response and is materially safer than the detail page.

It remains `CONDITIONAL` because:

- the exact automated/machine-access contract for the presentation-site route is not frozen;
- the presentation-site terms are not treated as an explicit commercial scraping/reuse grant;
- the cards do not expose the project `Sumário` / scope text used by the component engine.

A title-only discovery mode is research-only. It may not infer components beyond exact title spans and
must leave ambiguous scope `UNRESOLVED`. It requires a preregistered PII-safe end-to-end replay before it
can alter the production discovery contract.

### Mais Transparência project detail

The detail page contains the scope text ProcRun needs, but beneficiary content appears in the same HTTP
response. ProcRun's zero-PII boundary is pre-receipt; a broad response may not be downloaded and filtered
afterwards.

Decision: `BLOCKED` for intelligence ingestion.

### AD&C / dados.gov.pt PT2030 operations workbook

The official operations workbook contains useful operation identity/scope fields but also beneficiary
fields and identifiers. The only identified operation-level distribution is broad and does not expose
server-side output-column projection.

Current dados.gov.pt terms provide a stronger general reuse signal than previously recorded: state-body
data is published under CC BY 4.0 by default unless specified otherwise, and open data may be reused
commercially. The PT2030 dataset page itself currently displays `Licença não especificada`, so ProcRun
still treats exact-source rights as `CONDITIONAL` pending a frozen source-specific interpretation.

Regardless of rights, data safety remains `BLOCKED`: ProcRun must not download the workbook and remove
beneficiary columns locally.

## EU Knowledge Graph SPARQL result

ProcRun froze a narrow property allowlist and excluded beneficiary/contact properties, including `P841`.
A local Phase 2 probe queried exactly `PACS-FC-01781200`. The endpoint returned standards-compliant
SPARQL Results XML over GET. ProcRun parsed it with DTD processing prohibited and external entity
resolution disabled, then validated every declared/returned variable against the frozen allowlist.

The response contained zero rows (`coverage_found=false`). The same operation code is current on
Portugal's official PT2030 portal. Therefore this is a real coverage miss for the tested EUKG layer, not
a parser artefact.

Decision: the EUKG route is retired for current PT2030 discovery. Do not broaden the graph query, walk
arbitrary properties, query beneficiary records, use `SELECT *`, `DESCRIBE` or generic `CONSTRUCT`.

## Kohesio 2021-2027 final result

The current Kohesio 2021-2027 layer was investigated without retrieving a project response.

A Portugal-specific project export exists, but the project schema/export can contain beneficiary
identifiers. Country isolation is therefore insufficient for the pre-receipt rule.

Frontend-only probes then established the current project-list service shape:

- route: `api + "/projects"`;
- request parameters: `getProjectsFilters()` plus `offset`, `limit` and `language`;
- country/programming-period and other search filters are supported;
- the complete response object is received before `response.list` is mapped through the project
  deserializer;
- no `fields`, `select`, projection or equivalent output-field parameter was found in the actual
  `getProjects()` request path.

Earlier keyword hits for `fields`, `select` and `projection` were UI, form, Angular or map-projection
code, not response projection controls.

Decision: both the current project download and `/projects` REST path are `DATA SAFETY=BLOCKED` for
ProcRun. No more Kohesio project/data probes are authorised unless the Commission later publishes a
documented field-projection contract or separately field-safe Portugal distribution.

## Portugal production gate

A Portugal 2030 route may change to `APPROVED` only when all of the following are frozen and tested:

1. commercial reuse rights for the exact source/route;
2. automated-access rights/conditions for the exact route;
3. prohibited fields cannot enter the received response;
4. required identity, funding, dates and project-scope fields are available, or a deliberately reduced
   discovery mode has independently passed its preregistered sufficiency gate;
5. a defensible `first_seen_at` can be recorded without using project start date as proxy;
6. schema drift is detectable before persistence;
7. retrieval method, allowlist, attribution and terms references are frozen in code/tests;
8. known PT2030 operation codes resolve across a small frozen cross-programme sample.

For newly observed projects, local observation time may serve as first-seen provenance only after a safe
discovery route is approved. Historical backfills without defensible snapshot dates remain
`temporal_provenance=UNRESOLVED` and cannot support historical lead-time claims.

## TED production contract

Official references:

- `https://docs.ted.europa.eu/api/latest/search.html`
- `https://ted.europa.eu/en/legal-notice`
- `https://ted.europa.eu/en/news/fair-usage-policy-on-ted`
- `https://eur-lex.europa.eu/eli/dec/2011/833/oj`

Rights/access conclusion: TED explicitly supports notice reuse for commercial/non-commercial purposes
and identifies commercial value-added platforms as Search API users. Technical users are directed to
the public API. The published HTTP limit is 700 requests/minute; ProcRun freezes an internal ceiling of
600 and is expected to operate far below it.

Frozen transport:

- endpoint: `POST https://api.ted.europa.eu/v3/notices/search`;
- server-side explicit fields list only;
- pagination: `ITERATION` only for complete walks;
- default page size: 100, hard maximum: 250;
- hard field-cell budget: 10,000 per page;
- completion: empty `notices` page plus count reconciliation;
- timeout, missing continuation token, count mismatch or `max_pages` exhaustion => incomplete coverage
  and never `OPEN`;
- raw response bodies and iteration tokens are not persisted.

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

TED may attach `links` automatically; it is accepted only as transport metadata and is not copied into
the canonical record. Unknown envelope/notice fields fail before normalization.

The field list excludes contact person/email/phone/touchpoint, supplier/winner, street-address and
business-identifier fields. `buyer-name` is retained only as contracting-authority organisation name
needed for evidence matching.

Customer-facing source surfaces must credit TED/EU, identify ProcRun transformation/classification,
avoid implying EU endorsement and avoid distorting source meaning.

## Portal BASE / IMPIC decision

Official references:

- `https://www.base.gov.pt/Base4/pt/o-portal/base/`
- `https://www.base.gov.pt/Base4/pt/documentacao/formas-de-obter-dados-sobre-os-contratos-publicos/`
- `https://www.base.gov.pt/APIBase2`
- `https://www.base.gov.pt/Base4/pt/noticias/2025/api-para-consulta-de-dados-do-portal-base/`

Public BASE data can be automatically extracted, but large-volume API access requires registration and
prior IMPIC authorization. Current documentation says API fields are the same as the broad dados.gov
files, and the response example includes `adjudicatarios` identifiers/names. No server-side output field
projection is documented.

Therefore APIBase2 remains `DATA SAFETY=BLOCKED`. Obtaining an IMPIC token would not change that. Any
future route additionally needs the exact IMPIC authorization/commercial terms frozen before activation.

## Review expiry

Approved live-source reviews are deliberately time-bounded. `require_live_source()` rejects an approved
source after its review due date until the then-current terms are rechecked and the registry is explicitly
renewed.
