# A21 gold-standard execution runbook

Status: **IMPLEMENTED SCAFFOLD — EMPIRICAL ADJUDICATION NOT YET COMPLETE**

Authoritative gate: `docs/CLASSIFICATION_ENGINE_VALIDATION_GATE.md`.

This runbook turns the A21 specification into a reproducible workflow while preserving the blind-evaluation rule.

## 1. Export the raw qualifying project universe

Run only the approved OpenCoesione FundingProject route. This command does not run component extraction, TED matching or classification:

```bash
python scripts/export_a21_project_universe.py \
  --output artifacts/a21/funding-project-universe.jsonl
```

Record the printed `funding_projects`, source hash and universe hash in the validation record.

The JSONL is intentionally raw `FundingProject` data. Any row containing classifier state, extracted components or procurement-match output is rejected by the strict `FundingProject` schema and must not enter the blind gold workflow.

## 2. Build a blind screening pool before the final benchmark

The authoritative release gate requires the final benchmark to be explicitly stratified. A plain SHA-ranked sample is not sufficient as the final product-validation benchmark because it cannot guarantee coverage of supported domains, component counts, procurement situations, ambiguity, expected `UNRESOLVED`, description precision, geography, size and time-period strata.

A deterministic SHA-ranked sample may be frozen as a **screening pool only**. It must not be described as the final release-gate benchmark until independent stratum labels have been established.

The screening process must remain blind to ProcRun engine output. For every screening project, independently record:

- supported component domain(s);
- short/long scope band;
- zero-component / one-component / multi-component / ambiguous-component-count band;
- known procurement / no relevant TED procurement found / ambiguous candidate band;
- independently expected project state, including `UNRESOLVED` where justified;
- geography;
- project-size band;
- time-period band;
- high/low description-precision band;
- written rationale.

`ZERO` is required when no defensible purchasable component can be established from the public project scope. `AMBIGUOUS` is required when the public scope does not support a defensible exact component count. Neither condition may be coerced into `ONE` or `MULTI` merely to satisfy benchmark selection.

These records are validated by `src/procrun/classification_stratification.py`.

If the current screening pool cannot cover every mandatory stratum, expand the screening pool deterministically from the frozen qualifying universe and continue independent screening. Do not weaken, synthesize or infer a missing stratum from engine output.

## 3. Freeze the final stratified general benchmark

Only after the screening register is complete enough to satisfy the authoritative strata may the final 200-project benchmark be selected.

The selector must:

- use only independently produced stratification records;
- cover every supported component domain;
- include short and long scope descriptions;
- include zero-component, one-component, multi-component and ambiguous-component-count cases;
- include known procurement, no-relevant-TED-found and ambiguous-candidate cases;
- include expected `UNRESOLVED` cases;
- include multiple geographies, project-size bands and time bands;
- include both high-precision and low-precision descriptions;
- fill remaining slots deterministically using an immutable seed;
- fail closed when any required stratum is absent.

At least 25% of the final benchmark must be a disjoint holdout selected only after the final stratified population is fixed. Holdout membership must not be exposed during adjudication or rule tuning.

The final benchmark manifest embeds the exact raw `FundingProject` records and exposes a canonical SHA-256 so source text, cutoff and project identity cannot drift silently.

## 4. Blind gold adjudication

For every project in the final stratified benchmark, adjudicate from already-public, independently inspectable material only:

- purchasable components;
- exact verbatim component source span and offsets;
- relevant and explicitly rejected procurement evidence;
- publication date and public source URL;
- component state;
- project state;
- written rationale.

Do not inspect ProcRun classifier output while establishing the gold answer. No outreach, interview, source-owner contact, authority contact, customer contact or external human response may be used to resolve a case.

A conservative `UNRESOLVED` gold state is valid where the public record does not justify OPEN or CLOSED.

## 5. Complete and freeze the machine-readable gold file

Before freezing, remove helper display-only fields (`project_title`, `project_scope_text`, `region`, `municipality`, `source_url`) and the top-level `instructions` field from the working file. Each case must then conform to the strict `GoldTemplate` schema in `src/procrun/classification_gold.py`.

The freeze validator rejects, among other things:

- missing/duplicate benchmark cases;
- non-verbatim component evidence spans;
- CLOSED without accepted procurement evidence;
- OPEN with accepted procurement evidence;
- accepted post-cutoff evidence used to close a component;
- project state inconsistent with component aggregation;
- a gold file tied to a different manifest hash.

Freeze with:

```bash
python scripts/prepare_a21_gold.py freeze \
  --manifest artifacts/a21/benchmark-manifest.json \
  --completed-gold artifacts/a21/gold-completed.json \
  --output artifacts/a21/gold-frozen.json
```

The command prints `package_sha256`. Record the manifest hash and frozen package hash before scoring the release-candidate engine.

## 6. Dedicated OPEN safety population

The general 25% holdout is not the false-OPEN safety population.

After the release-candidate engine version is frozen, run it over the complete production-validation universe and capture every project it classifies `OPEN`. Every one of those OPEN-classified cases must be independently adjudicated before the false-OPEN gate can pass.

No OPEN case may be silently dropped because it is inconvenient, ambiguous or outside the 200-project general benchmark.

The A21 gate remains closed unless:

- the dedicated OPEN population is complete;
- observed false OPEN count is zero; and
- all other hard thresholds in `CLASSIFICATION_ENGINE_VALIDATION_GATE.md` pass.

## 7. Separation from engine tuning

The final benchmark manifest, holdout IDs, metric definitions and gold answers must be frozen before release-candidate scoring. If a gold record itself is later proven wrong, the correction must be versioned and hash-anchored with a written reason.

A gold correction must never be made merely because the engine disagrees with it.

If the same causal mechanism produces false OPEN in two separately frozen rounds, A21 requires that mechanism to be retired from OPEN-producing use and affected cases to fail closed to `UNRESOLVED` until a newly versioned mechanism passes fresh validation.

## Round-001 note

The SHA-ranked 200-project population frozen on 2026-09-09 before this correction remains useful as a blind screening pool. Because it was selected without explicit stratum metadata, it is **not the final authoritative A21 release-gate benchmark**. No engine scoring performed against that screening pool may be used as final product-validation evidence.
