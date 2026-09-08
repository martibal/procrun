# ProcRun Phase M — empirical validation of the matching engine

Status: **PRE-REGISTERED / ACTIVE**

Phase M exists to measure whether ProcRun's project-to-procurement matching is accurate enough to support the product promise. It is a validation gate, not a marketing exercise and not a threshold-tuning exercise.

## Locked thresholds

- CLOSED precision: `correct / (correct + false_closed)` must be **>= 90%**.
- OPEN false-negative rate: `false_open / (confirmed_absence + false_open)` must be **<= 10%**.
- UNRESOLVED share: reported and explained; no hard pass threshold.
- Human review sample: **n >= 30 CLOSED and n >= 30 OPEN**.
- Doubtful CLOSED cases are reported separately and excluded from the precision denominator.
- OPEN cases where relevant procurement exists only outside TED scope are reported separately and excluded from the model false-negative denominator.

The thresholds above must not be altered after a sample has been drawn in order to manufacture a pass.

## Continuation rule

**A failed Phase M result does not terminate ProcRun.** A failed threshold creates a named remediation gate. The specific root cause must be isolated, fixed without retroactively changing the test threshold, and the affected validation must be repeated with a new deterministic sample. This loop continues until the matching approach satisfies the locked quality bar or a materially different data/matching architecture is implemented and validated under the same discipline.

No failed run may be hidden, deleted, rounded into a pass, or replaced by a more favourable post-hoc metric.

## Part A — current-state audit

Run:

```powershell
.\scripts\phase_m_append_audit.ps1
```

The command runs aggregate-only diagnostics against the central production database and **appends** the exact SQL and complete output to `docs/MATCHING_QUALITY_REPORT.md`. Existing measurements are never overwritten.

## Parts B/C — deterministic human-review sample

Frozen initial seed:

```text
phase-m-2026-09-08-v1
```

Prepare the review files with:

```powershell
.\scripts\phase_m_prepare_sample.ps1
```

Sampling order is `md5(seed || ':' || component_id)` over the latest production component assessment state. The sample is therefore deterministic, reproducible and fixed before a reviewer sees the selected cases.

The generated CSV files contain public/customer-safe project and component fields plus source URLs. They deliberately contain blank review columns. A human reviewer must inspect the source documents and fill those columns manually.

### CLOSED verdicts

Allowed values in `human_verdict`:

- `CORRECT`
- `FALSE_CLOSED`
- `DOUBTFUL`

The reviewer must open both the funded-project source and the TED evidence source and independently answer whether the procurement actually covers the purchasing need in that funded project.

### OPEN verdicts

Allowed values in `human_verdict`:

- `CONFIRMED_ABSENCE`
- `FALSE_OPEN`
- `OUTSIDE_TED_COVERAGE`

The reviewer must manually search TED over the same time window available to the model at the recorded cutoff. `OUTSIDE_TED_COVERAGE` is reserved for a relevant procurement known to exist only through a national/below-threshold route outside the declared TED scope; it is reported but is not a model false negative.

For every reviewed row, `human_reason`, `reviewer`, and `reviewed_at` are mandatory. A model or automated classifier may not provide the human verdict.

## Scoring

After human review:

```powershell
py .\scripts\score_phase_m_reviews.py `
  --closed .\docs\phase_m\reviews\phase_m_closed_phase-m-2026-09-08-v1.csv `
  --open .\docs\phase_m\reviews\phase_m_open_phase-m-2026-09-08-v1.csv `
  --append-report .\docs\MATCHING_QUALITY_REPORT.md
```

The scorer refuses to calculate a passing result unless both review categories contain at least 30 completed human reviews.

## Publication gate

The public Methodology page may state that matching accuracy has been empirically measured only after both locked thresholds pass with the required sample sizes. The public section must show the actual measured values, sample sizes, method and date.

Until that gate passes, no generic public accuracy claim is permitted.

## Repetition cadence

Phase M B/C must be repeated:

1. whenever `MATCH_RULE_VERSION` changes; and
2. at least quarterly even if matching code has not changed.

Quarterly review months are January, April, July and October. Each run uses a new pre-declared deterministic seed and is appended to `MATCHING_QUALITY_REPORT.md`.

A previous pass never grandfathers a later matching-rule version.