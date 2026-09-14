# Engine V2 candidate freeze — RC1

Status: **FROZEN BEFORE FINAL HOLDOUT CONTENT INSPECTION**

Candidate id: `engine-v2-rc1`

This file freezes the relevance engine that may be evaluated on the disjoint final holdout. No engine, threshold, label or noise-rule change is permitted after final-holdout source content is inspected without creating a new candidate and a new untouched holdout.

## Frozen development evidence

- clean blind development sample canonical SHA-256: `8013c9f96c2988d5a0cdd80189c9e66636b43ea3b62c43b5444ec56181b955a7`
- development cases: 200
- clear positive cases: 59
- clear negative cases: 131
- ambiguous cases excluded from training/calibration: 10
- adjudication occurred source-only before Engine V2 output inspection
- frozen development labels: `data/engine_v2/clean_dev_labels_v1.json`

## Frozen model and inference contract

1. Input text is `project_title + "\n" + project_scope_text` from the sanctioned zero-PII source pool.
2. Embedding model: `intfloat/multilingual-e5-small`, passage encoding, normalized embeddings.
3. Relevance classifier: scikit-learn `LogisticRegression` with:
   - `C=1.0`
   - `class_weight="balanced"`
   - `max_iter=4000`
   - `solver="liblinear"`
   - `random_state=20260912`
4. Final candidate training uses all 190 clear development cases and excludes all 10 ambiguous cases.
5. Deterministic noise rejection is exactly the implementation in `scripts/benchmark_engine_v2_relevance_gate.py` at candidate code commit `85bba3427b34615243531a5f87526e5911b3ff89`.
6. Frozen probability threshold: **0.48335432**. A case is relevant only when it is not rejected by the deterministic noise gate and its classifier probability is greater than or equal to this threshold.
7. Relevant cases are then passed to the exact-span semantic evidence retriever; semantic similarity is never customer evidence by itself.
8. Customer-visible evidence must remain an exact source span with exact offsets.

## Clean development result that justified freezing

At the frozen threshold under 5-fold stratified out-of-fold development scoring plus the deterministic noise gate:

- TP: 57
- FP: 1
- FN: 2
- TN: 130
- recall: **96.6102%**
- precision: **98.2759%**
- negative-case false-positive rate: **0.7634%**
- F1: **97.4359%**
- noise-gate rejected positives: **0**
- noise-gate rejected negatives: **101**

Benchmark workflow run: `34689810209`  
Artifact: `10296792449`  
Artifact digest: `sha256:65f8a80d22155e4cf7453ef8fcedd337d298ef8eb172f01309d1892b908fc78b`

These are development results, not product claims. Product-quality claims require the untouched disjoint final holdout.

## Final-holdout decision rule

Before final holdout scoring, the holdout population and blind adjudication must be frozen with hashes and zero overlap with the 200 development cases.

RC1 is commercially acceptable only if the disjoint final holdout demonstrates all of the following:

- case-level recall >= 0.90;
- case-level precision >= 0.90;
- exact source-span integrity failures = 0;
- PII violations = 0;
- source/provenance violations = 0;
- deterministic rerun mismatch = 0.

The commercial target remains >=0.95 recall and >=0.95 precision. A result between the hard gate and target is not sufficient to resume non-engine product work without an explicit product decision.
