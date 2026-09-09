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

## 2. Freeze the general benchmark selection before adjudication

Use an explicit immutable seed and cutoff date:

```bash
python scripts/prepare_a21_gold.py prepare \
  --projects-jsonl artifacts/a21/funding-project-universe.jsonl \
  --cutoff YYYY-MM-DD \
  --seed a21-round-001 \
  --manifest artifacts/a21/benchmark-manifest.json \
  --template artifacts/a21/gold-working-template.json
```

Selection is deterministic SHA-256 ranking over `operation_code`. The manifest contains 200 real projects when at least 200 are available; otherwise it contains the entire qualifying universe. A disjoint holdout of at least 25% is selected by a separate deterministic hash namespace.

The manifest embeds the exact raw FundingProject records and exposes `manifest_sha256`, so the source text, cutoff, project IDs and holdout membership cannot drift silently.

## 3. Blind adjudication

The working template deliberately contains no ProcRun engine component, match or state output.

For every selected project, adjudicate from already-public, independently inspectable material only:

- purchasable components;
- exact verbatim component source span and offsets;
- relevant and explicitly rejected procurement evidence;
- publication date and public source URL;
- component state;
- project state;
- written rationale.

Do not inspect ProcRun classifier output while establishing the gold answer. No outreach, interview, source-owner contact, authority contact, customer contact or external human response may be used to resolve a case.

A conservative `UNRESOLVED` gold state is valid where the public record does not justify OPEN or CLOSED.

## 4. Complete the machine-readable gold file

Before freezing, remove the helper display-only fields (`project_title`, `project_scope_text`, `region`, `municipality`, `source_url`) and the top-level `instructions` field from the working file. Each case must then conform to the strict `GoldTemplate` schema in `src/procrun/classification_gold.py`.

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

The command prints `package_sha256`. Commit the manifest hash and frozen package hash before scoring the release-candidate engine.

## 5. Dedicated OPEN safety population

The general 25% holdout is not the false-OPEN safety population.

After the release-candidate engine version is frozen, run it over the complete production validation universe and capture every project it classifies `OPEN`. Every one of those OPEN-classified cases must be independently adjudicated before the false-OPEN gate can pass.

No OPEN case may be silently dropped because it is inconvenient, ambiguous or outside the 200-project general benchmark.

The A21 gate remains closed unless:

- the dedicated OPEN population is complete;
- observed false OPEN count is zero; and
- all other hard thresholds in `CLASSIFICATION_ENGINE_VALIDATION_GATE.md` pass.

## 6. Separation from engine tuning

The benchmark manifest, holdout IDs, metric definitions and gold answers must be frozen before release-candidate scoring. If a gold record itself is later proven wrong, the correction must be versioned and hash-anchored with a written reason.

A gold correction must never be made merely because the engine disagrees with it.

If the same causal mechanism produces false OPEN in two separately frozen rounds, A21 requires that mechanism to be retired from OPEN-producing use and affected cases to fail closed to `UNRESOLVED` until a newly versioned mechanism passes fresh validation.
