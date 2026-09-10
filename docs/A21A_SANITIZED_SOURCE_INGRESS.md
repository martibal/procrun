# A21a sanitized source ingress

Status: **MANDATORY PRECONDITION FOR A21a REAL-DATA DEVELOPMENT SET**

This gate exists because ProcRun must not make the user's local PC, a raw OpenCoesione archive, or download-then-filter processing part of the A21a validation path.

## Accepted input

Only a pre-sanitized `a21a-sanitized-source-pool-v1` JSON package may enter the A21a development-set builder.

The package must explicitly state:

- `pii_review_status = ZERO_PII_CONFIRMED`
- `engine_output_present = false`
- `raw_archive_present = false`
- `download_then_filter_used = false`
- `source_only_projection_confirmed = true`
- `projection_boundary = upstream_before_receipt`
- `transport_kind = field_selective_endpoint` or `prebuilt_sanitized_resource`
- `projection_evidence_url = <HTTPS public evidence for the projection/transport contract>`

A boolean assertion by itself is not sufficient. The transport must prove that only allowlisted source fields existed in the payload received by ProcRun.

Each case may contain only the project fields required for evidence retrieval: operation code, project title, project scope text, region, municipality, NUTS code, source URL and source language.

## Rejected input

The ingress gate rejects:

- raw ZIP/CSV source archives;
- beneficiary identity or beneficiary tax-code fields;
- contact, email, phone, address or natural-person identity fields;
- extractor, classifier or other engine output;
- unverified PII status;
- any source package produced by download-then-filter;
- any transport where projection occurs locally after ProcRun receives a broader payload;
- a bulk archive labelled safe only by setting attestation flags;
- missing or non-HTTPS projection-contract evidence;
- unknown extra case or provenance fields.

This is intentionally stricter than the runtime OpenCoesione collector. A21a validation must operate only on already-sanitized source-only material.

The legacy `build_a21a_live_sintesi_development_sample.py` route is permanently disabled under this contract because it received the complete OpenCoesione ZIP before local projection. It must not be used to create or attest an `a21a-sanitized-source-pool-v1` package.

## OpenCoesione widget / Lombardia qualification

The OpenCoesione 2021-2027 beneficiary/operation publication confirms that programme lists are distributed as open CSV files and that programme authorities may republish the lists through OpenCoesione widgets. Public crawler access to the Lombardia programme data route directs automated consumers to the Open Data section containing complete datasets rather than exposing a documented field-selective machine endpoint.

Therefore:

- the RGS rule still qualifies `TITOLO_PROGETTO` and `SINTESI_PROG` as safe source fields for the bounded PR FESR Lombardia context;
- the current OpenCoesione ZIP/CSV distribution does **not** satisfy `projection_boundary = upstream_before_receipt`;
- the widget is not evidence of a field-selective API contract and must not be used to attest a sanitized pool;
- a future route may qualify only if public documentation and the actual machine transport establish that ProcRun receives allowlisted fields only.

## Remote-only operating requirement

The sanctioned package must be made available through a remote resource ProcRun can consume directly (for example, an approved GitHub artifact or server-side sanitized package). Creating the package must not require the user to run commands, upload raw data, or keep a local PC/SSH session alive.

The current repository does not contain the sanctioned A21a real-data source pool. The validation code therefore fails closed until such a package exists.

## Sequence

1. Obtain or recover an already-sanitized source-only package from an approved remote location.
2. Verify its upstream projection evidence and transport kind.
3. Run `validate_a21a_sanitized_source_pool.py`.
4. Only on PASS, run `prepare_a21a_evidence_development_set.py`.
5. Perform blind evidence adjudication.
6. Run the A21a evidence retrieval benchmark.

The sealed A21/A21a holdout remains untouched throughout this sequence.
