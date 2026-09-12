# ProcRun Readiness Dossier v2 — frozen non-visual contract

## Product role

ProcRun structures a source-linked pre-application readiness review. It does not act as a public
authority, legal adviser, grant evaluator, or automatic qualification engine.

The paid dossier combines three independent surfaces:

1. **Historical dimensioning** — deterministic descriptive comparison with funded projects.
2. **Published requirements matrix** — exact, source-linked requirements from the selected source package.
3. **Points requiring professional verification** — source-linked items the adviser must assess; ProcRun records only the adviser status.

## Absolute language boundaries

Customer-facing ProcRun-generated output must not:

- state `ELIGIBLE` or `INELIGIBLE`;
- describe the product as a `complete verifica preliminare`;
- claim that ProcRun has approved, assessed or certified DNSH, PMI consolidation, ATECO interpretation or another discretionary/professional requirement;
- provide an approval probability, funding recommendation or proof of formal cost congruity.

Verbatim public-source text is evidence and is not rewritten merely because an official document uses
one of these terms. Source quotation and ProcRun conclusion must remain visibly separate.

## Invariants

### RD-1 — Integrity is not correctness or completeness

SHA-256 identifies the exact source package and benchmark snapshot used. It does not prove that a
human source extraction was legally correct or complete. Every source package therefore carries an
explicit completeness attestation in addition to cryptographic integrity.

### RD-2 — Completion is not a verdict

The product may state that listed checks have been addressed or confirmed by the adviser. It may not
turn checklist completion into a qualification, readiness, compliance or approval verdict.

### RD-3 — Seven-day source TTL

An active source package is fresh for at most seven calendar days from `verified_at`. After that it is
`SOURCE_REFRESH_REQUIRED` and a new paid dossier cannot be generated. Manual invalidation takes
effect immediately and overrides the remaining TTL.

A refresh creates a new immutable source-package version. Existing versions are never overwritten.
The seven-day TTL is a maximum age policy, not a statement that the official source cannot change
inside the window.

### RD-4 — Exact source package

Each package contains the official bando source set used for the matrix: relevant bando, allegati,
known rectifications and relevant official FAQs as applicable. Every published requirement references
an exact document and citation and preserves the source wording needed to audit the extraction.

### RD-5 — Mechanical checks are narrow factual comparisons

Automation is permitted only where the package declares an objective integer boundary and its scope.
The result states the user value relative to that published boundary. It never converts the comparison
into a broader qualification decision.

### RD-6 — Professional judgment stays with the adviser

Discretionary or context-dependent requirements are represented as adviser confirmations or points
requiring professional verification. ProcRun does not infer them from company/project text and does
not access external company/person registries.

Advisor confirmations are structured enum values only. No free-text note field exists in the dossier
contract, preventing customer-entered PII from entering the readiness data plane.

### RD-7 — Historical cohort is explicit and immutable

A source package binds to one `benchmark_cohort_id`. Cohort membership comes from an already-qualified
structured source and is frozen in the benchmark snapshot. ProcRun does not infer bando/action
membership from project titles, text similarity, geography, timing or fuzzy matching.

The benchmark snapshot binds both the admitted funded-project facts and the structured membership
source through source hashes.

### RD-8 — Historical sample governance

Funding and duration have independent sample sizes.

- `n >= 30`: full benchmark — median, Q1, Q3, P90, right-ECDF position and comparables;
- `15 <= n < 30`: descriptive only — median, min/max and comparables, no percentile/quartile claims;
- `n < 15`: reference only — actual observations, no statistical summary beyond sample count inside the paid dossier.

The pre-payment preview never exposes exact `n`, median, percentile, distribution values or comparable names.

### RD-9 — Funding and duration contracts

Funding is the canonical `FundingProject.approved_funding_eur`, sourced from
`CostoAmmesso_TotalEligibleExpenditure` and conservatively truncated to whole euros by the frozen
OpenCoesione collector. No fallback to total project cost is permitted.

Duration is completed calendar months. Missing dates and end-before-start fail closed for the duration
variable and never impute a replacement.

### RD-10 — Comparable determinism

Funding position uses the right empirical CDF `P(x)=#{Xi<=x}/n`; ties receive the same position.
The joint comparable ranking, when duration has sufficient descriptive coverage, uses the frozen
70/30 position-distance contract: 70% funding ECDF distance and 30% duration ECDF distance. Projects
without a valid duration do not compete in the joint ranking. Funding-only comparables remain a
separate list.

### RD-11 — Immutable paid dossier

A paid dossier binds:

- opaque tenant key;
- opaque trusted purchase reference;
- exact source package ID/version/hash and source manifest;
- exact benchmark snapshot ID/hash and data-through date;
- project funding/duration inputs;
- structured adviser confirmations;
- full generated matrix and historical analysis;
- canonical bytes and SHA-256.

Dossiers, source packages, invalidation events, benchmark snapshots and cohort memberships are
append-only.

## Paywall contract

The free preview says only whether historical analysis is available, limited-reference only, or blocked
because the source package is not fresh. The paid dossier is where exact sample size, statistics and
comparables are revealed.

`purchase_reference` is an opaque trusted billing-boundary assertion. ProcRun's readiness data plane
does not collect or store customer billing identity. A merchant integration must terminate outside
this zero-PII readiness boundary and provide only the opaque purchase assertion.

## GO / NO-GO

**GO:** deterministic benchmark; source-linked matrix; exact mechanical boundary comparisons; adviser
self-attestation; professional-verification list; immutable source/version provenance; seven-day
fail-closed TTL; leak-free preview; immutable paid dossier.

**NO-GO:** automatic eligibility verdict; generic risk engine; inferred rejection reasons; automated
technical/strategic judgment; fuzzy cohort assignment; external person/company lookup; arbitrary
customer free text; claims of complete preliminary verification, compliance certification or approval
prediction.
