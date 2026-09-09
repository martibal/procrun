# A21a remote source candidates

Status: **NO ROW-INGEST ROUTE APPROVED YET**

ProcRun needs a remote, source-only project feed for A21a that never causes identity-bearing fields to enter the intelligence plane. Download-then-filter is prohibited.

## Closed routes

### OpenCoesione general project API

Blocked for A21a row ingest. The published project-list serializer includes `soggetto` references and the documented implementation exposes no server-side field projection that would let ProcRun exclude those values before receipt.

### OpenCoesione project-search CSV export

Blocked for A21a row ingest. The export explicitly includes `SOGGETTI_PROGRAMMATORI` and `SOGGETTI_ATTUATORI`. Filtering those columns after download would violate the zero-PII boundary.

### OpenBDAP MOP Lombardia OData

Candidate route:

`https://bdap-opendata.rgs.mef.gov.it/opendata/spd_mop_prg_mon_reg03_01_9999`

Status: **BLOCKED FOR A21a**.

The remote metadata-only utility probe ran successfully without requesting any project or OData rows. The public metadata documents structured project attributes including CUP, status, nature, typology, sector, subsector and category, but it does not document an explicit project-title or project-description field class suitable for verbatim customer-facing source evidence.

This fails the A21a product-utility gate before the privacy projection gate. ProcRun therefore does not proceed to `$select`, `$filter`, OData row retrieval or post-download sanitization for this candidate. The full dataset's identity-bearing fields, including `Codice Fiscale Titolare` and `Descrizione Titolare`, remain outside the ProcRun intelligence plane.

## Current position

All three evaluated remote shortcuts are closed for A21a source-evidence input. No project-row ingest route is approved.

The next source candidate must satisfy both conditions from public, machine-verifiable evidence before any row is received:

1. it exposes human-readable project wording sufficient for exact source evidence; and
2. it provides a pre-receipt server-side projection boundary that can exclude all identity/contact fields.

A source that satisfies only structured project metadata is not enough for ProcRun 2.0 evidence retrieval.
