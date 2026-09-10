# A21a remote source candidates

Status: **GREEN — PR FESR LOMBARDIA PUBLISHER-SANITIZED RESOURCE APPROVED**

ProcRun requires project evidence to be zero-PII before receipt. Downloading a broad source and then removing personal data locally remains prohibited.

## Approved source/transport combination

Frozen source:

`https://opencoesione.gov.it/it/opendata/beneficiari/2021-2027/beneficiari_PR_FESR_LOMBARDIA.zip`

OpenCoesione states that the 2021-2027 beneficiary/operation publication is the minimum dataset required by Article 49 of Regulation (EU) 2021/1060, that its source is MEF-RGS-IGRUE, and that beneficiary names in this publication are limited to legal persons. The frozen RGS Vademecum separately establishes the natural-person-information prohibition for both `TITOLO_PROGETTO` and `SINTESI_PROG`.

The bounded PR FESR Lombardia publication is therefore qualified as a **prebuilt sanitized publisher resource**. ProcRun is not relying on local removal of personal data: the privacy-relevant boundary is the publisher's Article 49/RGS publication contract, before receipt.

A compressed transport does not make an otherwise qualified publisher resource an unqualified raw archive. `raw_archive_present = false` means that no broader, unqualified source archive is admitted or retained in the A21a package path.

Frozen A21a provenance:

- `transport_kind = prebuilt_sanitized_resource`
- `projection_boundary = upstream_before_receipt`
- `publisher_zero_pii_contract = opencoesione-art49-minimum-rgs-v1`
- source id `opencoesione_2021_2027_operations`
- exact received-resource SHA-256 and list update date must be recorded
- output cases may contain only the A21a source-field allowlist
- `download_then_filter_used = false`
- engine output is prohibited

The live Lombardia data previously showed `SINTESI_PROG` textually identical to `TITOLO_PROGETTO`; therefore this closes the sanitized-pool ingress problem but does not invent a richer description for weak titles.

## Routes that remain blocked

### Regione Lombardia Socrata

Server-side `$select` exists, but `descrizione_operazione` has no dataset-specific public zero-PII content guarantee. Project-row receipt remains prohibited.

### Kohesio / EU Knowledge Graph

Projection exists, but the free-text summary lacks a field-level pre-receipt zero-PII guarantee.

### OpenCoesione general API and project-search CSV

These are broader source families and remain outside the bounded Article 49 per-program contract.

### Beneficiary project pages

Unstructured pages may contain natural-person/contact data and remain prohibited.

### OpenBDAP MOP Lombardia

No qualified project-title/project-description field class has been established.

## Final architecture

The A21a source-ingress search is closed. `scripts/build_a21a_sanitized_source_pool.py` plus `.github/workflows/a21a-sanitized-source-pool.yml` are the sanctioned remote construction path. The resulting package must pass `scripts/validate_a21a_sanitized_source_pool.py` before any development-set or final-population step.

No blocked source may be used as fallback and no sealed A21/A21a/A21b holdout is opened by this decision.
