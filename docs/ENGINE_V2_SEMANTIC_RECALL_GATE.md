# ProcRun Engine V2 — Semantic Recall Gate

Status: **ENGINE WORK ONLY — ALL NON-ENGINE PRODUCT WORK PAUSED**

## Objective

ProcRun does not resume web, translation, pricing, visual polish or release work until the core retrieval engine demonstrates that it finds a commercially credible share of real procurement-relevant project evidence.

The historical ~3% OPEN/CLOSED classification coverage is not treated as an acceptable product ceiling. Engine V2 addresses the upstream retrieval problem directly: find the relevant evidence first, then classify only what the evidence supports.

## Architecture

Engine V2 is a two-stage local retrieval system:

1. sentence-level multilingual embeddings generate a broad candidate set from exact project source text;
2. a multilingual cross-encoder reranks the candidates;
3. every returned candidate remains an exact span from the approved source document;
4. semantic similarity is a retrieval/ranking signal only — it never rewrites source text and never becomes customer-facing evidence by itself;
5. final OPEN/CLOSED/UNRESOLVED logic remains downstream and fail-closed.

Default local models:

- embedding: `intfloat/multilingual-e5-small`
- reranker: `cross-encoder/mmarco-mMiniLMv2-L12-H384-v1`

No project text may be sent to a hosted inference API. Model inference is local to ProcRun infrastructure.

## Separation of thresholds

The broad candidate-generation threshold is an engineering tuning parameter, not a product-quality threshold. It should favor recall.

The final customer-visible acceptance threshold must be calibrated from a clean development set and then frozen before the final holdout is opened. The invalidated historical A21a v1 threshold set must not be reused as if it were a clean preregistration.

## Mandatory benchmark dimensions

Before Engine V2 can be promoted, the clean benchmark must report at minimum:

- positive-case recall;
- gold-excerpt recall;
- candidate precision;
- negative-case false-positive rate;
- exact-span integrity failures;
- determinism failures;
- candidate volume per project and runtime cost.

The benchmark must preserve the existing zero-PII and source-lineage requirements.

## Product stop rule

Until the engine benchmark is commercially credible, the following are paused:

- further customer-web feature work;
- translation UI;
- pricing implementation;
- marketing polish;
- production launch work.

Only work that improves, measures or safely supplies the retrieval engine is in scope.

## Promotion rule

Engine V2 is promoted only after:

1. a clean, admissible development benchmark exists;
2. retrieval parameters are tuned on that development set;
3. release thresholds are frozen after development tuning and before final evaluation;
4. a disjoint final population is hash-frozen;
5. the final evaluation meets the frozen release gate.

The commercial question is explicit: ProcRun must demonstrate that the small result set is a high-recall reduction of the real opportunity universe, not merely a low-recall subset.
