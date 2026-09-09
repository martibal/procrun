# A21a remote source candidates

Status: **NO ROW-INGEST ROUTE APPROVED YET**

ProcRun needs a remote, source-only project feed for A21a that never causes identity-bearing fields to enter the intelligence plane. Download-then-filter is prohibited.

## Closed routes

### OpenCoesione general project API

Blocked for A21a row ingest. The published project-list serializer includes `soggetto` references and the documented implementation exposes no server-side field projection that would let ProcRun exclude those values before receipt.

### OpenCoesione project-search CSV export

Blocked for A21a row ingest. The export explicitly includes `SOGGETTI_PROGRAMMATORI` and `SOGGETTI_ATTUATORI`. Filtering those columns after download would violate the zero-PII boundary.

## Current candidate: OpenBDAP MOP Lombardia OData

Candidate route:

`https://bdap-opendata.rgs.mef.gov.it/opendata/spd_mop_prg_mon_reg03_01_9999`

The official Lombardia MOP dataset is public and machine-readable, but its full 48-field surface includes identity-bearing fields such as `Codice Fiscale Titolare` and `Descrizione Titolare`.

Therefore the route remains **CONDITIONAL**. Metadata-only inspection is permitted. Project-row ingest remains prohibited until an automated probe proves all of the following before any project row is accepted:

1. an official OData route can be discovered deterministically;
2. the server supports an explicit projection/select operation;
3. the response contains only a frozen allowlist of project fields;
4. no tax identifier, holder identity, contact, address, beneficiary or other natural-person-capable field is present;
5. unknown/additional fields fail closed;
6. the route works from the remote execution environment used by ProcRun;
7. the selected fields provide enough project wording to support A21a evidence retrieval.

A successful projection probe authorizes only creation of a sanitized source-only package. It does not by itself approve production use or change any existing source contract.

## Next gate

Build and run a metadata/projection probe against OpenBDAP. It must inspect metadata first and may request a row only after the request itself is constrained to the frozen safe field allowlist. If server-side projection cannot be proven, this candidate is closed.
