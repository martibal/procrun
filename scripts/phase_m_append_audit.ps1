param(
    [string]$Server = "62.238.117.62",
    [string]$SshUser = "root",
    [string]$ReportPath = "docs/MATCHING_QUALITY_REPORT.md"
)

$ErrorActionPreference = "Stop"
$SshKey = Join-Path $env:USERPROFILE ".ssh\procrun_hetzner"

if (-not (Test-Path $SshKey)) {
    throw "Missing SSH key: $SshKey"
}

$sql = @'
\pset tuples_only on
\pset format unaligned

\echo === CURRENT state counts ===
WITH latest AS (
    SELECT DISTINCT ON (component_id)
        component_id, state, rationale, matching_candidates,
        cutoff_date, as_of, inserted_at, version_id
    FROM procrun.assessment_versions
    ORDER BY component_id, cutoff_date DESC, as_of DESC, inserted_at DESC, version_id DESC
)
SELECT count(*)::text || E'\t' || state
FROM latest
GROUP BY state
ORDER BY state;

\echo === UNRESOLVED rationale counts ===
WITH latest AS (
    SELECT DISTINCT ON (component_id)
        component_id, state, rationale, matching_candidates,
        cutoff_date, as_of, inserted_at, version_id
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
        component_id, state, rationale, matching_candidates,
        cutoff_date, as_of, inserted_at, version_id
    FROM procrun.assessment_versions
    ORDER BY component_id, cutoff_date DESC, as_of DESC, inserted_at DESC, version_id DESC
), review_rows AS (
    SELECT jsonb_array_elements(matching_candidates) AS candidate
    FROM latest
    WHERE state = 'UNRESOLVED'
      AND rationale = 'A pre-cutoff procurement candidate is in the review band; OPEN is prohibited.'
)
SELECT count(*)::text || E'\t' ||
       coalesce(candidate->>'tier', '<missing>') || E'\t' ||
       coalesce(candidate->>'reason', '<missing>')
FROM review_rows
WHERE candidate->>'disposition' = 'REVIEW'
GROUP BY candidate->>'tier', candidate->>'reason'
ORDER BY count(*) DESC, candidate->>'tier', candidate->>'reason';

\echo === REVIEW deterministic feature signatures ===
WITH latest AS (
    SELECT DISTINCT ON (component_id)
        component_id, state, rationale, matching_candidates,
        cutoff_date, as_of, inserted_at, version_id
    FROM procrun.assessment_versions
    ORDER BY component_id, cutoff_date DESC, as_of DESC, inserted_at DESC, version_id DESC
), review_rows AS (
    SELECT jsonb_array_elements(matching_candidates) AS candidate
    FROM latest
    WHERE state = 'UNRESOLVED'
      AND rationale = 'A pre-cutoff procurement candidate is in the review band; OPEN is prohibited.'
)
SELECT count(*)::text || E'\t' ||
       'tier=' || coalesce(candidate->>'tier','?') || E'\t' ||
       'project_id=' || coalesce(candidate#>>'{features,exact_project_identifier}','?') || E'\t' ||
       'geo=' || coalesce(candidate#>>'{features,geography_match}','?') || E'\t' ||
       'scope=' || coalesce(candidate#>>'{features,high_scope_overlap}','?') || E'\t' ||
       'cpv=' || coalesce(candidate#>>'{features,cpv_or_category_match}','?') || E'\t' ||
       'date=' || coalesce(candidate#>>'{features,compatible_date_window}','?') || E'\t' ||
       'title_or_location=' || coalesce(candidate#>>'{features,project_title_or_location_match}','?')
FROM review_rows
WHERE candidate->>'disposition' = 'REVIEW'
GROUP BY candidate->>'tier',
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
        component_id, state, rationale, matching_candidates,
        cutoff_date, as_of, inserted_at, version_id
    FROM procrun.assessment_versions
    ORDER BY component_id, cutoff_date DESC, as_of DESC, inserted_at DESC, version_id DESC
), per_component AS (
    SELECT component_id,
           count(*) FILTER (WHERE candidate->>'disposition' = 'REVIEW') AS review_count
    FROM latest
    CROSS JOIN LATERAL jsonb_array_elements(matching_candidates) AS candidate
    WHERE state = 'UNRESOLVED'
      AND rationale = 'A pre-cutoff procurement candidate is in the review band; OPEN is prohibited.'
    GROUP BY component_id
)
SELECT count(*)::text || E'\t' || bucket
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
ORDER BY CASE bucket
    WHEN '1 review candidate' THEN 1
    WHEN '2-5 review candidates' THEN 2
    WHEN '6-20 review candidates' THEN 3
    ELSE 4 END;
'@

$timestamp = (Get-Date).ToString("yyyy-MM-ddTHH:mm:ssK")
$commit = (git rev-parse HEAD).Trim()
if ($LASTEXITCODE -ne 0) { throw "Could not resolve current Git commit." }

Write-Host "Running Phase M production audit..."
$output = $sql | ssh -T `
    -o ConnectTimeout=10 `
    -o ConnectionAttempts=1 `
    -i $SshKey `
    "${SshUser}@${Server}" `
    "sudo -u postgres psql -d procrun"

if ($LASTEXITCODE -ne 0) {
    throw "Could not read Phase M aggregate diagnostics from the central database."
}

$section = @"

## $timestamp — automated Phase M Part A audit

- Git commit: `$commit`
- Database: central production `procrun`
- Invocation: `scripts/phase_m_append_audit.ps1`

### Exact SQL

```sql
$sql
```

### Complete output

```text
$($output -join [Environment]::NewLine)
```
"@

$reportDir = Split-Path -Parent $ReportPath
if ($reportDir -and -not (Test-Path $reportDir)) {
    New-Item -ItemType Directory -Force -Path $reportDir | Out-Null
}
Add-Content -Path $ReportPath -Value $section -Encoding UTF8

Write-Host "Appended full Phase M audit to $ReportPath"
Write-Host ($output -join [Environment]::NewLine)
