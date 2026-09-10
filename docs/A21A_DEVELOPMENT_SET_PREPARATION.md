# A21a evidence development-set preparation

This step creates the blind development set used to evaluate ProcRun 2.0 source-evidence retrieval.

## Hard boundaries

The builder accepts only a sanctioned source-only pool with `pii_review_status = ZERO_PII_CONFIRMED` and `engine_output_present = false`.

It must never download a raw source and then attempt to remove PII. Raw acquisition and post-hoc filtering are outside the permitted architecture.

It must never inspect evidence-retrieval output, component extraction, TED matching, or project-state labels when selecting cases or creating the adjudication package.

The sealed A21a holdout is not created or opened by this step.

## Output

Selection is deterministic and hash-anchored. Each selected case contains the sanctioned project source text and an empty blind-review block:

- `relevant_excerpts`: empty until independent adjudication
- `adjudication_status`: `PENDING_BLIND_REVIEW`

The relevant 1-3 source excerpts must later be marked directly against the source text with exact offsets. Extractor output must remain unavailable to adjudication.

## Current data availability

The repository does not currently contain the sanctioned sanitized A21 project source pool. Therefore this change deliberately adds the preparation contract and tooling but does not fabricate a benchmark dataset from test fixtures or raw public archives.

The A21a release candidate itself is now frozen separately as `a21a-evidence-rc1`; see `A21A_RELEASE_CANDIDATE_AND_FINAL_POPULATION_FREEZE.md`. The exact final population remains fail-closed until the sanctioned source pool exists and can be hash-anchored with zero development overlap.

The next data step is to make an already-sanitized, zero-PII source-only package available to an automated GitHub/server workflow, validate it, and deterministically freeze the disjoint final population before any sealed final-holdout scoring.
