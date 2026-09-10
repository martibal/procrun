# A21a sanitized source ingress

Status: **GREEN — SANCTIONED REMOTE SOURCE POOL ROUTE ESTABLISHED**

ProcRun may build `a21a-sanitized-source-pool-v1` from the bounded OpenCoesione PR FESR Lombardia 2021-2027 Article 49 operation list because the received publisher resource itself is qualified before receipt. This is not download-then-filter as a privacy mechanism.

## Why the publisher resource is admissible

OpenCoesione states that its 2021-2027 beneficiary/operation publication is the minimum dataset required by Article 49 of Regulation (EU) 2021/1060, that the source is MEF-RGS-IGRUE, and that beneficiary names in this publication are limited to legal persons. The previously frozen RGS monitoring guidance independently applies the natural-person-information prohibition to `TITOLO_PROGETTO` and `SINTESI_PROG`.

For the bounded PR FESR Lombardia route, the privacy-relevant sanitization therefore happens at the publisher boundary before ProcRun receives the resource. The complete per-program publication is the approved source contract; local mapping into the smaller A21a JSON shape is product-schema projection, not removal of received personal data.

Frozen evidence:

- `https://opencoesione.gov.it/it/beneficiari_operazioni_2021_2027/`
- `https://opencoesione.gov.it/media/uploads/20241203_vademecum-monitoraggio-puc-rgs-vers10.pdf`
- Regulation (EU) 2021/1060, Article 49.

Frozen source:

- source id: `opencoesione_2021_2027_operations`
- programme: PR FESR Lombardia 2021-2027 only
- transport kind: `prebuilt_sanitized_resource`
- publisher zero-PII contract: `opencoesione-art49-minimum-rgs-v1`

## Package contract

Only `a21a-sanitized-source-pool-v1` may enter the A21a development/final-population machinery. It must state:

- `pii_review_status = ZERO_PII_CONFIRMED`
- `engine_output_present = false`
- `raw_archive_present = false` (no unqualified raw archive is retained or admitted)
- `download_then_filter_used = false`
- `source_only_projection_confirmed = true`
- `projection_boundary = upstream_before_receipt`
- `transport_kind = prebuilt_sanitized_resource`
- `projection_evidence_url` = frozen OpenCoesione publication page
- `source_id = opencoesione_2021_2027_operations`
- `publisher_resource_sha256` = exact received-resource SHA-256
- `list_updated_on` = exact source update date
- `publisher_zero_pii_contract = opencoesione-art49-minimum-rgs-v1`

Each case may contain only operation code, project title, project scope text, region, municipality, NUTS code, source URL and language. No beneficiary identity, tax code, contact data or engine output may enter the package.

## Remote implementation

`scripts/build_a21a_sanitized_source_pool.py` retrieves only the already-approved bounded source contract and emits the source-only JSON package. `scripts/validate_a21a_sanitized_source_pool.py` independently validates the package and hash/provenance contract.

`.github/workflows/a21a-sanitized-source-pool.yml` performs both steps remotely and publishes the package plus ingress report as a GitHub Actions artifact. No local PC, manual upload or human contact is required.

## What remains prohibited

- general OpenCoesione project API;
- general project-search CSV;
- unqualified OpenCoesione source families;
- Socrata project-row free text;
- Kohesio free-text project rows;
- beneficiary project pages;
- any source where personal data are received and then removed locally;
- any attempt to inspect a blocked row merely to determine whether it is safe.

The legacy live-SINTESI builder remains disabled because its old attestation model was ambiguous. The new builder is the only sanctioned A21a remote ingress route.

## Gate result

The A21a source-ingress problem is **closed GREEN**. The next A21a work is normal benchmark/final-population execution using the sanctioned package, not further source discovery.

The sealed A21/A21a/A21b holdout remains untouched by this source-ingress closure.
