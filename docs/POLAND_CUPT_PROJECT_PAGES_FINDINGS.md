# Poland CUPT project-page findings

Status date: 2026-09-03.

This note evaluates CUPT's public 2021-2027 project-list pages as a distinct Poland source architecture after the national SL2021 bulk route, dane.gov.pl, Mapa Dotacji UE, and the CST implementation-contract report.

## Candidate 5 — CUPT public project-list pages (KPO / FEnIKS / FEPW)

CUPT publishes public project-list pages for current programmes including:

- Krajowy Plan Odbudowy (KPO);
- Fundusze Europejskie na Infrastrukturę, Klimat, Środowisko 2021-2027 (FEnIKS);
- Fundusze Europejskie dla Polski Wschodniej 2021-2027 (FEPW).

The KPO project list is an HTML project surface rather than a simple downloadable workbook. The public page exposes project-specific fields directly in the same HTML response, including project title/scope, applicant information, dates, programme/action identifiers, financial values and named evaluation personnel.

That transport shape is incompatible with ProcRun's absolute pre-receipt boundary. The fact that the page is public does not make receipt acceptable: ProcRun may not receive a broad page containing natural-person identity fields and then discard those fields locally.

## Gate decision

- current-period relevance: **PASS**;
- project-specific scope: **PASS in principle** for many entries because project titles can be materially descriptive;
- broad HTML data safety: **FAIL** because natural-person identity fields are present in the same response;
- pre-receipt field projection: **NOT DOCUMENTED** for the public project-list page;
- download/render-then-filter: **PROHIBITED**;
- further project-page or project-row smoke tests: **PROHIBITED**;
- production eligibility: **REJECTED** for the public CUPT project-list-page route.

The family is also not a substitute for a Poland-wide funded-project discovery source: CUPT covers transport-related programmes/investments under its remit rather than the full national 2021-2027 project universe.

## Safety incident note

During metadata/navigation research, opening the public KPO project-list URL returned project entries and natural-person evaluator identity fields directly in the HTML response before that response shape had been established. No such names or row content are reproduced or persisted in ProcRun. After the response shape became known, no further project-entry body inspection is authorised for this source family.

## Reopen condition

Do not reopen this route unless CUPT publishes an authoritative transport that guarantees, before receipt:

1. field-bounded output that excludes all natural-person identity fields;
2. sufficiently rich project-specific scope for exact component evidence;
3. a pre-publication zero-PII guarantee for every retained free-text scope field;
4. acceptable rights, access and temporal provenance.
