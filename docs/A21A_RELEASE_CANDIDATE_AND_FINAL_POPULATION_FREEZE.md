# A21a — Release Candidate and Final Population Freeze

**Status:** RELEASE CANDIDATE FROZEN; FINAL POPULATION BLOCKED PENDING SANITIZED SOURCE POOL

## Frozen release candidate

The A21a evidence retriever is frozen as:

- release candidate: `a21a-evidence-rc1`
- extractor version: `evidence-retrieval-v1`
- baseline commit: `49e6345e514f85fe2e5b5f58076efe3f7dba85dc`
- `src/procrun/evidence_retrieval.py` Git blob SHA: `d077a919d91f2049ced6546e585ff0e651c81dd7`
- threshold preregistration: `a21a-thresholds-v1`

Any change to the evidence retriever or the preregistered A21a threshold contract creates a new candidate and invalidates this RC identity for final-holdout evaluation.

## Final evaluation population

The exact final population is **not yet frozen** because the repository still lacks the sanctioned remote `a21a-sanitized-source-pool-v1` required by `A21A_SANITIZED_SOURCE_INGRESS.md`. ProcRun must not fabricate a final population from unit-test fixtures, development-review material, raw archives or blocked source families.

Before the final population may be marked frozen, one immutable manifest must record all of the following:

- SHA-256 of the sanctioned source-only pool;
- SHA-256 of the complete selected final-population document;
- SHA-256 of the canonically ordered final case-ID list;
- exact case count;
- development-overlap count, which must equal `0`;
- confirmation that all input satisfied `ZERO_PII_CONFIRMED`, `engine_output_present = false`, `raw_archive_present = false`, `download_then_filter_used = false`, and `source_only_projection_confirmed = true`;
- confirmation that gold adjudication was produced blind to extractor output;
- `frozen = true` only after every field above has been populated and independently reproducible.

Selection must be deterministic from the sanctioned pool and must represent the production universe across wording utility, ambiguity, project/domain mix and the source structures actually admitted to production. No sealed final material may be inspected to tune selection.

## Machine guard

`procrun.a21a_release_freeze.require_final_holdout_ready()` fails closed while the final-population manifest is incomplete or has any development overlap. The default checked-in state deliberately remains blocked.

## Current gate

- Thresholds: **FROZEN**
- Evidence release candidate: **FROZEN**
- Final evaluation population: **NOT FROZEN — MISSING SANCTIONED SANITIZED SOURCE POOL**
- Sealed A21a holdout access/scoring: **BLOCKED**
- A21a product gate: **NOT YET GREEN**

The next data action is therefore not to open the holdout. It is to supply or recover an approved remote sanitized source-only pool, validate it, derive the exact disjoint final population deterministically, and freeze its hashes before any final scoring occurs.
