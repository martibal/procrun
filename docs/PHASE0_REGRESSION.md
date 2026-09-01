# Phase-0 V1.1 regression oracle

Status date: 2026-09-01.

## Frozen source

The classification oracle is derived from the corrected Phase-0 result artifact:

`procurement_runway_phase0_result_v1_1.json`

SHA-256 of the exact source artifact used to construct the fixture:

`194c7ed3534d9c484c3b765495d25fded89a1b4e2c7bdba7373628a271f125f2`

Source specification version:

`PROCUREMENT_RUNWAY_PHASE0_RESULT_V1_1_CORRECTED`

Frozen preregistration SHA-256 retained by that artifact:

`aebfd33597697c7ad33f32e3e19a95b02c9ef683390d35ac4fa348d0fa591ef4`

The source artifact records the corrected 30-project result as 18 CLOSED, 6 OPEN, 4 PARTIAL and
2 UNRESOLVED. The correction changes `PACS-FC-04022300` from OPEN to PARTIAL without changing the
preregistration or thresholds.

## Repository fixture

`tests/fixtures/phase0_v1_1_expected.json` intentionally contains only small non-personal regression
fields:

- rank;
- operation code;
- expected project state;
- expected customer action;
- cutoff date and source hashes/versions.

Project names, narrative evidence and source-page bodies are not copied into the fixture because the
regression oracle does not require them.

Tests lock:

- exactly 30 unique ranked cases;
- 18/6/4/2 state counts;
- CLOSED -> SUPPRESS;
- OPEN -> DELIVER;
- PARTIAL -> DELIVER_COMPONENTS_ONLY;
- UNRESOLVED -> WITHHOLD;
- project aggregation semantics for every case; and
- `PACS-FC-04022300 = PARTIAL` explicitly.

## Important limitation

This is a **classification oracle**, not yet a full end-to-end replay of the original Phase-0 evidence.
It proves that the canonical project-state/output semantics cannot drift away from the corrected frozen
outcomes unnoticed. It does not prove that the current extractor and candidate matcher can reconstruct
all 30 historical decisions from raw source inputs.

A true end-to-end Phase-0 replay requires a separate, curated PII-safe normalized fixture containing the
component scopes and procurement evidence needed to exercise extraction + candidate matching. That
remains an acceptance-gate item; this oracle must not be misrepresented as completing it.
