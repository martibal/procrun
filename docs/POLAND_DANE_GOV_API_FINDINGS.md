# Poland dane.gov.pl API gate

Status: 2026-09-03

## Decision

The dane.gov.pl row API is **REJECTED as a production funded-project transport under the current zero-PII boundary**.

The portal remains useful for metadata discovery, but no funded-project data row may be requested unless an authoritative current API contract proves server-side output-field projection for the exact resource and the selected project-scope fields have an adequate pre-receipt zero-PII guarantee.

## Official API evidence

The official dane.gov.pl API documentation describes the service as a source of public data made available free of charge for re-use and explicitly lists companies building products and services based on data among intended API users.

The documented resource model includes:

- `GET /resources`
- `GET /resources/{id}`
- `GET /resources/{id}/data` — returns a list of rows
- `GET /resources/{id}/data/{row_id}` — returns a single row

Responses use JSON:API and the API is versioned.

Source reviewed:

- https://api.dane.gov.pl/doc

## Projection gate

The current public API documentation reviewed for `GET /resources/{id}/data` establishes row access, but does **not** document a `fields`, `select`, projection, sparse-fieldset, or equivalent parameter that guarantees excluded source columns are omitted from the HTTP response before ProcRun receives it.

This distinction is decisive. A row API is not automatically a field-bounded API.

ProcRun's absolute rule is that prohibited natural-person or supplier identity fields must not enter the response at all. Receiving a broad row and discarding fields locally would violate the boundary.

Therefore:

- row access: **PASS / documented**
- server-side output-field projection: **FAIL / NOT ESTABLISHED**
- broad-row receipt: **PROHIBITED**
- download-then-filter: **PROHIBITED**

No project row was requested during this review.

## Relation to the national SL2021 project list

The preceding national-source review established that the official Polish 2021-2027 project-list family contains useful project-specific scope, including project name and project description, while the broad distribution also contains identity-bearing beneficiary/contractor fields.

That makes field projection outcome-determinative for any dane.gov.pl resource exposing the same or materially equivalent project records. Without a documented pre-receipt projection contract, dane.gov.pl does not solve the blocked national bulk route.

## Rights

The API platform itself is explicitly intended for re-use, including use by companies building products and services. That is positive platform-level evidence.

However, production approval would still require the exact selected dataset/resource licence and conditions to be reviewed. The platform-level statement is not silently promoted into unconditional rights approval for every resource.

## Scope-text safety

Even if a future authoritative projection contract is found, production approval would still require a separate source-side guarantee for the selected project-specific scope fields. Rich free text cannot be assumed to be free of natural-person identifiers merely because identity columns are excluded.

No such guarantee is established by this review.

## Gate result

- public API existence: **PASS**
- machine-readable row endpoint: **PASS**
- platform re-use intent: **PASS**
- exact resource rights: **UNRESOLVED until a resource is selected**
- server-side field projection: **FAIL / NOT ESTABLISHED**
- broad-row zero-PII safety: **FAIL**
- project-scope zero-PII guarantee: **NOT ESTABLISHED**
- project-row smoke test: **PROHIBITED**
- production eligibility: **REJECTED**

## Re-open condition

Do not issue a funded-project row request unless all of the following are available first:

1. the exact current resource ID and schema are established from metadata only;
2. authoritative dane.gov.pl documentation proves server-side output-field projection for that resource endpoint;
3. the projected allowlist excludes every beneficiary, contractor, supplier, contact and natural-person identifier before receipt;
4. the retained project-description/scope fields have an explicit source-side privacy/masking/validation guarantee strong enough for ProcRun's zero-PII boundary;
5. exact resource rights and automated-access conditions are approved.

Until then, dane.gov.pl may be used only as a metadata/catalogue discovery surface for this product path.
