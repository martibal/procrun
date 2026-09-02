# Kohesio 2021-2027 download-route findings

Status date: 2026-09-02.

This note records evidence discovered after the metadata-only catalogue probe. It does not approve a
new ProcRun source and does not change `SOURCE_CONTRACTS`.

## Catalogue probe result

The official page
`https://kohesio.ec.europa.eu/en/data/projects-2021-2027/latest` returned a small HTML application shell
(2,651 UTF-8 bytes in the local 2026-09-02 probe) with no direct CSV/XLSX/RDF anchor links.

Observed probe result:

- HTTP content type: `text/html; charset=utf-8`;
- SHA-256: `c8b5ad33eb32ce3a8200cf5409aa2c926d12c0ca5656440a7a4c605526b804c3`;
- distribution bodies fetched: `false`;
- direct candidate anchors: `0`.

Therefore distribution discovery is JavaScript/API driven and cannot be inferred from static catalogue
anchors.

## Country-specific object route discovered

A public open-source Kohesio client currently constructs country-specific 2021-2027 project URLs using
this pattern:

`https://kohesio.ec.europa.eu/api/data/object?id=data/projects-2021-2027/latest/PT-pp21-27-latest.csv`

The same client uses a distinct beneficiary-object path under `data/beneficiaries/latest/`. This is useful
evidence that Kohesio can isolate the project export by country before receipt.

This implementation is third-party evidence, not an authoritative Commission API contract. ProcRun does
not call the object URL on this basis alone.

Supporting implementation:
`https://github.com/dataninjafi/eufundr/blob/d34eb440fad90f6dd3a4fa3b1a23d1665ecf3648/R/download_kohesio.R`

## Why the country project CSV is still blocked

Country isolation is insufficient for ProcRun's zero-PII boundary. The same public client documentation
shows a 42-column Kohesio **project** record that includes `beneficiary_unique_identifier` alongside
operation fields and summaries.

The European Commission Kohesio validator/specification independently confirms that the Kohesio field
model contains both `Beneficiary_Name` and `Beneficiary_Unique_Identifier`; the latter is described as a
beneficiary identifier such as VAT/registration number. A beneficiary can be a person or an entity.

Under ProcRun's pre-receipt rule, a file that may include a beneficiary identifier must not be downloaded
and then filtered locally. An EUKG entity/Q identifier is also not treated as harmless merely because it
is indirect: if it refers to a natural-person beneficiary it is still an identifier connected to that
person.

Decision for the country CSV object route: **DATA SAFETY=BLOCKED unless an authoritative server-side
column projection or separately published field-safe export is proven.**

## Undocumented `/api/projects` route

A separate public implementation calls:

`https://kohesio.ec.europa.eu/api/projects?page=0&size=100&countryCode=RO`

and maps project title/description, dates, budgets, country/objective and coordinates. Its source comments
state that the endpoint does not provide the beneficiary tax identifier. However, that implementation
persists the entire JSON response and then selects only fields it needs; it does not prove that no other
beneficiary/person field is present in the received JSON object.

Supporting implementation:
`https://github.com/TudorAndrei/registru-fonduri-ue/blob/d2d748d2a559a74cbb54cfdc3d1b529b653db081/registru/sources/kohesio.py`

Therefore `/api/projects` remains **UNVERIFIED** for ProcRun. A narrow response is not inferred from what
a downstream mapper chooses to read.

## Next safe gate

Before any project API response is requested, inspect only the Kohesio frontend application code and
answer:

1. Which API routes are actually called by the current 2021-2027 frontend?
2. Does the current frontend or API expose a `fields`, `select`, projection, or equivalent output-field
   parameter?
3. Which country/programming-period filters are sent server-side?
4. Is there a schema/model definition that enumerates the full `/api/projects` response surface?

The corresponding ProcRun probe may retrieve only:

- the official Kohesio HTML application shell; and
- same-origin JavaScript assets referenced by that shell.

It must not invoke `/api/projects`, `/api/data/object`, SPARQL, or any CSV/XLSX/RDF distribution. It may
emit only asset hashes, API route literals and parameter-keyword metadata, never whole JavaScript bodies.

If no pre-receipt field projection or authoritative field-safe response contract is found, Kohesio's
2021-2027 download/REST surfaces remain blocked for ProcRun and research returns to a Portuguese national
field-bounded source.
