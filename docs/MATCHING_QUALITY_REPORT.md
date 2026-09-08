# ProcRun matching quality report

This file is append-only by validation run. Historical measurements remain visible even when later code fixes improve the result.

The locked Phase M thresholds and continuation rule are defined in `docs/PHASE_M_MATCHING_VALIDATION.md`.

## 2026-09-08 — production UNRESOLVED audit before reclassification

**Purpose:** Part A baseline against the actual central production assessment ledger.

**Context:** this snapshot was produced before the production corpus was reclassified with the fix that separates a real project-title match from a geography-only match. The result is intentionally retained as the pre-fix baseline.

### Exact SQL

```sql
\pset tuples_only on
\pset format unaligned

\echo === UNRESOLVED rationale counts ===
WITH latest AS (
    SELECT DISTINCT ON (component_id)
        component_id,
        state,
        rationale,
        matching_candidates,
        cutoff_date,
        as_of,
        inserted_at,
        version_id
    FROM procrun.assessment_versions
    ORDER BY component_id, cutoff_date DESC, as_of DESC, inserted_at DESC, version_id DESC
)
SELECT count(*)::text || E'\t' || rationale
FROM latest
WHERE state = 'UNRESOLVED'
GROUP BY rationale
ORDER BY count(*) DESC, rationale;

\echo === REVIEW candidate tier/reason counts ===
WITH latest AS (
    SELECT DISTINCT ON (component_id)
        component_id,
        state,
        rationale,
        matching_candidates,
        cutoff_date,
        as_of,
        inserted_at,
        version_id
    FROM procrun.assessment_versions
    ORDER BY component_id, cutoff_date DESC, as_of DESC, inserted_at DESC, version_id DESC
), review_rows AS (
    SELECT jsonb_array_elements(matching_candidates) AS candidate
    FROM latest
    WHERE state = 'UNRESOLVED'
      AND rationale = 'A pre-cutoff procurement candidate is in the review band; OPEN is prohibited.'
)
SELECT
    count(*)::text || E'\t' ||
    coalesce(candidate->>'tier', '<missing>') || E'\t' ||
    coalesce(candidate->>'reason', '<missing>')
FROM review_rows
WHERE candidate->>'disposition' = 'REVIEW'
GROUP BY candidate->>'tier', candidate->>'reason'
ORDER BY count(*) DESC, candidate->>'tier', candidate->>'reason';

\echo === REVIEW deterministic feature signatures ===
WITH latest AS (
    SELECT DISTINCT ON (component_id)
        component_id,
        state,
        rationale,
        matching_candidates,
        cutoff_date,
        as_of,
        inserted_at,
        version_id
    FROM procrun.assessment_versions
    ORDER BY component_id, cutoff_date DESC, as_of DESC, inserted_at DESC, version_id DESC
), review_rows AS (
    SELECT jsonb_array_elements(matching_candidates) AS candidate
    FROM latest
    WHERE state = 'UNRESOLVED'
      AND rationale = 'A pre-cutoff procurement candidate is in the review band; OPEN is prohibited.'
)
SELECT
    count(*)::text || E'\t' ||
    'tier=' || coalesce(candidate->>'tier','?') || E'\t' ||
    'project_id=' || coalesce(candidate#>>'{features,exact_project_identifier}','?') || E'\t' ||
    'geo=' || coalesce(candidate#>>'{features,geography_match}','?') || E'\t' ||
    'scope=' || coalesce(candidate#>>'{features,high_scope_overlap}','?') || E'\t' ||
    'cpv=' || coalesce(candidate#>>'{features,cpv_or_category_match}','?') || E'\t' ||
    'date=' || coalesce(candidate#>>'{features,compatible_date_window}','?') || E'\t' ||
    'title_or_location=' || coalesce(candidate#>>'{features,project_title_or_location_match}','?')
FROM review_rows
WHERE candidate->>'disposition' = 'REVIEW'
GROUP BY
    candidate->>'tier',
    candidate#>>'{features,exact_project_identifier}',
    candidate#>>'{features,geography_match}',
    candidate#>>'{features,high_scope_overlap}',
    candidate#>>'{features,cpv_or_category_match}',
    candidate#>>'{features,compatible_date_window}',
    candidate#>>'{features,project_title_or_location_match}'
ORDER BY count(*) DESC;

\echo === REVIEW candidates per unresolved component ===
WITH latest AS (
    SELECT DISTINCT ON (component_id)
        component_id,
        state,
        rationale,
        matching_candidates,
        cutoff_date,
        as_of,
        inserted_at,
        version_id
    FROM procrun.assessment_versions
    ORDER BY component_id, cutoff_date DESC, as_of DESC, inserted_at DESC, version_id DESC
), per_component AS (
    SELECT
        component_id,
        count(*) FILTER (WHERE candidate->>'disposition' = 'REVIEW') AS review_count
    FROM latest
    CROSS JOIN LATERAL jsonb_array_elements(matching_candidates) AS candidate
    WHERE state = 'UNRESOLVED'
      AND rationale = 'A pre-cutoff procurement candidate is in the review band; OPEN is prohibited.'
    GROUP BY component_id
)
SELECT
    count(*)::text || E'\t' || bucket
FROM (
    SELECT CASE
        WHEN review_count = 1 THEN '1 review candidate'
        WHEN review_count BETWEEN 2 AND 5 THEN '2-5 review candidates'
        WHEN review_count BETWEEN 6 AND 20 THEN '6-20 review candidates'
        ELSE '21+ review candidates'
    END AS bucket
    FROM per_component
) grouped
GROUP BY bucket
ORDER BY
    CASE bucket
        WHEN '1 review candidate' THEN 1
        WHEN '2-5 review candidates' THEN 2
        WHEN '6-20 review candidates' THEN 3
        ELSE 4
    END;
```

### Complete output

```text
Auditing current UNRESOLVED states using aggregate counts only...
Output format is unaligned.
=== UNRESOLVED rationale counts ===
75      A pre-cutoff procurement candidate is in the review band; OPEN is prohibited.
8       Component boundary is ambiguous; false-OPEN protection requires withholding.
=== REVIEW candidate tier/reason counts ===
75      C       Tier C evidence is corroborated but remains in review until a CLOSED threshold is explicitly frozen
=== REVIEW deterministic feature signatures ===
75      tier=C  project_id=false        geo=true        scope=true      cpv=true        date=true       title_or_location=true
=== REVIEW candidates per unresolved component ===
75      1 review candidate
```

### Result interpretation

The UNRESOLVED population was overwhelmingly dominated by one implementation pattern: 75 of 83 current UNRESOLVED components had a single Tier C review candidate with no exact project identifier and a geography match. The candidate feature builder was subsequently corrected so geography alone can no longer also satisfy `project_title_or_location_match`.

This baseline does **not** establish post-fix quality. A new Part A audit is required after production reclassification.

### Phase M B/C status at this snapshot

Human precision/false-negative validation is **not yet complete**. No public matching-accuracy claim is authorized from this report section.

The current product snapshot showed no CLOSED components in the customer-facing current-state set. Therefore the pre-registered requirement of at least 30 current production CLOSED cases cannot be satisfied from this snapshot. Phase M treats this as a validation-data availability gate, not as a reason to terminate ProcRun: the project continues under the remediation/retest rule until a qualifying CLOSED population exists or a materially different validation design is pre-registered before inspecting outcomes.