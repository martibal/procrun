# A21a Evidence Retrieval Benchmark Protocol

Status: **DEVELOPMENT BENCHMARK PROTOCOL — DOES NOT AUTHORIZE PRODUCT GO**

This protocol validates the ProcRun 2.0 evidence-first layer independently from the A21b interpretation/classification engine.

## What A21a measures

A21a answers one product question:

> Can ProcRun reliably surface the small amount of original source wording a customer needs to inspect, while preserving exact provenance and source type and abstaining rather than inventing evidence?

It does not measure OPEN/CLOSED correctness, TED matching correctness, procurement existence, future buying probability or commercial value.

A21a validates usefulness, correctness and provenance of the **best available approved source wording**. A successful evidence result may be an exact project title or an exact excerpt from a richer description. There is no minimum character count or sentence count merely for a result to qualify.

## Benchmark package

The development benchmark uses schema `a21a-evidence-benchmark-v1` and contains only zero-PII project source material already admitted by the ProcRun source boundary.

Each case contains:

- a stable `case_id` and `operation_code`;
- the exact approved source wording used as the evidence surface;
- the actual source field/type (`Project title` or `Project description`);
- source URL and language;
- independently adjudicated `relevant_excerpts` with exact start/end offsets and verbatim text.

Where an approved description is identical to the project title, it must be represented as one `Project title` evidence surface rather than two apparently independent sources.

Gold adjudication must be completed without seeing extractor output. `engine_output_used_for_gold` must therefore be `false`.

The package must explicitly state `pii_review_status = ZERO_PII_CONFIRMED` before the runner accepts it.

## What counts as a hit

The runner reports two retrieval concepts:

1. **Relevant overlap** — returned source wording overlaps an independently marked relevant source span.
2. **Exact gold match** — returned wording has exactly the same text and offsets as a gold excerpt.

Relevant overlap is the primary retrieval signal because an evidence surface may be a complete title or a customer-readable excerpt while adjudicators may mark a narrower relevant phrase. Exact-match rate remains visible as a stricter diagnostic.

## Hard integrity requirements

The following are non-negotiable and can be evaluated before numerical relevance thresholds are frozen:

- returned evidence must be an exact substring of the declared approved source field;
- source URL and source field/type must remain correct;
- a title must never be mislabeled as a project description;
- the evidence extractor must not generate or populate an English translation;
- repeated extraction on identical input must be deterministic;
- benchmark gold spans themselves must be exact source spans;
- sealed holdout material must be rejected by the development runner;
- zero-PII confirmation is mandatory.

Any violation of these conditions is a hard integrity failure.

## Reported development metrics

The development runner reports:

- evidence precision: share of returned evidence items that overlap gold evidence;
- gold excerpt recall: share of independently marked relevant excerpts hit by at least one returned evidence item;
- gold-positive case recall: share of cases containing relevant evidence where ProcRun returns at least one relevant item;
- negative-case false-positive rate: share of gold-negative cases where ProcRun returns any evidence item;
- exact gold-match count;
- exact source-span integrity failures;
- provenance/source-type failures;
- translation violations;
- determinism failures.

The development report must also separate results by source type where more than one source type exists in the benchmark.

## Threshold freeze rule

This development protocol deliberately does **not** define product-GO percentages yet.

Before any fresh final A21a evaluation:

1. build and adjudicate a representative development set;
2. inspect failure modes without using a sealed final holdout;
3. freeze the release-candidate evidence retriever;
4. preregister explicit numerical pass/fail thresholds;
5. freeze the final evaluation population and disjoint holdout;
6. only then run the final A21a gate.

Thresholds may not be selected after seeing final-evaluation results.

## Sealed holdout rule

`scripts/run_a21a_evidence_retrieval_benchmark.py` refuses any document with `sealed = true`.

The sealed holdout is not to be opened merely to tune selection, ranking, text segmentation or thresholds. A separate final-gate path may be created only after the release candidate and numerical thresholds are frozen.

## Relationship to A21b

A21a and A21b are independent:

- **A21a:** can ProcRun retrieve useful, exact source wording with truthful source type and provenance?
- **A21b:** can ProcRun correctly interpret procurement/project status from the available evidence?

A21b is not required to make the evidence-first table useful, but A21a is a necessary quality gate for the ProcRun 2.0 product position. Passing A21a alone is not sufficient for paid public launch; all other release, safety, source and operational gates still apply.
