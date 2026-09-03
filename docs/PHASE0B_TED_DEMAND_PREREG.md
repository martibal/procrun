# Phase 0B — TED embedded-demand preregistration

Status: PREREGISTERED BEFORE LIVE CI EXECUTION
Date: 2026-09-03

## Purpose

ProcRun v2 is a different commercial mechanism from the original funded-project runway product. This test does not reuse the old Phase 0 result as evidence for v2. It tests whether already-published Portugal TED infrastructure notices contain enough structured, supplier-relevant demand below the notice level to justify a dedicated product surface.

## Frozen hypothesis

`published TED notice -> purchasable requirements -> structured product demand`

The test is deliberately narrower than a customer willingness-to-pay study. It asks whether the source material contains an empirically useful requirement layer that is not reducible to title/CPV filtering.

## Frozen population and transport

- official TED Search API only;
- Portugal notices published on/after 2025-09-03;
- exact pre-receipt field allowlist only;
- `scope=ALL`;
- `checkQuerySyntax=false`;
- ITERATION pagination;
- infrastructure CPV prefixes: 31, 34, 42, 44, 45, 90;
- active/later notice types use the frozen set from the TED foundation qualification;
- first 300 qualifying active/later infrastructure records encountered after deterministic API pagination form the evaluation sample;
- if fewer than 200 qualifying records are obtained within eight 250-record pages, the test fails.

No raw notice body, title or description is logged or persisted by the qualification script.

## Frozen extraction mechanism

The existing deterministic `component_engine.RULES` taxonomy is used unchanged. A requirement is counted only when an existing frozen phrase occurs in title or procedure description. No LLM, semantic expansion or post-hoc taxonomy additions are permitted during this test.

This makes the test conservative: it measures what the already-built deterministic layer can extract from TED today, not what a future model might infer.

## Frozen metrics

For each sampled notice calculate unique matched `(domain, category)` requirements.

1. `any_requirement_pct` — share with at least one extracted requirement.
2. `multi_requirement_pct` — share with at least two distinct requirements.
3. `description_only_value_pct` — share containing at least one requirement found in description but not title. This tests whether scope decomposition adds information beyond headline matching.
4. `cpv_blind_value_pct` — share containing at least one text-supported requirement whose rule CPV prefixes are absent from the notice CPV list. This tests whether structured text extraction adds information beyond CPV filtering.
5. `distinct_categories` — unique requirement categories observed across the sample.
6. `domains_represented` — unique component domains observed.

## Frozen GO thresholds

All must pass:

- sample size >= 200;
- `any_requirement_pct >= 20.0`;
- `description_only_value_pct >= 10.0`;
- `cpv_blind_value_pct >= 5.0`;
- `distinct_categories >= 8`;
- `domains_represented >= 3`.

`multi_requirement_pct` is diagnostic and has no GO threshold.

## Interpretation

PASS means the TED corpus contains a non-trivial, structured demand layer that is empirically richer than title/CPV filtering under the existing conservative taxonomy. It does not prove uniqueness, willingness to pay or precision of every future inferred requirement.

FAIL means ProcRun must not proceed to a full website build on the current v2 promise without another explicit product decision.

Competitive and buyer-mass checks are documented separately and must be read together with this live gate before declaring WEBSITE_BUILD_READY.