# Poland Mapa Dotacji route findings

Status date: 2026-09-03.

This note evaluates Mapa Dotacji UE as the next Poland funded-project discovery candidate after the national SL2021 bulk route and the dane.gov.pl row API. It does not approve a new ProcRun source and does not change the executable source registry.

## Candidate 3 — Mapa Dotacji UE

Official public material describes Mapa Dotacji UE as a government project-search service for EU-funded projects in Poland. The current official CUPT description states that the map contains projects from the 2004-2006, 2007-2013 and 2014-2020 programming periods.

Current Portal Funduszy Europejskich pages for the 2021-2027 national project list link to Mapa Dotacji UE as a related service, but the official material reviewed here does not establish Mapa Dotacji UE itself as a complete current 2021-2027 project source.

ProcRun requires current expansion-market coverage. A related-project service whose authoritative description stops at 2014-2020 cannot be promoted to a Poland 2021-2027 discovery source merely because current 2021-2027 pages link to it.

## Gate decision

- official government source family: **PASS**;
- searchable project surface: **PASS in principle**;
- authoritative current 2021-2027 coverage: **FAIL / NOT ESTABLISHED**;
- national 2021-2027 completeness: **FAIL / NOT ESTABLISHED**;
- pre-receipt field projection: **NOT INVESTIGATED because coverage fails first**;
- rich project-scope safety: **NOT INVESTIGATED because coverage fails first**;
- project-row/API smoke test: **PROHIBITED**;
- production eligibility: **REJECTED for Poland 2021-2027 discovery**.

No Mapa Dotacji project record, API response, export or project-detail body was fetched during this review.

## Reopen condition

Do not reopen this route unless an authoritative current source explicitly establishes that Mapa Dotacji UE covers the active 2021-2027 project population. If that occurs, the route must still pass the normal ProcRun gates for commercial rights, automated access, pre-receipt exclusion of prohibited person fields, sufficiently rich project-specific scope, and a source-side safety guarantee for any retained free text before any project-row request is allowed.

## Next source-search rule

Move to a genuinely different Poland source family rather than probing Mapa Dotacji internals. Prefer sources that can establish current 2021-2027 coverage and field-bounded transport from documentation before any project body is received.
