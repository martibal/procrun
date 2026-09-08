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

\echo === CLOSED rule construction facts ===
SELECT 'FundingProject has contracting-authority field' || E'\t' ||
       CASE WHEN EXISTS (
           SELECT 1 FROM information_schema.columns
           WHERE table_schema='procrun'
             AND table_name='funding_project_versions'
             AND column_name IN ('contracting_authority_name','contracting_authority_id')
       ) THEN 'YES' ELSE 'NO' END;

\echo === Current TED evidence field availability ===
WITH latest_evidence AS (
    SELECT DISTINCT ON (evidence_id)
        evidence_id,
        component_id,
        project_reference,
        contracting_authority_name,
        publication_date,
        as_of,
        inserted_at,
        version_id
    FROM procrun.procurement_evidence_versions
    ORDER BY evidence_id, as_of DESC, inserted_at DESC, version_id DESC
)
SELECT 'evidence rows' || E'\t' || count(*) FROM latest_evidence
UNION ALL
SELECT 'project_reference present' || E'\t' || count(*)
FROM latest_evidence
WHERE nullif(btrim(project_reference),'') IS NOT NULL
UNION ALL
SELECT 'contracting_authority_name present' || E'\t' || count(*)
FROM latest_evidence
WHERE nullif(btrim(contracting_authority_name),'') IS NOT NULL;

\echo === Exact project-reference path (Tier A prerequisite) ===
WITH latest_assessment AS (
    SELECT DISTINCT ON (component_id)
        component_id,
        operation_code,
        cutoff_date,
        as_of,
        inserted_at,
        version_id
    FROM procrun.assessment_versions
    ORDER BY component_id, cutoff_date DESC, as_of DESC, inserted_at DESC, version_id DESC
), latest_evidence AS (
    SELECT DISTINCT ON (evidence_id)
        evidence_id,
        component_id,
        project_reference,
        publication_date,
        as_of,
        inserted_at,
        version_id
    FROM procrun.procurement_evidence_versions
    ORDER BY evidence_id, as_of DESC, inserted_at DESC, version_id DESC
)
SELECT 'project_reference present on current-component evidence' || E'\t' || count(*)
FROM latest_evidence e
JOIN latest_assessment a USING (component_id)
WHERE nullif(btrim(e.project_reference),'') IS NOT NULL
UNION ALL
SELECT 'exact project_reference = operation_code' || E'\t' || count(*)
FROM latest_evidence e
JOIN latest_assessment a USING (component_id)
WHERE nullif(btrim(e.project_reference),'') IS NOT NULL
  AND lower(btrim(e.project_reference)) = lower(btrim(a.operation_code));

\echo === What currently blocks automatic CLOSED ===
SELECT 'Tier A' || E'\t' || 'requires exact project identifier + exact scope evidence + compatible date';
SELECT 'Tier B' || E'\t' || 'requires contracting-authority match + geography + exact scope evidence + CPV/category + compatible date';
SELECT 'Tier C' || E'\t' || 'review only; cannot produce CLOSED';
'@

Write-Host "Auditing whether current source fields can support Tier A/B CLOSED (aggregate counts only)..."
$sql | ssh -T `
    -o ConnectTimeout=10 `
    -o ConnectionAttempts=1 `
    -i $SshKey `
    "${SshUser}@${Server}" `
    "sudo -u postgres psql -d procrun"

if ($LASTEXITCODE -ne 0) {
    throw "Could not read aggregate CLOSED evidence-path diagnostics from the central database."
}
