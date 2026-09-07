# ProcRun — programme concentration

## Purpose

This measure describes how concentrated current effective OPEN procurement needs are within the funded-programme dimension already present in the approved funded-project ledger.

Example:

`energy_efficiency:lighting — 8 of 11 programme-known OPEN needs are in PR FESR Lombardia 2021-2027 (72.7%)`

This is a descriptive portfolio distribution. It is not buyer concentration, supplier concentration, market dominance or procurement-risk scoring.

## Population

The population is the same current effective OPEN component population used by the OPEN purchasing-needs aggregation.

Each OPEN component is joined through its existing `operation_code` to the latest funded-project version.

The funded-project ledger contributes only:

- `operation_code`
- `programme`

No new source is introduced.

## Calculation

For each exact component category:

1. Count all current effective OPEN needs.
2. Count OPEN needs with non-null `programme`.
3. Group programme-known OPEN needs by `programme`.
4. Select the programme with the largest OPEN-needs count.
5. Calculate:

`top_programme_open_needs / open_needs_with_programme`

The denominator excludes null programme values.

Nulls are disclosed separately through:

`open_needs_with_programme / total_open_needs`

## Output

Per category:

- `total_open_needs`
- `open_needs_with_programme`
- `top_programme`
- `top_programme_open_needs`
- `top_programme_share_pct`

## Customer-safe boundary

This measure does not require or expose:

- buyer identity
- contracting-authority identity
- beneficiary identity
- personal contact data
- new procurement fields
- new external sources

Programme is already a customer-safe funded-project field in `customer-runway-v1`.

## Interpretation

Permitted:

`72.7% of programme-known OPEN lighting needs are in PR FESR Lombardia 2021-2027.`

Not permitted without a separately approved measure:

- buyer concentration
- customer concentration
- market dominance
- demand concentration
- dependency risk
- programme risk
- likely procurement behaviour