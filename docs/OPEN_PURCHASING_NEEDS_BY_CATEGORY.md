# ProcRun — OPEN purchasing needs across projects

## Purpose

This measure describes how many currently effective OPEN procurement needs ProcRun observes in each exact frozen component category, and across how many distinct funded projects those needs occur.

Example:

`energy_efficiency:lighting — 14 OPEN needs across 11 funded projects`

This is an observed portfolio distribution. It is not a market-size estimate, demand forecast, delay signal or procurement probability.

## Population

One component contributes when:

1. the component exists in the canonical component ledger;
2. its latest effective procurement observation is `OPEN`;
3. explicitly corrected observations are superseded by their correction history.

The latest component version supplies only:

- `component_id`
- `operation_code`
- `category`

The procurement history supplies only:

- `component_id`
- `operation_code`
- `observed_at`
- `state`
- correction linkage required to determine effective history

## Output

Per exact category:

- `open_needs`
- `funded_projects`
- `earliest_cutoff_date`
- `latest_cutoff_date`

`funded_projects` is `COUNT(DISTINCT operation_code)`.

## Customer-safe boundary

This measure does not require or expose:

- buyer identity
- contracting-authority identity
- beneficiary identity
- personal contact data
- new source fields
- new external sources

The aggregation remains inside the existing customer-safe component/project boundary.

## Interpretation

The measure may be described as:

`14 OPEN needs across 11 funded projects`

It must not be described as:

- market demand
- buyer demand
- hot market
- rising demand
- likely purchase
- delayed procurement
- total addressable market

unless a separately approved measure directly supports that claim.