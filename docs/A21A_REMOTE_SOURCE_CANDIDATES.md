# A21a remote source candidates

Status: **OPENCOESIONE PR FESR LOMBARDIA FIELDS QUALIFIED; CURRENT BULK TRANSPORT NOT QUALIFIED FOR SANITIZED-POOL INGRESS**

ProcRun needs remote, source-only project evidence that does not introduce natural-person identity/contact data into the intelligence plane. Download-then-filter is prohibited as a privacy mitigation. Public availability alone is not sufficient: any free-text fallback must be safe **before receipt**, and the machine transport must ensure that ProcRun receives only allowlisted fields.

## OpenCoesione PR FESR Lombardia — field qualification

Published route:

`https://opencoesione.gov.it/it/opendata/beneficiari/2021-2027/beneficiari_PR_FESR_LOMBARDIA.zip`

The primary RGS source, **Vademecum Monitoraggio, versione 1.0, dicembre 2024, AP00 - Anagrafica progetto, page 39 of the document / PDF page 40**, states that `SINTESI_PROG` is a maximum-1,300-character project summary and explicitly applies the same natural-person information prohibition to both `TITOLO_PROGETTO` and `SINTESI_PROG`.

Primary source:

`https://opencoesione.gov.it/media/uploads/20241203_vademecum-monitoraggio-puc-rgs-vers10.pdf`

The fields are therefore qualified for A21a source wording in the bounded PR FESR Lombardia 2021-2027 context. However, the live PR FESR Lombardia universe currently has `SINTESI_PROG` textually identical to `TITOLO_PROGETTO`, so it does not currently provide a richer fallback surface for weak titles.

This field qualification does **not** by itself qualify the ZIP as an `a21a-sanitized-source-pool-v1` transport.

## OpenCoesione transport requalification — BLOCKED FOR SANITIZED-POOL CREATION

OpenCoesione's 2021-2027 beneficiary/operation publication documents programme data as downloadable open CSV files and provides widgets for republication on programme-authority websites. The crawler-facing Lombardia programme route does not expose a documented field-selective machine response; automated clients are directed to the Open Data area with complete datasets.

Consequently, the current OpenCoesione ZIP/CSV route fails the A21a transport boundary even though the title/summary fields themselves are source-qualified:

- the received payload is a broader bulk archive;
- allowlisted field projection happens only after receipt;
- this is `download_then_filter_used = true` under the A21a ingress semantics;
- a widget rendering path is not evidence of a documented field-selective API contract;
- the route must not be used to produce or attest an `a21a-sanitized-source-pool-v1` package.

A future OpenCoesione/RGS route may be reconsidered only if a publicly documented machine interface returns the allowlisted project fields upstream, before ProcRun receives any broader row or archive.

This transport decision does not revoke the field-level finding that `TITOLO_PROGETTO` and `SINTESI_PROG` are safe under the bounded RGS/OpenCoesione contract.

## Richer-fallback qualification — consolidated result

The 60-case development review found 14 project titles that were `NOT_USEFUL` on their own. Adding the already-admitted `specific objective` did not solve the problem: 0 of those 14 became `CLEAR`, 6 were `PARTIAL`, and 8 remained `NOT_USEFUL`. `specific objective` is therefore programme context only and is not a project-evidence fallback.

A separate qualification pass then examined the strongest realistic richer-source families that could avoid another title-only surface.

### Regione Lombardia PR FESR Socrata — BLOCKED

Dataset:

`https://www.dati.lombardia.it/resource/q78n-g3m9.json`

The official Regione Lombardia dataset exposes `DESCRIZIONE_OPERAZIONE` as a project-description field. Its API supports server-side projection, so beneficiary columns can technically be excluded before receipt. It is therefore a strong transport candidate.

It nevertheless fails ProcRun's privacy contract. The same dataset explicitly contains beneficiary names including natural persons. No dataset-specific public rule has been identified that guarantees `DESCRIZIONE_OPERAZIONE` itself cannot contain natural-person data. ProcRun may not receive that free text and then inspect, redact or reject it. The source remains blocked for row ingest.

### Kohesio / EU Knowledge Graph — BLOCKED

Public project query service:

`https://query.linkedopendata.eu/sparql`

Kohesio is a European Commission project-level aggregation. Its published data specification includes `Operation_Summary_Programme_Language`, and the public validator requires an individual person's `Beneficiary_Name` to be anonymised. Its SPARQL endpoint could technically project only project fields, making it another strong transport candidate.

The privacy evidence is still insufficient for ProcRun. The published anonymisation requirement is specific to `Beneficiary_Name`; no public field-level contract was found that guarantees `Operation_Summary_Programme_Language` itself cannot contain natural-person data. A projected free-text summary therefore still fails the pre-receipt zero-PII gate. Kohesio remains blocked for A21a row ingest unless such a source-level guarantee is established from public documentation.

### Beneficiary project pages — BLOCKED

Regulation (EU) 2021/1060 Article 50 can require or encourage beneficiaries to publish a short description of funded operations on their websites. Those pages can be rich and project-specific, but they are unstructured documents and may also contain names, telephone numbers, email addresses, staff profiles or other natural-person data. There is no source-wide projection or content contract that removes those data before receipt. Public web pages are therefore not an admissible A21a fallback source.

### OpenCoesione general API — BLOCKED

Historical response structure includes `soggetto` references and no approved server-side field-projection contract has been established.

### OpenCoesione project-search CSV — BLOCKED

The export includes `SOGGETTI_PROGRAMMATORI` and `SOGGETTI_ATTUATORI`. Receiving the export and filtering afterward is prohibited.

### OpenBDAP MOP Lombardia OData — BLOCKED

The metadata-only utility review found structured MOP attributes, but no explicit project-title/project-description field class that can satisfy the verbatim project-evidence requirement.

## Frozen architecture after qualification

There is currently **no approved source/transport combination that can create the required A21a real-data sanitized pool** while satisfying both the field-level zero-PII rule and the upstream-before-receipt projection boundary.

The product must therefore remain truthful and fail closed:

- source-field safety and transport safety are separate gates;
- approved OpenCoesione title/summary fields must not be obtained through the bulk ZIP/CSV route for A21a sanitized-pool creation;
- weak titles must not be upgraded with `specific objective` or other programme context;
- blocked richer sources must not be ingested merely to test whether their rows are safe;
- ProcRun must not generate, paraphrase or infer a richer source description;
- a route can be introduced only when public evidence establishes both project-text safety and upstream field-bounded transport.

The sealed A21/A21a/A21b holdout remains untouched.
