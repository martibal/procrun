# Poland national funded-project route findings

Status date: 2026-09-03.

This note starts the Poland expansion-source review required by the locked Phase 2 order in the repository: Italy, then Poland. It does not approve a new ProcRun source and does not change `SOURCE_CONTRACTS`.

## Candidate 1 — Portal Funduszy Europejskich / SL2021 national project list

Official source family:

- Portal Funduszy Europejskich: `Lista projektów realizowanych z Funduszy Europejskich w Polsce w latach 2021-2027`;
- current public distributions are XLSX and CSV;
- source data is stated to come from the Centralny system teleinformatyczny SL2021.

The official publication describes the national 2021-2027 project list as containing, among other fields:

- `Nazwa projektu` — project name;
- `Opis projektu` — project description;
- agreement/decision number;
- `Nazwa beneficjenta` — beneficiary name;
- `Nazwa wykonawcy kontraktu` — contract-contractor name;
- fund, specific objective, programme, priority and action;
- project value and EU contribution;
- place of implementation;
- project start and end dates;
- support category.

The project name and project description are potentially rich enough for ProcRun component evidence. The same broad published project record also contains beneficiary and contractor identity fields.

## Zero-PII decision

ProcRun's boundary is pre-receipt. A broad XLSX/CSV file may not be downloaded and then reduced locally.

For the official national SL2021 publication route reviewed here:

- scope richness: **PASS in principle** because `Opis projektu` is present;
- national 2021-2027 coverage: **PASS in principle**;
- automated bulk availability: **PASS**;
- pre-receipt field projection: **NOT DOCUMENTED for this publication route**;
- broad distribution data safety: **FAIL** because beneficiary and contractor identity fields are part of the same published file;
- project-row/file smoke test: **PROHIBITED**;
- production eligibility: **REJECTED for the bulk route**.

No XLSX or CSV body was fetched during this review.

## Candidate 2 — dane.gov.pl API

Poland's official `dane.gov.pl` platform remains a separate candidate rather than being rejected by the bulk-file decision above.

The platform documents a public JSON:API with resource metadata and `GET /resources/{id}/data` row access. Its own API documentation says the service is intended for re-use, including companies building products and services from public data. The portal also states that data can be used free of charge, including commercially.

That makes `dane.gov.pl` materially different from a simple bulk-download mirror **if** all of the following can be established for a current 2021-2027 SL2021 project resource:

1. the exact current resource can be identified from metadata without receiving project rows;
2. the deployed row endpoint supports authoritative server-side output-field projection;
3. the projection can exclude beneficiary, contractor and any other prohibited identity fields before receipt;
4. `Opis projektu` or an equivalent project-specific scope field is included in the safe projected surface;
5. the scope field itself has a sufficiently strong pre-publication zero-PII guarantee, or an independently safe structured substitute exists.

Until those points are proven, `dane.gov.pl` is **RESEARCH-ONLY / NOT PRODUCTION-APPROVED**.

## Next authorised action

Research the `dane.gov.pl` metadata/API contract only. Do not request a project data row until the exact resource and server-side projection semantics are established from metadata/documentation.
