# Phase M — M0-B TED safe structured CUP-linkage qualification

Status: **PREREGISTERED BEFORE LIVE SAMPLE EXECUTION**

## Purpose

Qualify one prospective TED Search API route for observing whether a frozen OpenBDAP MOP CUP later appears in TED, without receiving identity-bearing or free-text notice content.

This is a source/data-safety gate, not a commercial outcome test. It does not change the already frozen MOP cohort.

## Frozen MOP input

- Source observation date: `2026-08-31`
- Prospective window: through `2027-08-31`
- Cohort count: `1,356` CUPs
- Canonical cohort SHA-256: `daea98e853ba49ed8b69e0221a2d844c00462fdddce14f7f93a97b8c3a1608e2`
- Canonical planned-start rule: earliest valid planned execution start per CUP

## Public TED basis

Public TED documentation establishes that:

1. `POST /v3/notices/search` is an openly accessible Search API intended for reuse, including commercial reuse workflows.
2. The request body accepts an explicit `fields` list and the response notice records contain the requested fields.
3. `internal-identifier-proc` is a documented Search API field corresponding to eForms `BT-22-Procedure` (Internal Identifier for Procedure).
4. BT-22 is an authority-supplied procedure identifier. Its structure is not constrained, so its value is **not** safe to receive under ProcRun's zero-PII rule. It may only be used as a server-side query predicate in this gate.

Documentation:

- https://docs.ted.europa.eu/api/latest/search.html
- https://docs.ted.europa.eu/ODS/latest/reuse/search-api.html
- https://docs.ted.europa.eu/ODS/latest/reuse/field-list.html
- https://docs.ted.europa.eu/eforms/latest/schema/procedure-lot-part-information.html
- https://ted.europa.eu/en/legal-notice
- https://ted.europa.eu/en/news/fair-usage-policy-on-ted

## Permanent data-safety rule

**Datasikkerheten følger ikke av at kilden er offentlig, den følger av hva vi faktisk lar systemet motta.**

The qualification therefore MUST NOT request or receive:

- `internal-identifier-proc` values themselves;
- title or description fields;
- buyer/organisation/contact fields;
- names, email addresses, phone numbers or addresses;
- arbitrary notice free text;
- full XML/HTML/PDF notices.

There is no download-then-filter fallback.

## Frozen server-side matching rule

The only permitted CUP linkage candidate is an expert-query equality predicate on:

`internal-identifier-proc`

Transport syntax candidates, in this order, are frozen as:

1. `internal-identifier-proc = "<CUP>"`
2. `internal-identifier-proc = <CUP>`

A syntax candidate may be rejected only for transport/query-syntax failure. Result presence/absence MUST NOT be used to choose between syntaxes.

No search against title, description, buyer fields or generic full-text is permitted if this route fails.

## Frozen returned-field allowlist

Only these structured fields may be requested:

- `publication-number`
- `publication-date`
- `notice-type`
- `classification-cpv`
- `estimated-value-proc`
- `estimated-value-cur-proc`

TED may add its documented `links` object to each result. It may be validated as HTTPS metadata but MUST NOT be persisted or followed by this gate.

No other notice field is permitted.

## Frozen qualification sample

The sample is the first 20 CUPs in lexicographic order from the already frozen 1,356-CUP cohort. The sample is fixed in `scripts/qualify_ted_mop_safe_linkage.py` before live execution.

The qualification report persists aggregate counts only. It MUST NOT persist CUP-to-notice rows, raw notices, returned field values, titles or descriptions.

## Frozen controls and metrics

The run records:

- selected query syntax and number of syntax attempts;
- support for every safe projected field;
- sample size;
- number of sampled CUPs with at least one TED hit;
- aggregate number of matching notices;
- maximum notice count for one sampled CUP;
- number of returned safe notice objects;
- whether any unrequested field escaped the allowlist.

The run explicitly records:

- `identity_fields_received = false`
- `free_text_received = false`
- `internal_identifier_values_received = false`
- `raw_notices_persisted = false`
- `outcome_rows_persisted = false`

## Decision rule

**PASS** requires all of the following:

1. TED accepts one of the predeclared query syntaxes.
2. All frozen structured returned fields are supported.
3. Every response remains inside the frozen pre-receipt allowlist.
4. At least one of the 20 frozen CUPs has a TED result through the structured `internal-identifier-proc` predicate.

If 1–3 pass but the frozen 20-CUP sample produces zero structured CUP hits, the route is **BLOCKED_NO_STRUCTURED_CUP_EVIDENCE**. That does not prove the projects never entered procurement; it proves only that this exact zero-free-text TED linkage route is not evidenced strongly enough to activate.

If the route is blocked, ProcRun MUST NOT broaden the search to title/description/free-text fields.

## Later prospective outcome semantics

Only after M0-B passes may the full 1,356-CUP outcome protocol be activated.

For that later protocol:

- a TED match is a TED-observed procurement materialisation, not proof of all procurement activity;
- no TED match is not proof of no procurement;
- notices published before `2026-08-31` are baseline contamination/pre-existing TED visibility and cannot count as prospective lead time;
- primary commercial evidence remains usable lead time from frozen MOP observation to first qualifying TED publication on or after `2026-08-31`.
