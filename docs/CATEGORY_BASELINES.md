# ProcRun category baseline contract

## Status

Implemented as the statistical foundation for later opportunity-age percentile ranking. This feature does not widen any source, privacy or customer-safe data boundary.

## Measure

For each exact frozen component taxonomy category, ProcRun computes the distribution of **observed days from the first effective stored `OPEN` observation to the first subsequent effective `CLOSED` observation** for each component.

The published descriptive fields are:

- `p25_days`
- `median_days`
- `p75_days`
- `n`

One component contributes at most one completed lifecycle to a baseline.

## Effective-history rule

`procurement_observations` remains append-only. A historical observation that is explicitly referenced by a later correction is excluded as a baseline endpoint. Correction rows are not used to mutate history.

`CLOSED` keeps the existing requirement for independently verifiable TED evidence. The baseline feature does not infer or relax CLOSED.

## Category boundary

Category is taken only from the existing frozen `component_versions.category` value, for example `energy_efficiency:lighting`. No broader or inferred category grouping is introduced.

## Interpretation boundary

The measure is ProcRun-observed lifecycle duration. It is **not** total project duration, procurement lead time outside ProcRun observation history, a probability, or a prediction.

The Market Intelligence view must always show `n` with the quartiles. It may display descriptive baselines for any available `n`, but a later feature that ranks a current opportunity by percentile must define and enforce its own minimum-sample threshold before customer-facing release.
