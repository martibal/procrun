param(
    [string]$Server = "62.238.117.62",
    [string]$SshUser = "root"
)

$ErrorActionPreference = "Stop"
$SshKey = Join-Path $env:USERPROFILE ".ssh\procrun_hetzner"

if (-not (Test-Path $SshKey)) {
    throw "Missing SSH key: $SshKey"
}

$sql = @'
\pset tuples_only on
\pset format unaligned

\echo === CURRENT latest component states ===
WITH latest AS (
    SELECT DISTINCT ON (component_id)
        component_id, state, matching_candidates, cutoff_date, as_of, inserted_at, version_id
    FROM procrun.assessment_versions
    ORDER BY component_id, cutoff_date DESC, as_of DESC, inserted_at DESC, version_id DESC
)
SELECT state || E'\t' || count(*)::text
FROM latest
GROUP BY state
ORDER BY state;

\echo === Candidate dispositions across current assessments ===
WITH latest AS (
    SELECT DISTINCT ON (component_id)
        component_id, matching_candidates, cutoff_date, as_of, inserted_at, version_id
    FROM procrun.assessment_versions
    ORDER BY component_id, cutoff_date DESC, as_of DESC, inserted_at DESC, version_id DESC
), candidates AS (
    SELECT jsonb_array_elements(matching_candidates) AS candidate
    FROM latest
)
SELECT
    coalesce(candidate->>'disposition','<missing>') || E'\t' ||
    coalesce(candidate->>'tier','<missing>') || E'\t' ||
    count(*)::text
FROM candidates
GROUP BY candidate->>'disposition', candidate->>'tier'
ORDER BY count(*) DESC, candidate->>'disposition', candidate->>'tier';

\echo === Candidate evaluation reasons ===
WITH latest AS (
    SELECT DISTINCT ON (component_id)
        component_id, matching_candidates, cutoff_date, as_of, inserted_at, version_id
    FROM procrun.assessment_versions
    ORDER BY component_id, cutoff_date DESC, as_of DESC, inserted_at DESC, version_id DESC
), candidates AS (
    SELECT jsonb_array_elements(matching_candidates) AS candidate
    FROM latest
)
SELECT
    count(*)::text || E'\t' ||
    coalesce(candidate->>'reason','<missing>')
FROM candidates
GROUP BY candidate->>'reason'
ORDER BY count(*) DESC, candidate->>'reason';

\echo === Structural feature prevalence ===
WITH latest AS (
    SELECT DISTINCT ON (component_id)
        component_id, matching_candidates, cutoff_date, as_of, inserted_at, version_id
    FROM procrun.assessment_versions
    ORDER BY component_id, cutoff_date DESC, as_of DESC, inserted_at DESC, version_id DESC
), candidates AS (
    SELECT jsonb_array_elements(matching_candidates) AS candidate
    FROM latest
)
SELECT 'exact_project_identifier=true' || E'\t' || count(*)::text
FROM candidates WHERE candidate#>>'{features,exact_project_identifier}' = 'true'
UNION ALL
SELECT 'contracting_authority_match=true' || E'\t' || count(*)::text
FROM candidates WHERE candidate#>>'{features,contracting_authority_match}' = 'true'
UNION ALL
SELECT 'geography_match=true' || E'\t' || count(*)::text
FROM candidates WHERE candidate#>>'{features,geography_match}' = 'true'
UNION ALL
SELECT 'high_scope_overlap=true' || E'\t' || count(*)::text
FROM candidates WHERE candidate#>>'{features,high_scope_overlap}' = 'true'
UNION ALL
SELECT 'cpv_or_category_match=true' || E'\t' || count(*)::text
FROM candidates WHERE candidate#>>'{features,cpv_or_category_match}' = 'true'
UNION ALL
SELECT 'compatible_date_window=true' || E'\t' || count(*)::text
FROM candidates WHERE candidate#>>'{features,compatible_date_window}' = 'true'
UNION ALL
SELECT 'project_title_or_location_match=true' || E'\t' || count(*)::text
FROM candidates WHERE candidate#>>'{features,project_title_or_location_match}' = 'true';

\echo === Near-Tier-A signatures (exact project id) ===
WITH latest AS (
    SELECT DISTINCT ON (component_id)
        component_id, matching_candidates, cutoff_date, as_of, inserted_at, version_id
    FROM procrun.assessment_versions
    ORDER BY component_id, cutoff_date DESC, as_of DESC, inserted_at DESC, version_id DESC
), candidates AS (
    SELECT jsonb_array_elements(matching_candidates) AS candidate
    FROM latest
)
SELECT
    count(*)::text || E'\t' ||
    'project_id=' || coalesce(candidate#>>'{features,exact_project_identifier}','?') || E'\t' ||
    'scope=' || coalesce(candidate#>>'{features,high_scope_overlap}','?') || E'\t' ||
    'date=' || coalesce(candidate#>>'{features,compatible_date_window}','?') || E'\t' ||
    'tier=' || coalesce(candidate->>'tier','?') || E'\t' ||
    'disposition=' || coalesce(candidate->>'disposition','?')
FROM candidates
WHERE candidate#>>'{features,exact_project_identifier}' = 'true'
GROUP BY
    candidate#>>'{features,exact_project_identifier}',
    candidate#>>'{features,high_scope_overlap}',
    candidate#>>'{features,compatible_date_window}',
    candidate->>'tier',
    candidate->>'disposition'
ORDER BY count(*) DESC;

\echo === Near-Tier-B signatures (scope + CPV + date) ===
WITH latest AS (
    SELECT DISTINCT ON (component_id)
        component_id, matching_candidates, cutoff_date, as_of, inserted_at, version_id
    FROM procrun.assessment_versions
    ORDER BY component_id, cutoff_date DESC, as_of DESC, inserted_at DESC, version_id DESC
), candidates AS (
    SELECT jsonb_array_elements(matching_candidates) AS candidate
    FROM latest
)
SELECT
    count(*)::text || E'\t' ||
    'authority=' || coalesce(candidate#>>'{features,contracting_authority_match}','?') || E'\t' ||
    'geo=' || coalesce(candidate#>>'{features,geography_match}','?') || E'\t' ||
    'scope=' || coalesce(candidate#>>'{features,high_scope_overlap}','?') || E'\t' ||
    'cpv=' || coalesce(candidate#>>'{features,cpv_or_category_match}','?') || E'\t' ||
    'date=' || coalesce(candidate#>>'{features,compatible_date_window}','?') || E'\t' ||
    'tier=' || coalesce(candidate->>'tier','?')
FROM candidates
WHERE candidate#>>'{features,high_scope_overlap}' = 'true'
  AND candidate#>>'{features,cpv_or_category_match}' = 'true'
  AND candidate#>>'{features,compatible_date_window}' = 'true'
GROUP BY
    candidate#>>'{features,contracting_authority_match}',
    candidate#>>'{features,geography_match}',
    candidate#>>'{features,high_scope_overlap}',
    candidate#>>'{features,cpv_or_category_match}',
    candidate#>>'{features,compatible_date_window}',
    candidate->>'tier'
ORDER BY count(*) DESC;
'@

Write-Host "Auditing why current production produces no CLOSED components (aggregate counts only)..."
$sql | ssh -T `
    -o ConnectTimeout=10 `
    -o ConnectionAttempts=1 `
    -i $SshKey `
    "${SshUser}@${Server}" `
    "sudo -u postgres psql -d procrun"

if ($LASTEXITCODE -ne 0) {
    throw "Could not read aggregate CLOSED diagnostics from the central database."
}
