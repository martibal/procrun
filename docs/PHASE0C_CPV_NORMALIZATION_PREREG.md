# Phase 0C — disjoint confirmation of CPV-normalization value

Status: PREREGISTERED BEFORE LIVE EXECUTION
Date: 2026-09-03

## Why this test exists

Phase 0B failed its description-only gate and therefore did not validate the original v2 framing. It did, however, reveal a strong post-hoc signal: text-supported purchasable requirements were frequently absent from the corresponding notice CPV classification.

This Phase 0C test treats that as a **new hypothesis** and confirms it on a disjoint historical Portugal population. No Phase 0B threshold is retroactively changed.

## Frozen hypothesis

`TED notice text -> normalized purchasable requirement taxonomy` adds material supplier-facing information beyond CPV filtering alone.

The product claim tested here is not "ProcRun discovers hidden needs that are absent from the notice title." The tested claim is that ProcRun turns notice text into a structured, supplier-usable product-demand layer that CPV codes alone do not represent.

## Frozen disjoint population

- Portugal TED notices only;
- publication dates 2024-09-03 through 2025-09-02 inclusive;
- this period does not overlap the Phase 0B period beginning 2025-09-03;
- same safe pre-receipt field projection and privacy rules;
- same infrastructure CPV prefixes and later/active notice-type set;
- same unchanged deterministic `component_engine.RULES` taxonomy;
- first 300 qualifying records after deterministic ITERATION pagination;
- minimum valid sample 200 records;
- maximum eight pages of 250 records.

No raw notice text is logged or persisted.

## Frozen confirmation metrics and gates

All gates must pass:

- sample size >= 200;
- at least one normalized requirement in >= 20.0% of notices;
- CPV-blind requirement value in >= 12.0% of notices;
- at least 15 distinct normalized categories;
- all five existing infrastructure domains represented.

`description_only_value_pct` and `multi_requirement_pct` remain diagnostic only and cannot rescue or fail this hypothesis.

## Meaning of CPV-blind value

A notice counts as CPV-blind-value positive when the frozen phrase rules identify a requirement in title or description, that rule has one or more CPV prefixes, and none of those rule CPV prefixes occur in the notice's own CPV list.

This is intentionally stricter than saying the notice is semantically relevant: it demonstrates that the structured requirement layer can expose a product category that would not be obtained by simply filtering the notice on the component rule's CPV family.

## Decision rule

PASS allows ProcRun to proceed to website build only under the narrower positioning documented after the result: **structured public-procurement product demand, normalized from notice text, not hidden pre-tender discovery.**

FAIL closes the current TED-based ProcRun v2 mechanism as a build candidate.