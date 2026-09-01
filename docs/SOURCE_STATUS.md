# Phase A/B source status

Status date: 2026-09-01. Terms/compliance re-review due: 2026-11-30.

## Production rule

Production source use is enforced by `procrun.source_contracts`. Every network collector must call `require_live_source()` before retrieval.

A route is usable only when all three gates are approved:

1. **RIGHTS** — commercial reuse/derivative use is approved;
2. **ACCESS** — automated access through the exact route is approved;
3. **DATA SAFETY** — prohibited person/supplier fields can be excluded before receipt.

Anything else fails closed. Public availability is not sufficient.

## Current registry

| Source | Overall | Rights | Access | Data safety | Production implication |
| --- | --- | --- | --- | --- | --- |
| TED Search API | APPROVED | APPROVED | APPROVED | APPROVED | Live collector implemented with frozen server-side projection and schema-drift rejection |
| Portugal 2030 / Mais Transparência project search | CONDITIONAL | CONDITIONAL | CONDITIONAL | CONDITIONAL | Human/reference discovery only; no live production collector |
| Portugal 2030 full project detail | BLOCKED | CONDITIONAL | CONDITIONAL | BLOCKED | Must not be ingested |
| AD&C/dados.gov.pt PT2030 operations bulk file | BLOCKED | CONDITIONAL | APPROVED | BLOCKED | Must not be downloaded and filtered after receipt |
| Portal BASE / IMPIC APIBase2 | BLOCKED | CONDITIONAL | CONDITIONAL | BLOCKED | No production calls |

See `docs/COMPLIANCE.md` for rights/access reasoning and external legal references.

## Portugal 2030 project discovery

The Mais Transparência search surface exposes useful human-visible project cards, but it does not establish a complete, production-approved transport contract. The exact route still lacks all of the following simultaneously:

- source-specific commercial/automated reuse clearance for the chosen transport;
- a response that proves prohibited beneficiary/contact/tax fields cannot enter before validation;
- the required project scope field surface;
- defensible historical `first_seen_at` provenance.

The portal terms are not treated as an open-data licence for automated commercial HTML scraping. Production ingestion should use a separately approved underlying official/open-data route.

The full project-detail page is hard blocked because beneficiary content appears in the same response.

The PT2030 bulk operations resource is also hard blocked by the zero-PII pre-receipt rule. Its dados.gov.pt metadata currently states `Licença não especificada`; ProcRun therefore keeps source-specific rights `CONDITIONAL` even though dados.gov.pt terms state CC BY 4.0 as the default for State datasets unless otherwise specified.

### Portugal production gate

A Portugal 2030 route may change to `APPROVED` only when all of the following are frozen and tested:

1. commercial reuse rights for the exact source/route;
2. automated-access rights/conditions for the exact route;
3. prohibited fields cannot enter the received response;
4. required identity, funding, dates and project-scope fields are available;
5. a defensible `first_seen_at` can be recorded without using project start date as proxy;
6. schema drift is detectable before persistence;
7. retrieval method, allowlist, attribution and terms references are frozen in code/tests.

For newly observed projects, local observation time may serve as first-seen provenance after a safe discovery route is approved. Historical backfills without defensible snapshot dates remain `temporal_provenance=UNRESOLVED` and cannot support historical lead-time claims.

## TED production contract

Official references:

- `https://docs.ted.europa.eu/api/latest/search.html`
- `https://ted.europa.eu/en/legal-notice`
- `https://ted.europa.eu/en/news/fair-usage-policy-on-ted`
- `https://eur-lex.europa.eu/eli/dec/2011/833/oj`

Rights/access conclusion: TED explicitly supports notice reuse for commercial/non-commercial purposes and identifies commercial value-added platforms as Search API users. Technical users are directed to the public API. The published HTTP limit is 700 requests/minute; ProcRun freezes an internal ceiling of 600 and is expected to operate far below it.

Frozen transport:

- endpoint: `POST https://api.ted.europa.eu/v3/notices/search`;
- server-side explicit fields list only;
- pagination: `ITERATION` only for complete walks;
- default page size: 100, hard maximum: 250;
- hard field-cell budget: 10,000 per page;
- completion: empty `notices` page plus count reconciliation;
- timeout, missing continuation token, count mismatch or `max_pages` exhaustion => incomplete coverage and never `OPEN`;
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

TED may attach `links` automatically; it is accepted only as transport metadata and is not copied into the canonical record. Unknown envelope/notice fields fail before normalization.

The field list excludes contact person/email/phone/touchpoint, supplier/winner, street-address and business-identifier fields. `buyer-name` is retained only as contracting-authority organisation name needed for evidence matching.

Customer-facing source surfaces must credit TED/EU, identify ProcRun transformation/classification, avoid implying EU endorsement and avoid distorting source meaning.

## Portal BASE / IMPIC decision

Official references:

- `https://www.base.gov.pt/Base4/pt/o-portal/base/`
- `https://www.base.gov.pt/Base4/pt/documentacao/formas-de-obter-dados-sobre-os-contratos-publicos/`
- `https://www.base.gov.pt/APIBase2`
- `https://www.base.gov.pt/Base4/pt/noticias/2025/api-para-consulta-de-dados-do-portal-base/`

Public BASE data can be automatically extracted, but large-volume API access requires registration and prior IMPIC authorization. Current documentation says API fields are the same as the broad dados.gov files, and the response example includes `adjudicatarios` identifiers/names. No server-side output field projection is documented.

Therefore APIBase2 remains `DATA SAFETY=BLOCKED`. Obtaining an IMPIC token would not change that. Any future route additionally needs the exact IMPIC authorization/commercial terms frozen before activation.

## Review expiry

Approved live-source reviews are deliberately time-bounded. `require_live_source()` rejects an approved source after its review due date until the then-current terms are rechecked and the registry is explicitly renewed.
