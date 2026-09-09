# A21a Evidence Retrieval Benchmark Protocol

Status: **DEVELOPMENT BENCHMARK PROTOCOL — DOES NOT AUTHORIZE PRODUCT GO**

This protocol validates the ProcRun 2.0 evidence-first layer independently from the A21b interpretation/classification engine.

## What A21a measures

A21a answers one product question:

> Can ProcRun reliably surface the small amount of original project-document text a customer needs to inspect, while preserving exact source provenance and abstaining rather than inventing evidence?

It does not measure OPEN/CLOSED correctness, TED matching correctness, procurement existence, future buying probability or commercial value.

## Benchmark package

The development benchmark uses schema `a21a-evidence-benchmark-v1` and contains only zero-PII project source material already admitted by the ProcRun source boundary.

Each case contains:

- a stable `case_id` and `operation_code`;
- exact `project_scope_text` used as the source surface;
- source URL and language;
- independently adjudicated `relevant_excerpts` with exact start/end offsets and verbatim text.

Gold adjudication must be completed without seeing extractor output. `engine_output_used_for_gold` must therefore be `false`.

The package must explicitly state `pii_review_status = ZERO_PII_CONFIRMED` before the runner accepts it.

## What counts as a hit

The runner reports two retrieval concepts:

1. **Relevant overlap** — a returned sentence overlaps an independently marked relevant source span.
2. **Exact gold match** — the returned sentence has exactly the same text and offsets as a gold excerpt.

Relevant overlap is the primary retrieval signal because the extractor returns complete customer-readable sentences while adjudicators may mark a narrower relevant phrase. Exact-match rate remains visible as a stricter diagnostic.

## Hard integrity requirements

The following are non-negotiable and can be evaluated before numerical relevance thresholds are frozen:

- returned evidence must be an exact substring of `project_scope_text`;
- source URL and source field must remain correct;
- the evidence extractor must not generate or populate an English translation;
- repeated extraction on identical input must be deterministic;
- benchmark gold spans themselves must be exact source spans;
- sealed holdout material must be rejected by the development runner;
- zero-PII confirmation is mandatory.

Any violation of these conditions is a hard integrity failure.

## Reported development metrics

The development runner reports:

- evidence precision: share of returned excerpts that overlap gold evidence;
- gold excerpt recall: share of independently marked relevant excerpts hit by at least one returned excerpt;
- gold-positive case recall: share of cases containing relevant evidence where ProcRun returns at least one relevant excerpt;
- negative-case false-positive rate: share of gold-negative cases where ProcRun returns any excerpt;
- exact gold-match count;
- exact source-span integrity failures;
- provenance failures;
- translation violations;
- determinism failures.

## Threshold freeze rule

This development protocol deliberately does **not** define product-GO percentages yet.

Before any fresh final A21a evaluation:

1. build and adjudicate a representative development set;
2. inspect failure modes without using a sealed final holdout;
3. freeze the release-candidate evidence extractor;
4. preregister explicit numerical pass/fail thresholds;
5. freeze the final evaluation population and disjoint holdout;
6. only then run the final A21a gate.

Thresholds may not be selected after seeing final-evaluation results.

## Sealed holdout rule

`scripts/run_a21a_evidence_retrieval_benchmark.py` refuses any document with `sealed = true`.

The sealed holdout is not to be opened merely to tune keywords, ranking, sentence splitting or thresholds. A separate final-gate path may be created only after the release candidate and numerical thresholds are frozen.

## Relationship to A21b

A21a and A21b are independent:

- **A21a:** can ProcRun retrieve useful, exact source evidence?
- **A21b:** can ProcRun correctly interpret procurement/project status from the available evidence?

A21b is not required to make the evidence-first table useful, but A21a is a necessary quality gate for the ProcRun 2.0 product position. Passing A21a alone is not sufficient for paid public launch; all other release, safety, source and operational gates still apply.
