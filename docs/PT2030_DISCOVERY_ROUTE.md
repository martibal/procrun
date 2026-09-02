# Portugal 2030 production discovery route investigation

Status date: 2026-09-02.

## Decision

No Portugal 2030 project-discovery route is production-approved yet.

The EU Knowledge Graph SPARQL route has now passed its transport and zero-PII smoke mechanics but failed
the first required **Portugal 2030 coverage** test: the known current operation
`PACS-FC-01781200` returned a valid SPARQL Results response with zero rows. The operation code is
independently current on Portugal's official Mais Transparência/PT2030 portal.

Therefore ProcRun must not broaden the EUKG query to discover data. The EUKG route is not a viable
PT2030 discovery source unless later evidence shows that Portugal 2021-2027 data has been loaded.

The next research candidate is the European Commission's newer Kohesio 2021-2027 project-download
surface at:

`https://kohesio.ec.europa.eu/en/data/projects-2021-2027/latest`

That surface is research-only. No CSV/XLSX/RDF project body may be downloaded until metadata proves that
a Portugal-specific and pre-receipt-safe distribution or projection exists.

Do not build a production collector for either candidate until every gate in this document is proven.

## Why the existing Portuguese routes remain blocked or conditional

### Mais Transparência project search

The project-only search surface is useful for discovery and exposes project name, operation code,
completion date and financing amount without requiring the full project-detail response.

It is not sufficient for ProcRun because the search results do not expose the project `Sumário` / scope
text required for component decomposition. The portal presentation-site terms also do not provide the
same explicit machine-reuse contract as a separately approved open-data/API route.

Decision: `CONDITIONAL`; human/reference discovery only.

### Mais Transparência project detail

The detail page contains the scope text ProcRun needs. A current example,
`PACS-FC-01781200` (Construção do novo porto das Lajes das Flores), exposes a detailed `Sumário`
covering port works, maritime signalling equipment, terminal construction, operational supervision and
control, and breakwater work.

The same HTTP document also contains the beneficiary section. ProcRun's zero-PII boundary is
pre-receipt: a broad response may not be downloaded and filtered afterwards. A beneficiary that happens
to be a company in one example does not prove that every project response is free of natural-person
data.

Decision: `BLOCKED` for intelligence ingestion.

### AD&C / dados.gov.pt PT2030 operations workbook

The official operations data has useful project-level fields, including operation identity and scope,
but the broad source surface also contains beneficiary fields and identifiers. The Kohesio-compatible
field model itself illustrates the same risk by defining `Beneficiary_Name` and
`Beneficiary_Unique_Identifier` alongside operation fields.

The specific PT2030 operations dataset also currently reports its licence as unspecified, so ProcRun
does not silently replace the source-specific licence with the dados.gov.pt portal-wide default.

Decision: `BLOCKED` for download-then-filter ingestion.

## EUKG SPARQL route: measured result

### What was proven

The European Commission EU Knowledge Graph public SPARQL surface can be queried with a frozen explicit
`SELECT` allowlist. ProcRun froze the model-facing properties and excluded beneficiary/contact fields,
including `P841` (beneficiary).

The local Phase 2 smoke probe queried only `PACS-FC-01781200` and the frozen safe variables. The endpoint
returned standards-compliant SPARQL Results XML over GET. ProcRun parsed it with DTD processing
prohibited and external entity resolution disabled, then validated every declared/returned binding name
against the frozen variable allowlist.

Result:

- transport: successful GET;
- media type: `application/sparql-results+xml;charset=utf-8`;
- target: `PACS-FC-01781200`;
- row count: `0`;
- `coverage_found`: `false`;
- no project binding was returned.

This resolves the earlier parser/transport uncertainty. The zero-row result is a real coverage result for
the tested graph/query, not a malformed-response artefact.

### Why this is a no-go for current PT2030 discovery

The exact operation code is independently published by Portugal's official Mais Transparência/PT2030
portal, including the project title and detailed summary. Therefore the graph miss is not explained by an
invalid fixture.

Current Commission material also says 2021-2027 Kohesio projects are not yet available for every
country. Other 2026 material demonstrates that the newer Kohesio platform/download layer does contain
2021-2027 project data, so the safest interpretation is that the EUKG query layer tested here must not be
assumed equivalent to the current downloadable Kohesio 2021-2027 project layer.

Decision: do **not** broaden the graph query, walk arbitrary properties, search beneficiary records, or
try alternative identifiers against project entities. Such exploration would weaken the pre-receipt
zero-PII guarantee without solving the production coverage requirement.

## Next candidate: Kohesio 2021-2027 download surface

A 2026 European Parliament study cites the European Commission Kohesio project dataset for the current
programming period at:

`https://kohesio.ec.europa.eu/en/data/projects-2021-2027/latest`

Commission/data.europa.eu material states that Kohesio datasets are available for download and free
reuse in machine-readable formats such as CSV/XLSX and RDF. This establishes that a current downloadable
project layer exists, but it does **not** by itself make that layer safe for ProcRun.

The broad Kohesio schema contains fields ProcRun must never receive, including beneficiary name and
beneficiary identifiers. Therefore a combined EU-wide or Portugal-wide file containing those columns is
still blocked under ProcRun's pre-receipt rule even if the file is openly licensed.

### Frozen metadata-only gate

Before any project distribution body is downloaded, ProcRun must inspect only the download catalogue
metadata and answer:

1. Does the current 2021-2027 surface expose a Portugal-specific distribution?
2. Is there a server-side field projection or a separate projects-only distribution that excludes
   beneficiary/person fields before receipt?
3. What exact media types, file names, update timestamps and stable URLs are exposed?
4. What exact licence/reuse metadata applies to that distribution?
5. Can the distribution be retrieved automatically without browser/session coupling or unstable signed
   links?

The metadata probe must not follow CSV/XLSX/RDF links. It may retrieve only the HTML catalogue page,
return catalogue link metadata and hash the page for provenance.

If the only available distribution is a broad project dataset containing beneficiary/person columns,
this route is `DATA SAFETY=BLOCKED` and ProcRun must move back to a national field-bounded source rather
than download and filter the file.

## Frozen production gate

Any future Portugal 2030 route may be added to `SOURCE_CONTRACTS` as `APPROVED` only after all of the
following are proven and retained in the repository.

1. **Current Portugal coverage**
   - known Portugal 2030 operation codes resolve;
   - coverage includes more than one programme/fund;
   - a stable operation identifier joins back to the Portuguese operation code.

2. **Scope availability**
   - Portuguese operation summary/scope is available;
   - for known fixtures, scope materially corresponds to the official Portugal source rather than a
     title-only or machine-generated synopsis.

3. **Pre-receipt zero-PII**
   - prohibited beneficiary/person/contact/tax fields are excluded by the server or by a separately
     published safe distribution before ProcRun receives a response body;
   - download-then-filter is not permitted;
   - broad graph walks, `SELECT *`, `DESCRIBE`, generic `CONSTRUCT`, and broad project records remain
     prohibited.

4. **Temporal provenance**
   - source last-update metadata may be retained but is not relabelled as first public observability;
   - after route approval, ProcRun's own first successful observation can establish `first_seen_at` for
     newly observed projects;
   - historical records without defensible snapshot evidence remain
     `temporal_provenance=UNRESOLVED`.

5. **Rights and access**
   - freeze endpoint/distribution owner and machine-access basis;
   - freeze source-specific commercial reuse/licence basis;
   - record attribution/change-disclosure obligations;
   - record availability/rate/fair-use constraints.

6. **Schema/provenance controls**
   - freeze exact received fields and parser schema;
   - bind retrieval to source URL, route/query version and content hash;
   - unknown fields or missing mandatory fields fail closed;
   - no broad raw response containing prohibited fields is persisted or received.

## Official evidence reviewed

- European Commission CORDIS SPARQL guide:
  `https://cordis.europa.eu/about/sparql`
- European Commission Kohesio validator/specification:
  `https://www.itb.ec.europa.eu/csv/kohesio/upload`
- European Commission ESF+ Kohesio page:
  `https://european-social-fund-plus.ec.europa.eu/en/data-and-figures/kohesio-esf-projects`
- European Commission Cohesion Open Data:
  `https://cohesiondata.ec.europa.eu/`
- data.europa.eu Kohesio data story/download documentation:
  `https://data.europa.eu/publications/datastories/linking-data-kohesio-platform`
- European Parliament 2026 study citing the current-period Kohesio download surface:
  `https://www.europarl.europa.eu/RegData/etudes/STUD/2026/783965/BUDG_STU(2026)783965_EN.pdf`
- European Commission legal/reuse notice:
  `https://commission.europa.eu/legal-notice_en`
- Mais Transparência Portugal 2030 example project:
  `https://transparencia.gov.pt/pt/fundos-europeus/pt2030/beneficiarios-projetos/projeto/PACS-FC-01781200/`
- Mais Transparência terms:
  `https://transparencia.gov.pt/pt/termos-e-condicoes/`
- dados.gov.pt terms:
  `https://dados.gov.pt/pt/termos-de-utilizacao`

## Bottom line

The EUKG/SPARQL experiment succeeded technically but failed the first required PT2030 coverage fixture.
It is therefore not the current production-discovery solution.

The next evidence-driven path is the official Kohesio **2021-2027 download catalogue**, starting with a
metadata-only inspection. No project file may be downloaded until the catalogue proves a pre-receipt-safe
Portugal distribution or server-side projection.