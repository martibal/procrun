# Frozen Portuguese component benchmark corpus

Status date: 2026-09-01.

## Purpose

This corpus is the first frozen quality-measurement surface for the Phase C local-model fallback. It
exists to answer a narrow question: when deterministic rules leave a scope span unmatched, can the
candidate model map that span to the existing frozen component taxonomy while citing the exact source
text?

It is not a production approval dataset and it does not define a pass/fail threshold.

## Privacy and provenance boundary

`tests/fixtures/component_benchmark_v1.json` contains 12 deliberately synthetic Portuguese project
scope sentences. They are authored benchmark examples, not copied project records and not extracted
from a live source.

Every case uses a synthetic `BENCH-*` operation code. The loader rejects non-`BENCH-*` codes, URLs,
email-like text, duplicate case IDs, duplicate operation codes, unknown taxonomy categories and
non-exact evidence spans. The fixture contains no source URLs, beneficiary fields, supplier fields or
contact fields.

This makes the quality fixture small, inspectable and independent of any broad raw-data retention.

## Coverage

Version `component-benchmark-v1` contains:

- 12 cases total;
- 10 positive component cases;
- 2 negative/abstention cases;
- all five frozen Phase C domains;
- Portuguese terminology intentionally not already frozen as deterministic phrase rules.

The positive cases cover examples such as UV treatment, telemetry, traction substations, electronic
interlocking, port lifting equipment, breakwater reinforcement, heat pumps, window-envelope work,
uncrewed thermal-imaging systems and digital dispatch/coordination.

The two negative cases test that vague or maintenance-only text can remain unresolved rather than
forcing a component proposal.

## Exact scoring

`src/procrun/model_benchmark.py` awards a true positive only when all five proposal facts match:

1. domain;
2. category;
3. absolute start offset;
4. absolute end offset; and
5. exact source text.

There is no fuzzy span credit and no semantic near-match credit.

The score reports:

- expected and predicted proposal counts;
- exact true positives, false positives and false negatives;
- exact precision, recall and F1 when defined;
- exact whole-case match rate;
- abstention-case count;
- correct abstentions; and
- negative cases polluted by a false component proposal.

Predictions must cover the exact frozen case set. Omitting a difficult case is an error rather than a
way to improve the score.

## Runtime report

`build_component_benchmark_report()` binds one report to:

- exact corpus SHA-256;
- one model ID;
- one model artifact SHA-256;
- one `llama-cli` SHA-256;
- exact benchmark score;
- cache-hit/inference counts; and
- measured per-inference elapsed seconds with median and maximum summaries.

Mixed model or runtime hashes are rejected. Case result operation codes and source hashes must also
match the requests generated from the corpus.

Peak RAM is intentionally not fabricated by this scoring layer. The adapter already enforces the
Linux address-space ceiling; empirical server-level RSS measurements belong in the later target-host
benchmark run.

## What this does not prove

A perfect score on 12 synthetic cases would only prove correct behavior on these frozen examples. It
would not establish production quality, population-wide accuracy or fitness for every Portuguese
infrastructure description.

Before any model is changed from `BENCHMARK_CANDIDATE`, the corpus must be expanded with a larger
PII-safe frozen evaluation set and the target CX33 host must produce reproducible RAM and latency
measurements. Any numerical approval threshold must be frozen explicitly rather than inferred from a
single benchmark run.
