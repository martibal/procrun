# Portugal 2030 production discovery route investigation

Status date: 2026-09-02.

## Decision

No Portugal 2030 project-discovery route is production-approved yet.

The current best technical candidate is the European Commission Kohesio / EU Knowledge Graph SPARQL
surface, because a SPARQL `SELECT` can in principle project only ProcRun-approved project fields before
any response is received. It is **research-only** at this stage and is deliberately not added to the
live source registry.

Do not build a production collector for this candidate until every gate in this document is proven.

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

## EU candidate: Kohesio / EU Knowledge Graph SPARQL

### What is promising

European Commission material documents a public SPARQL query surface for the EU Knowledge Graph and
states that the graph contains Kohesio projects. SPARQL provides server-side variable projection, so a
frozen `SELECT` can request only approved variables rather than receiving a complete project record.

The Commission's current Kohesio validation specification defines fields that map closely to ProcRun's
required discovery record:

- `Operation_Unique_Identifier`;
- `Operation_Name_Programme_Language`;
- `Operation_Start_Date`;
- `Operation_Expected_End_Date` / `Operation_End_Date`;
- eligible expenditure amount/currency;
- NUTS/geographic indicators;
- `Operation_Summary_Programme_Language`;
- `Programming_Period` including `2021-2027`;
- programme/fund/objective fields; and
- `Date_Of_Last_Update`.

The same specification also includes fields ProcRun must never request, notably `Beneficiary_Name`,
`Beneficiary_Unique_Identifier` and social-media links. Their existence is not itself disqualifying if
the SPARQL transport can prove that only explicitly selected safe variables are returned.

### What is not proven

The route cannot be approved from the schema alone.

Current Commission documentation is inconsistent enough that coverage must be measured rather than
assumed:

- the CORDIS federated-query guide currently describes the Kohesio content in the EU Knowledge Graph as
  projects from the 2014-2020 programming period;
- a current Commission ESF+ page says 2021-2027 Kohesio projects are not yet available for every
  country; and
- the Kohesio validator already accepts `Programming_Period = 2021-2027`, which proves schema support
  but not that current Portugal 2030 operations are present in the query endpoint.

Public web/index searches performed on 2026-09-02 did not establish that the known Portugal 2030
operation `PACS-FC-01781200` is present in the EU Knowledge Graph. Search-engine absence is not treated
as proof of endpoint absence.

### Rights/access status

The Commission publicly documents machine queries against the SPARQL endpoint, which is strong evidence
that automated query access is an intended use. The Commission's general reuse notice permits reuse of
EU-owned website content under CC BY 4.0 unless otherwise indicated.

ProcRun nevertheless keeps commercial reuse **unresolved for this dataset** until the applicable
Kohesio/EU Knowledge Graph data licence and upstream Member-State project-data reuse basis are frozen
for the exact route. A general Commission website notice is not silently promoted into a source-specific
project-data licence.

## Frozen pre-production verification gate

Before this route may be added to `SOURCE_CONTRACTS` as `APPROVED`, all of the following must be proven
and retained in the repository.

1. **2021-2027 Portugal coverage**
   - known current Portugal 2030 operation codes must resolve through the endpoint;
   - coverage must include more than one programme/fund and not merely a hand-picked project;
   - the route must expose a stable operation identifier that can be joined back to the Portuguese
     operation code.

2. **Scope availability**
   - the Portuguese operation summary/scope must be available through a documented property;
   - for known fixtures, the returned scope must materially correspond to the official Portugal 2030
     source rather than a title-only or machine-generated synopsis.

3. **Pre-receipt zero-PII projection**
   - the exact query must use an explicit `SELECT` allowlist;
   - no beneficiary, beneficiary identifier/VAT, contact, social-media or person field may be selected;
   - no `DESCRIBE`, broad `CONSTRUCT`, `SELECT *`, generic property walk, or download-then-filter probe
     is permitted;
   - the response parser must reject any variable outside the frozen allowlist before persistence.

4. **Temporal provenance**
   - `Date_Of_Last_Update`, if available, may be retained as source metadata but must not be relabelled
     as first public observability;
   - after route approval, ProcRun's own first successful observation time may establish `first_seen_at`
     for newly observed projects;
   - historical records without defensible snapshot/observation evidence remain
     `temporal_provenance=UNRESOLVED`.

5. **Rights and access**
   - freeze the exact endpoint owner/operator and machine-access documentation;
   - freeze the source-specific reuse/licence basis applicable to Kohesio project data;
   - record attribution/change-disclosure obligations;
   - record any rate, fair-use or availability constraints.

6. **Schema/provenance controls**
   - freeze the exact SPARQL properties used for every ProcRun field;
   - freeze response media type and parser schema;
   - bind retrieval to source URL, query version and content hash;
   - unknown variables or missing mandatory variables fail closed;
   - no raw broad graph response is persisted.

## Safe next probe

The next network probe must first discover the **documented property identifiers** for the allowlisted
operation fields without walking arbitrary project records. Only after those property IDs are frozen may
a project query be executed.

The first project-level query should request only:

- operation identifier;
- operation name;
- operation summary in programme language;
- programming period;
- programme/fund;
- start/end dates;
- eligible/financing amount and currency;
- NUTS/geographic code; and
- source last-update date.

It must not request beneficiary or organisation data even for test purposes.

A successful response for one known operation is only a transport smoke test. Production approval
requires a small frozen cross-programme coverage sample and a documented source-specific rights review.

## Official evidence reviewed

- European Commission CORDIS SPARQL guide:
  `https://cordis.europa.eu/about/sparql`
- European Commission Kohesio validator/specification:
  `https://www.itb.ec.europa.eu/csv/kohesio/upload`
- European Commission ESF+ Kohesio page:
  `https://european-social-fund-plus.ec.europa.eu/en/data-and-figures/kohesio-esf-projects`
- European Commission Cohesion Open Data:
  `https://cohesiondata.ec.europa.eu/`
- European Commission legal/reuse notice:
  `https://commission.europa.eu/legal-notice_en`
- Mais Transparência Portugal 2030 example project:
  `https://transparencia.gov.pt/pt/fundos-europeus/pt2030/beneficiarios-projetos/projeto/PACS-FC-01781200/`
- Mais Transparência terms:
  `https://transparencia.gov.pt/pt/termos-e-condicoes/`
- dados.gov.pt terms:
  `https://dados.gov.pt/pt/termos-de-utilizacao`

## Bottom line

Kohesio/SPARQL is the first discovered route that plausibly solves the **transport** side of ProcRun's
zero-PII requirement while also having a schema capable of carrying the required project scope. It does
not yet solve the **coverage** and **source-specific rights** gates.

Therefore the Portugal production-discovery blocker remains open. The next useful work is a narrowly
scoped property/coverage verification of this EU route, not further scraping of Mais Transparência and
not another download of the broad AD&C workbook.
