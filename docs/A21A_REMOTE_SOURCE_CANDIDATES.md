# A21a remote source candidates

Status: **OPENCOESIONE PR FESR LOMBARDIA OPERATION LIST APPROVED FOR A21a SOURCE-EVIDENCE INPUT**

ProcRun needs a remote, source-only project feed for A21a that does not introduce natural-person identity/contact data into the intelligence plane. Download-then-filter is prohibited as a privacy mitigation.

## Approved route — OpenCoesione 2021-2027 operation list

Approved A21a route:

`https://opencoesione.gov.it/it/opendata/beneficiari/2021-2027/beneficiari_PR_FESR_LOMBARDIA.zip`

The route was already approved in the production source registry. A later A21a review incorrectly concluded that `SintesiProgetto_OperationSummary` lacked the same natural-person safety rule already accepted for the project title.

The primary RGS source resolves that contradiction. In **Vademecum Monitoraggio, versione 1.0, dicembre 2024, AP00 - Anagrafica progetto, page 39 of the document / PDF page 40**, RGS states that `SINTESI_PROG` is a maximum-1,300-character project summary and immediately states:

> `Nei campi TITOLO_PROGETTO e SINTESI_PROG non vanno inserite informazioni sensibili riferibili a persone fisiche, quali il nome, il Codice fiscale, il numero di telefono o l’indirizzo e-mail.`

Primary source:

`https://opencoesione.gov.it/media/uploads/20241203_vademecum-monitoraggio-puc-rgs-vers10.pdf`

The A21a safety decision must therefore treat `TITOLO_PROGETTO` and `SINTESI_PROG` consistently. Both are covered by the same explicit upstream natural-person information prohibition. `SintesiProgetto_OperationSummary` is eligible as the primary source text for A21a evidence retrieval.

This approval is specific to the already-approved bounded PR FESR Lombardia 2021-2027 operation-list route. It does **not** reopen the general OpenCoesione project API or the project-search CSV export.

## Closed routes

### OpenCoesione general project API

Blocked for A21a row ingest. Historical response structure includes `soggetto` references and no approved pre-receipt projection contract has been established.

### OpenCoesione project-search CSV export

Blocked for A21a row ingest. The export includes `SOGGETTI_PROGRAMMATORI` and `SOGGETTI_ATTUATORI`; it is not the approved bounded operation-list contract.

### OpenBDAP MOP Lombardia OData

Blocked for A21a because it does not provide the required project-specific verbatim evidence surface under the approved safety contract.

### Regione Lombardia Socrata

Blocked for A21a verbatim evidence. Server-side column projection was proven, but no source-specific content rule equivalent to the RGS `TITOLO_PROGETTO`/`SINTESI_PROG` prohibition was established for its free-text description.

## Current position

A21a no longer needs a new text-source family. The next task is to use the approved OpenCoesione PR FESR Lombardia operation-list contract and evaluate whether `SintesiProgetto_OperationSummary` provides sufficient **customer utility and evidence-retrieval quality**. Safety is established by the upstream RGS rule; utility and retrieval accuracy remain empirical questions and must be tested separately.
