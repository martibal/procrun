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

This is now the **preferred Italy research candidate**.

Official OpenCoesione documentation states that:

- lists are published as open CSV and split by Operational Programme specifically to facilitate reuse,
  processing and extraction;
- the comprehensive list is updated bimonthly;
- the data are CC BY 4.0;
- published information includes beneficiary name **only for legal persons**, operation name, operation
  summary, operation start/end dates, eligible expenditure, EU co-financing rate, postcode/country,
  operation category and list update date;
- `Operation summary` maps to PUC2127 `SINTESI_PRG` and is intended to state what is being built/done,
  its purpose, and when necessary the type of territory, up to 1,300 characters;
- operation name must not contain names of natural persons.

This route therefore has the exact scope and timing fields missing from relational `Progetti`.

### Remaining zero-PII gate

The 2021-2027 publication layout also contains a field named `Codice fiscale Beneficiario`, sourced from
PUC2127 `SC00`. The current public page says beneficiary **names** are published only for legal persons,
and OpenCoesione's general privacy FAQ says a natural person's fiscal code is not published on the portal
and is masked. Those are strong signals, but ProcRun requires exact-route proof before receipt.

The page links an exact metadata file:

`https://opencoesione.gov.it/media/opendata/metadati_beneficiari.xls`

The next authorised research action is **metadata only**. Do not retrieve a beneficiary/operation CSV until
the metadata confirms the value rule for natural-person beneficiary fiscal codes/names and confirms that
no other natural-person/contact field is present.

Required Phase-2 metadata conclusions:

1. list every field in the 2021-2027 beneficiary/operation record;
2. prove the natural-person value rule for `Codice fiscale Beneficiario`;
3. prove the natural-person value rule for `Nome Beneficiario`;
4. confirm operation title/summary constraints;
5. confirm no email, phone, address-of-person, personal social identifier or equivalent person field;
6. freeze exact licence, owner, update cadence and attribution obligations.

If any natural-person identifier can be emitted, this route is `DATA SAFETY=BLOCKED` and the CSV body must
not be fetched. If values are demonstrably anonymised (`Individuo`, blank or another non-identifying
sentinel) before publication, a bounded Phase-3 smoke test may be designed.

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
| 2021-2027 beneficiary/operation list | **strong** | **strong** | **pending exact metadata** | **strong** | preferred candidate; metadata-only gate next |
| OpenCUP project/API | strong/open-data signal | conditional/API registration | **blocked** | strong | reject as enrichment unless future projection exists |

Nothing in this document changes the executable production registry.