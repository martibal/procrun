# A21a — title + specific-objective fallback decision

**Status:** DEVELOPMENT DECISION — SOURCE CONTEXT ONLY, NOT FINAL A21a GO/NO-GO

## Question

For the 14 frozen A21a development cases where the exact project title was previously judged `NOT_USEFUL`, does adding the exact OpenCoesione `specific objective` make the source wording sufficiently informative to explain the funded intervention?

## Blind development result

The review used the previously frozen source-only 14-case artifact with canonical SHA-256:

`d014391f1e6f0f4e10bc0041352a4ea15fb12e4fe03cc974d31709a2c0dee02b`

The parent 60-case development sample remains:

`f214a0ee54bec0de8ef67d29707e18562fee582db57c60448b7014841e8e0b37`

Result:

- `CLEAR`: 0 / 14
- `PARTIAL`: 6 / 14
- `NOT_USEFUL`: 8 / 14

No classification, matching, procurement-state or evidence-retrieval output was used. No new source field was received. The sealed A21/A21b holdout was not touched.

## Decision

`Specific objective` is **not an acceptable fallback source-evidence surface** for weak project titles.

It is programme-level context. It can explain the broad funding objective, but this development sample shows that it does not recover any of the 14 weak-title cases to a `CLEAR` explanation of the actual funded intervention.

Therefore:

1. ProcRun must not replace, rewrite or augment a weak project title with `specific objective` and present the combination as if it were richer project documentation.
2. `Specific objective` may remain ordinary source metadata / programme context if the product later exposes it, but it must be labelled as such and remain separate from project source evidence.
3. The customer-facing project evidence remains the exact `Project title` when that is the strongest approved wording available.
4. A weak title must not be upgraded to `Project description` merely because programme metadata exists.
5. If ProcRun requires richer wording for a weak-title row, that wording must come from a separately qualified source that supplies project-specific text under the zero-PII and provenance contract.

## Consequence for source architecture

The currently approved OpenCoesione PR FESR Lombardia operation-list route does not contain a richer project-specific fallback for these cases: the live `SINTESI_PROG` surface is identical to the title in the current logical universe, `specific objective` is too broad, and `intervention category` was absent for all 14 weak-title cases in the development probe.

Existing previously examined alternatives remain closed under their recorded gates: the general OpenCoesione project API and project-search export admit disallowed identity surfaces; OpenBDAP MOP did not establish the required project-specific verbatim evidence surface; Regione Lombardia Socrata did not establish an equivalent source-specific free-text safety rule.

Accordingly, **the next source step is not another title/objective diagnostic**. It is qualification of a genuinely richer project-specific source under the existing zero-PII, no-contact and provenance rules, but only if the final A21a quality threshold requires richer wording for weak-title cases.

## Product rule while that qualification is unresolved

ProcRun remains truthful rather than synthetic:

- show the exact project title as `Project title`;
- do not invent a description;
- do not treat programme objective as project evidence;
- keep ProcRun interpretation separate;
- do not infer procurement status from source wording alone.

This development result does not itself define the final numerical A21a acceptance threshold. That threshold must still be preregistered before final holdout evaluation.
