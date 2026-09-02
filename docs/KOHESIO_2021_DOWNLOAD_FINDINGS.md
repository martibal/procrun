# Kohesio 2021-2027 route findings

Status date: 2026-09-02.

This note records the completed Kohesio route investigation. It does not approve a new ProcRun source
and does not change `SOURCE_CONTRACTS`.

## Final decision

**Kohesio 2021-2027 is not a production-safe Portugal 2030 discovery route for ProcRun.**

Two separate Kohesio transports were investigated:

1. EU Knowledge Graph / SPARQL: a frozen zero-PII query worked technically, but the known current
   operation `PACS-FC-01781200` returned zero rows. The tested graph layer therefore lacks required
   current Portugal 2030 coverage.
2. Current Kohesio 2021-2027 download/REST surfaces: Portugal-specific project data exists, but no
   server-side output-column projection or separately field-safe project distribution was found. The
   available project model/distribution can contain beneficiary identifiers, so ProcRun may not receive
   it and filter afterwards.

No more Kohesio project/data probes are authorised unless the Commission later publishes a documented
field-projection contract or a separately field-safe Portugal distribution.

## Catalogue probe

The official page
`https://kohesio.ec.europa.eu/en/data/projects-2021-2027/latest` returned a small HTML application shell
(2,651 UTF-8 bytes in the local 2026-09-02 probe) with no direct CSV/XLSX/RDF anchor links.

Observed result:

- HTTP content type: `text/html; charset=utf-8`;
- SHA-256: `c8b5ad33eb32ce3a8200cf5409aa2c926d12c0ca5656440a7a4c605526b804c3`;
- distribution bodies fetched: `false`;
- direct candidate anchors: `0`.

Distribution discovery is therefore JavaScript/API driven.

## Country-specific project object

A public open-source Kohesio client constructs a Portugal-specific 2021-2027 project URL using this
pattern:

`https://kohesio.ec.europa.eu/api/data/object?id=data/projects-2021-2027/latest/PT-pp21-27-latest.csv`

The same implementation uses a separate beneficiary-object path. This shows that country isolation is
possible, but country isolation is not a zero-PII field projection.

Supporting implementation:
`https://github.com/dataninjafi/eufundr/blob/d34eb440fad90f6dd3a4fa3b1a23d1665ecf3648/R/download_kohesio.R`

A documented 42-column Kohesio project record includes `beneficiary_unique_identifier`. The European
Commission Kohesio validator/specification independently defines `Beneficiary_Name` and
`Beneficiary_Unique_Identifier` alongside operation fields. Because a beneficiary may be a natural
person, ProcRun must not download the project file and remove those columns locally.

Decision for the country object route: **DATA SAFETY=BLOCKED**.

## Current `/projects` REST service

Frontend-only probes inspected the current official Kohesio HTML shell and its same-origin JavaScript
assets. They never called `/projects`, `/api/data/object`, SPARQL or a project distribution.

The final targeted service probe established the actual project-list call used by the frontend:

- route: `api + "/projects"`;
- request parameters are generated from `getProjectsFilters()` plus `offset`, `limit` and `language`;
- country/programming-period and other search filters are supported;
- the frontend receives the response object first and then maps `response.list` through its project
  deserializer;
- project detail similarly calls `api + "/projects/" + id` and deserializes the returned response.

No `fields`, `select`, projection or equivalent output-field parameter was found in the actual
`getProjects()` service path. Earlier keyword hits for `fields`, `select` and `projection` were UI,
HTML-form, Angular or map-projection code and were not request projection controls.

This does not prove that an undocumented server feature can never exist. It does prove that ProcRun has
no authoritative or implemented pre-receipt field projection on which a production zero-PII contract can
be based.

Decision for `/projects`: **DATA SAFETY=BLOCKED / ACCESS CONTRACT UNVERIFIED**. ProcRun does not issue a
project-response smoke request merely to discover whether prohibited fields happen to be present.

## Why downstream deserialization is insufficient

ProcRun's boundary applies before receipt. A client that receives a broad JSON object and then maps only
the fields it wants has already crossed the boundary. Therefore all of the following are insufficient:

- ignoring unknown JSON properties in a client model;
- selecting safe properties after the response arrives;
- downloading a country-specific CSV and dropping beneficiary columns;
- persisting a raw response and extracting only project fields later.

A future Kohesio route is eligible for reconsideration only if the server or a separately published
artifact excludes prohibited fields before ProcRun receives the response body.

## Frozen evidence/probes

Research scripts retained in the repository document the investigation:

- `scripts/probe_eukg_property_metadata.ps1`
- `scripts/probe_kohesio_pt2030_project.ps1`
- `scripts/probe_kohesio_2021_download_metadata.ps1`
- `scripts/probe_kohesio_frontend_route_metadata.ps1`
- `scripts/probe_kohesio_frontend_service_context.ps1`

Their presence does not authorise production use. Production source registration remains unchanged.

## Next route

Research returns to a Portuguese national field-bounded source. See
`docs/PT2030_NATIONAL_FALLBACK_GATE.md`.
