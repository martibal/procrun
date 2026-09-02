# Frozen Portuguese component benchmark corpora

Status date: 2026-09-02.

## Purpose

The Phase C local-model fallback now has two frozen synthetic Portuguese evaluation surfaces:

- `tests/fixtures/component_benchmark_v1.json` — the primary diagnostic/regression corpus;
- `tests/fixtures/component_benchmark_holdout_v1.json` — a disjoint holdout corpus.

Both answer the same narrow question: when deterministic rules leave a scope span unmatched, can the
candidate model map that span to the existing frozen component taxonomy while citing the exact source
text?

Neither corpus is a production approval dataset and neither defines a pass/fail threshold.

## Privacy and provenance boundary

Both fixtures contain deliberately synthetic Portuguese project-scope sentences. They are authored
benchmark examples, not copied project records and not extracted from a live source.

Every case uses a synthetic `BENCH-*` operation code. The loader rejects non-`BENCH-*` codes, URLs,
email-like text, duplicate case IDs, duplicate operation codes, unknown taxonomy categories and
non-exact evidence spans. The fixtures contain no source URLs, beneficiary fields, supplier fields or
contact fields.

This keeps model quality evaluation inside the zero-PII intelligence boundary.

## Primary corpus

`component_benchmark_v1.json` contains:

- 12 cases total;
- 10 positive component cases;
- 2 negative/abstention cases;
- all five frozen Phase C domains;
- Portuguese terminology intentionally not already frozen as deterministic phrase rules.

This is the corpus used to diagnose the first Qwen3-4B run and the taxonomy-boundary errors found in
that run. It may therefore be used for regression diagnosis, but improvement on this corpus alone is
not treated as independent validation.

## Holdout corpus

`component_benchmark_holdout_v1.json` contains a separate:

- 12 cases total;
- 10 positive component cases;
- 2 negative/abstention cases;
- coverage across all five frozen Phase C domains;
- distinct case IDs and distinct operation codes from the primary corpus;
- distinct synthetic wording and component examples.

The holdout was frozen before the next empirical model run. It is not a source of per-case prompt
answers. Taxonomy guidance must remain category-level and general; benchmark-case wording or expected
answers must never be inserted into prompts, selection rules or deterministic extraction merely to
raise the score.

If the holdout expected answers are later edited after inspecting model output, that creates a new
holdout version and the previous result must remain attributable to the old corpus SHA-256.

## Model-facing taxonomy guidance

Every allowed category serialized into a local-model request now carries a computed
`selection_rule`. The rules are versioned by
`MODEL_CATEGORY_GUIDANCE_VERSION = "component-model-guidance-v1"` and cover the exact frozen taxonomy.

The guidance describes semantic boundaries between neighboring categories, for example control versus
monitoring, rail signalling versus traction power, marine structural works versus landside civil
works, and sensing/imaging platforms versus vehicles. These are taxonomy definitions, not benchmark
case answers.

Import-time validation fails if a frozen taxonomy category lacks a model selection rule or if guidance
exists for a category outside the taxonomy.

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

## Runtime reports

`build_component_benchmark_report()` binds each report to:

- exact corpus SHA-256;
- one model ID;
- one model artifact SHA-256;
- one `llama-cli` SHA-256;
- exact benchmark score;
- cache-hit/inference counts; and
- measured per-inference elapsed seconds with median and maximum summaries.

The target-host runner executes the primary and holdout corpora in the same ephemeral CX33 session,
using the same verified model artifact and `llama.cpp` runtime. This avoids paying for two host
provisioning/build cycles while keeping the corpus reports cryptographically separate.

Peak RAM is not fabricated by the scoring layer. The adapter enforces the Linux address-space ceiling;
GNU `time -v` resource reports are retained separately for both corpus runs.

## What this does not prove

A perfect score on either small synthetic corpus would only prove correct behavior on those frozen
examples. It would not establish population-wide accuracy or fitness for every Portuguese
infrastructure description.

Before any model changes from `BENCHMARK_CANDIDATE`, evaluation still requires a larger PII-safe
frozen set, target-host RAM and latency evidence, explicit error analysis and an explicit governance
decision. Any numerical approval threshold must be frozen explicitly rather than inferred from a
single benchmark run.
