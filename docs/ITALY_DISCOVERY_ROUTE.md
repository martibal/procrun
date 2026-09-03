# Italy 2021-2027 funded-project discovery gate

Status date: 2026-09-03.

This document freezes the current research decision for Italy. It does **not** approve a live source and
does not add an entry to `SOURCE_CONTRACTS`.

## Product requirement

ProcRun may only ingest a funded-project route when commercial reuse, automated access and the exact
**pre-receipt** field surface are all approved. Natural-person names, fiscal/tax identifiers, contact data
and equivalent person identifiers are prohibited from the intelligence plane. Download-then-filter is not
a valid mitigation.

The funded-project source must also contain enough project scope to support exact component evidence
spans. Title-only discovery is not silently substituted for scope text.

## Candidate 1 — OpenCoesione relational `Progetti`

Phase-1 metadata was inspected without retrieving project records. The frozen workbook was:

- `https://opencoesione.gov.it/media/opendata/metadati_database_OC.xlsx`
- observed SHA-256: `464a55a9aa78d8f197e399714fdc8cd76c8970d46b0fa8ae172fe7d2c705ced6`
- observed size: 248,608 bytes.

The workbook confirms that `Progetti` is a separate relation from `Soggetti`, `Localizzazioni`,
`Pagamenti`, `Impegni`, `Fasi` and other complementary tables.

Useful project fields include:

- `COD_LOCALE_PROGETTO` — stable local project key;
- `CUP` — Codice Unico di Progetto;
- `OC_TITOLO_PROGETTO` — title; the metadata explicitly says natural-person first/last names or fiscal
  codes appearing in the supplied title are anonymised;
- `OC_COD_CICLO` / `OC_DESCR_CICLO` — programming period (`3` = 2021-2027);
- CUP nature/type/sector/subsector/category classifications;
- project-level financing and payment aggregates;
- `DATA_AGGIORNAMENTO`.

No direct natural-person name, person fiscal/tax identifier, contact, supplier or contractor identity field
was found in the `Progetti` relation. References to `soggetto`/`beneficiario` in the metadata are explanatory
text for aggregate amounts or the relational link to the separate `Soggetti` table, not identity columns in
`Progetti` itself.

### Current-cycle insufficiency

For 2021-2027, however, the metadata explicitly marks the following fields `Dato attualmente non
rilevato`:

- `OC_SINTESI_PROGETTO` — detailed project description / scope;
- `OC_DATA_INIZIO_PROGETTO`;
- `OC_DATA_FINE_PROGETTO_PREVISTA`;
- `OC_DATA_FINE_PROGETTO_EFFETTIVA`.

Therefore the relational `Progetti` table is **promising for data safety but insufficient as ProcRun's
current-cycle scope source**. It must not be promoted on title alone.

OpenCoesione's current FAQ also explains that the 2021-2027 project population is still progressively
populated and that the complete project set will be available after full activation/acquisition through the
new National Monitoring System. This is consistent with the metadata gaps above.

## Candidate 2 — OpenCoesione `/api/progetti`

The official API is intended for external software, is CC BY 4.0 and documents 12 anonymous requests per
minute (60/minute for registered users). That is a strong general rights/access signal.

A historical public OpenCoesione implementation (`DeppSRL/open_coesione`) is useful implementation
evidence but is **not treated as proof of the current production serializer**. In that implementation:

- the project-list serializer includes a `soggetto` field;
- project detail includes `ruolo_set` / subject links;
- documented GET controls cover filters, pagination and ordering;
- no output-field projection parameter is implemented in the project-list request path.

Because `Soggetti` may include individuals, ProcRun will not call `/api/progetti` merely to discover its
current response shape. The API route remains unapproved until current documentation proves a complete
safe response schema or server-side projection.

## Candidate 3 — `Lista beneficiari e operazioni 2021-2027`

This remains the **preferred Italy research candidate**, but it is not yet authorised for record receipt.

Official OpenCoesione documentation states that the lists are published as open CSV, split by Operational
Programme, updated bimonthly and licensed CC BY 4.0. The published surface includes beneficiary identity,
operation name and summary, dates, eligible expenditure, EU co-financing rate, location, intervention
category and update date.

This route therefore has the scope and timing fields missing from relational `Progetti`.

### Phase-2 metadata review

The exact linked metadata resource was retrieved without fetching beneficiary/operation records:

- `https://opencoesione.gov.it/media/opendata/metadati_beneficiari.xls`
- observed SHA-256: `c1e3be23c8ba7c84bc18a1183bd2e6ac0044f966843d72403ce0725b7cd4b96a`
- observed size: 38,400 bytes.

The workbook exposes 17 fields. Its relevant value rules are explicit:

- `CodiceFiscaleBeneficiario_BeneficiaryTaxCode`: when the beneficiary is an individual, the tax ID is
  not published and is overwritten by `*CODICE FISCALE*`;
- `NomeBeneficiario_BeneficiaryName`: when the beneficiary is an individual, the name is not published
  and is overwritten by `*INDIVIDUO*`;
- `TitoloProgetto_OperationName`: if the supplied project name contains a natural-person name/surname or
  tax ID, that information is not published.

No email, phone, personal contact, personal social identifier or equivalent direct-person field is present
in the 17-field metadata surface.

The route also contains the required project-scope and timing fields, including:

- `SintesiProgetto_OperationSummary` — detailed project description;
- `DataInizioProgetto_OperationStartDate`;
- `DataFineProgetto_OperationEndDate`;
- `CostoAmmesso_TotalEligibleExpenditure`;
- `TassoCofinanziamentoUE_EUCofinancingRate`;
- `CodicePostale_Postcode`;
- `StatoMembro_Country`;
- `CategoriaOperazione_CategoryIntervention`;
- `DataAggiornamento_LastUpdate`.

### Blocking issue — `OperationSummary`

The metadata supplies **no pre-publication anonymisation or exclusion rule for
`SintesiProgetto_OperationSummary`**. It describes the field only as a detailed project description.

OpenCoesione's public privacy FAQ confirms masking for natural-person fiscal codes and, in specified cases,
name/surname on the portal, but does not establish that arbitrary natural-person identifiers are removed
from the operation-summary free text before the CSV is published.

That distinction is decisive under ProcRun's boundary. A Phase-3 procedure that downloads an operation CSV
and then scans `OperationSummary` for personal data is not an acceptable safety test: receipt and scanning
would themselves process potentially identifying data. The source must be proven safe **before receipt**.

Therefore:

- Phase-2 identity-field rules: **PASS**;
- Phase-2 structured-field surface: **PASS**;
- Phase-2 scope sufficiency: **PASS**;
- Phase-2 `OperationSummary` pre-receipt safety: **UNPROVEN**;
- overall data-safety gate: **BLOCKED**;
- Phase-3 CSV smoke test: **NOT AUTHORISED**.

The next authorised action is documentation/provenance research only. ProcRun may proceed to a bounded CSV
smoke test only if an authoritative OpenCoesione/MEF publication rule, schema contract or equivalent source
proves that `OperationSummary` cannot expose natural-person identifiers before publication. If no such proof
can be established, this route must be rejected or used without the summary only where server-side/source-side
field projection can exclude it before receipt.

## OpenCUP enrichment — rejected

OpenCUP has useful CUP-keyed descriptive fields such as project/intervention descriptions, but available
project surfaces and observed project-record schemas can include beneficiary/person names and fiscal/tax
identifiers in the same record. No documented server-side output projection has been established.

Decision: **do not use OpenCUP as a scope enrichment route** under the current zero-PII boundary.

## Production status

No Italy funded-project source is production-approved yet.

Current research classification:

| Route | Rights | Access | Data safety | Scope | Research decision |
| --- | --- | --- | --- | --- | --- |
| OpenCoesione relational `Progetti` | strong | strong | promising | **blocked for 2021-2027** | safe-looking discovery table, insufficient scope |
| OpenCoesione `/api/progetti` | strong | strong | unresolved | insufficient/unresolved | do not call project records before current schema proof |
| 2021-2027 beneficiary/operation list | **strong** | **strong** | **BLOCKED: summary rule unproven** | **strong** | preferred candidate; documentation-only gate next |
| OpenCUP project/API | strong/open-data signal | conditional/API registration | **blocked** | strong | reject as enrichment unless future projection exists |

Nothing in this document changes the executable production registry.
