# Portugal 2030 production discovery route investigation

Status date: 2026-09-02.

## Decision

No Portugal 2030 project-discovery route is production-approved yet.

Two European Commission routes have now been closed for current production use:

1. **EU Knowledge Graph SPARQL** passed the narrow transport/zero-PII mechanics but failed current
   Portugal 2030 coverage: known operation `PACS-FC-01781200` returned zero rows.
2. **Current Kohesio 2021-2027 project REST/download surfaces** have current-period data but do not expose
   a proven pre-receipt output-field projection. The country project export can contain beneficiary
   identifiers, and the frontend `/projects` service receives the response before client-side
   deserialization.

ProcRun will not weaken its zero-PII boundary by broadening graph queries, downloading broad project
files or calling a broad REST project endpoint merely to discover what fields happen to arrive.

The active research gate is now the Portuguese national fallback documented in
`docs/PT2030_NATIONAL_FALLBACK_GATE.md`.

## Existing Portuguese routes

### Mais Transparência project search

The project-only search surface is useful for discovery and exposes project title, operation code,
completion date and financing amount without requiring the full project-detail response. The observed
project-card surface is materially safer than project detail because beneficiary information is not part
of the card fields used for discovery.

It remains `CONDITIONAL` because:

- the exact automated/machine-access contract for this presentation-site route is unresolved;
- the site terms are not treated as an explicit commercial HTML scraping/reuse licence;
- the cards do not expose the project `Sumário` / scope used for component decomposition.

Decision: human/reference discovery only until the national fallback gate passes.

### Mais Transparência project detail

The detail page contains the scope text ProcRun needs. A current example,
`PACS-FC-01781200` (Construção do novo porto das Lajes das Flores), exposes a detailed `Sumário`
covering port works, maritime signalling equipment, terminal construction, operational supervision and
control, and breakwater work.

The same HTTP document also contains beneficiary content. ProcRun's zero-PII boundary is pre-receipt: a
broad response may not be downloaded and filtered afterwards. A beneficiary that happens to be a company
in one example does not prove that every project response is natural-person-free.

Decision: `BLOCKED` for intelligence ingestion.

### AD&C / dados.gov.pt PT2030 operations workbook

The official operations workbook has useful project-level identity and scope fields but also beneficiary
fields and identifiers. No server-side output-column projection has been established.

Current dados.gov.pt platform terms say data uploaded by state bodies is published under CC BY 4.0 by
default unless otherwise specified and describe commercial reuse of open data. This is a stronger general
rights signal than previously recorded. The PT2030 dataset page itself currently displays
`Licença não especificada`, so exact-source rights remain `CONDITIONAL` until that interaction is frozen
and reviewed explicitly.

This rights nuance does not change the production decision: the workbook remains `DATA SAFETY=BLOCKED`
because download-then-filter is prohibited.

## EU Knowledge Graph SPARQL result

### What was proven

The public EU Knowledge Graph SPARQL surface can be queried with a frozen explicit `SELECT` allowlist.
ProcRun froze the model-facing properties and excluded beneficiary/contact fields, including `P841`.

The local smoke probe queried only `PACS-FC-01781200` and the frozen safe variables. The endpoint returned
standards-compliant SPARQL Results XML over GET. ProcRun parsed it with DTD processing prohibited and
external entity resolution disabled, then validated every declared/returned binding name against the
frozen variable allowlist.

Result:

- transport: successful GET;
- media type: `application/sparql-results+xml;charset=utf-8`;
- target: `PACS-FC-01781200`;
- row count: `0`;
- `coverage_found`: `false`.

The exact operation is independently current on Portugal's official PT2030 portal. The zero-row result is
therefore a real coverage miss for the tested graph layer, not a malformed fixture or parser artefact.

Decision: retire EUKG for current PT2030 discovery. Do not broaden the query, walk arbitrary properties,
query beneficiary records, use `SELECT *`, `DESCRIBE` or generic `CONSTRUCT`.

## Kohesio 2021-2027 result

### Country project export

A Portugal-specific project object can be addressed in the current Kohesio data layer. However, the
project export/model can include `beneficiary_unique_identifier`; the Commission Kohesio field model also
defines beneficiary name and beneficiary unique identifier alongside project fields.

Country isolation is not field isolation. ProcRun therefore does not download the Portugal project file
and drop prohibited columns afterwards.

Decision: `DATA SAFETY=BLOCKED`.

### Current `/projects` frontend service

Frontend-only probes retrieved the official HTML shell and same-origin JavaScript assets but never called
a project/data endpoint.

The final service-context probe established the current frontend request path:

- `getProjects(...)` calls `api + "/projects"`;
- request parameters are produced by `getProjectsFilters()` plus `offset`, `limit` and `language`;
- search filters include country, programming period and other project dimensions;
- the full response is received and then `response.list` is mapped through a project deserializer;
- project detail calls `api + "/projects/" + id` and similarly deserializes the returned object.

No `fields`, `select`, projection or equivalent output-field parameter was found in the actual
`getProjects()` service call. Earlier appearances of those words in the JavaScript were UI/form/map or
framework code, not response projection controls.

Client-side deserialization does not satisfy ProcRun's pre-receipt rule. An undocumented server feature
cannot be assumed into the production contract.

Decision: current Kohesio `/projects` is `DATA SAFETY=BLOCKED / ACCESS CONTRACT UNVERIFIED` for ProcRun.
No project-response probe is authorised merely to inspect the payload.

See `docs/KOHESIO_2021_DOWNLOAD_FINDINGS.md` for the frozen evidence record.

## Active gate: Portuguese national fallback

The first national candidate is the Mais Transparência project-search-card surface because it appears to
provide a narrower project-only response than detail/bulk routes.

Two gates must be resolved independently before any collector is proposed:

1. **Exact-route rights/access** — establish whether the card/search transport may be automated and
   commercially reused; public visibility is insufficient.
2. **Scope sufficiency** — cards lack `Sumário`. A possible title-only mode must be evaluated as a
   deliberately reduced evidence source, not silently substituted for scope text.

The component engine requires exact supporting source spans and already fails ambiguous component
boundaries to `UNRESOLVED`. A title-only experiment must preserve that rule: it may extract only phrases
actually in the title, may not invent missing scope and may never turn absence of procurement evidence
into an OPEN result when the component boundary itself is unknown.

Before title-only discovery can alter the production contract, ProcRun must preregister and run a PII-safe
end-to-end replay against the frozen Phase-0 sample. The existing Phase-0 regression artifact is only a
classification oracle and must not be misrepresented as an extraction replay.

If title-only sufficiency fails, Portugal discovery remains blocked until a real field-projected scope
source exists.

## Frozen production gate

Any future Portugal 2030 route may be added to `SOURCE_CONTRACTS` as `APPROVED` only after all of the
following are proven and retained in the repository.

1. **Current Portugal coverage**
   - known Portugal 2030 operation codes resolve;
   - coverage includes more than one programme/fund;
   - a stable operation identifier joins to the Portuguese operation code.

2. **Scope/evidence sufficiency**
   - the normal route provides Portuguese project scope materially corresponding to the official source;
   - or a deliberately reduced source mode passes a preregistered end-to-end sufficiency test without
     weakening fail-closed component semantics.

3. **Pre-receipt zero-PII**
   - prohibited beneficiary/person/contact/tax fields are excluded by the server or a separately
     published safe distribution before ProcRun receives a response body;
   - download-then-filter is not permitted.

4. **Temporal provenance**
   - source last-update metadata is not relabelled as historical first observability;
   - after route approval, ProcRun's own first successful observation may establish `first_seen_at` for
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
   - bind retrieval to source URL, route/query version and content hash where applicable;
   - unknown fields or missing mandatory fields fail closed;
   - no broad raw response containing prohibited fields is received or persisted.

## Official evidence reviewed

- European Commission CORDIS SPARQL guide:
  `https://cordis.europa.eu/about/sparql`
- European Commission Kohesio validator/specification:
  `https://www.itb.ec.europa.eu/csv/kohesio/upload`
- European Commission ESF+ Kohesio page:
  `https://european-social-fund-plus.ec.europa.eu/en/data-and-figures/kohesio-esf-projects`
- data.europa.eu Kohesio data/download documentation:
  `https://data.europa.eu/publications/datastories/linking-data-kohesio-platform`
- European Commission legal/reuse notice:
  `https://commission.europa.eu/legal-notice_en`
- Mais Transparência Portugal 2030 project/search surfaces:
  `https://transparencia.gov.pt/pt/fundos-europeus/pt2030/beneficiarios-projetos/`
- Mais Transparência terms:
  `https://transparencia.gov.pt/pt/termos-e-condicoes/`
- dados.gov.pt terms and reuse guidance:
  `https://dados.gov.pt/pt/termos-de-utilizacao`
  `https://dados.gov.pt/pt/reuses/`

## Bottom line

Kohesio research is complete for the current source surfaces. EUKG lacks the required current Portugal
coverage, while the current 2021-2027 project download/REST surfaces lack a proven pre-receipt field
projection.

The active path is now a Portuguese national field-bounded fallback. No production source gate changes
until that route independently passes rights, access, data safety, coverage and scope-sufficiency tests.
