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

\echo === Exact funded-project identifier paths in stored TED evidence ===
WITH latest_project AS (
    SELECT DISTINCT ON (operation_code)
        operation_code,
        project_title,
        nuts_code
    FROM procrun.funding_project_versions
    ORDER BY operation_code, as_of DESC, inserted_at DESC, version_id DESC
), latest_evidence AS (
    SELECT DISTINCT ON (evidence_id)
        evidence_id,
        component_id,
        title,
        scope_description,
        project_reference,
        publication_date,
        cpv_codes,
        nuts_code
    FROM procrun.procurement_evidence_versions
    ORDER BY evidence_id, as_of DESC, inserted_at DESC, version_id DESC
), latest_component AS (
    SELECT DISTINCT ON (component_id)
        component_id,
        operation_code
    FROM procrun.component_versions
    ORDER BY component_id, as_of DESC, inserted_at DESC, version_id DESC
), joined AS (
    SELECT
        p.operation_code,
        e.evidence_id,
        e.title,
        e.scope_description,
        e.project_reference,
        regexp_replace(lower(coalesce(p.operation_code,'')), '[^a-z0-9]', '', 'g') AS op_norm,
        regexp_replace(lower(coalesce(e.project_reference,'')), '[^a-z0-9]', '', 'g') AS ref_norm,
        regexp_replace(lower(coalesce(e.title,'')), '[^a-z0-9]', '', 'g') AS title_norm,
        regexp_replace(lower(coalesce(e.scope_description,'')), '[^a-z0-9]', '', 'g') AS scope_norm
    FROM latest_evidence e
    JOIN latest_component c ON c.component_id = e.component_id
    JOIN latest_project p ON p.operation_code = c.operation_code
)
SELECT 'evidence rows' || E'\t' || count(*) FROM joined;
SELECT 'project_reference exact raw' || E'\t' || count(*)
FROM joined
WHERE nullif(project_reference,'') IS NOT NULL
  AND lower(trim(project_reference)) = lower(trim(operation_code));
SELECT 'project_reference exact normalized' || E'\t' || count(*)
FROM joined
WHERE op_norm <> '' AND ref_norm = op_norm;
SELECT 'operation_code embedded in TED title (normalized)' || E'\t' || count(*)
FROM joined
WHERE op_norm <> '' AND position(op_norm in title_norm) > 0;
SELECT 'operation_code embedded in TED scope (normalized)' || E'\t' || count(*)
FROM joined
WHERE op_norm <> '' AND position(op_norm in scope_norm) > 0;
SELECT 'operation_code embedded in TED title OR scope (normalized)' || E'\t' || count(*)
FROM joined
WHERE op_norm <> '' AND (position(op_norm in title_norm) > 0 OR position(op_norm in scope_norm) > 0);
SELECT 'distinct components with exact id in title/scope' || E'\t' || count(DISTINCT c.component_id)
FROM latest_evidence e
JOIN latest_component c ON c.component_id = e.component_id
JOIN latest_project p ON p.operation_code = c.operation_code
WHERE regexp_replace(lower(p.operation_code), '[^a-z0-9]', '', 'g') <> ''
  AND (
      position(
          regexp_replace(lower(p.operation_code), '[^a-z0-9]', '', 'g')
          in regexp_replace(lower(coalesce(e.title,'')), '[^a-z0-9]', '', 'g')
      ) > 0
      OR position(
          regexp_replace(lower(p.operation_code), '[^a-z0-9]', '', 'g')
          in regexp_replace(lower(coalesce(e.scope_description,'')), '[^a-z0-9]', '', 'g')
      ) > 0
  );

\echo === Current production projection context ===
\echo production retains TED title and scope_description: YES
\echo production retains eu-funds-identifier as project_reference: YES
\echo procedure-identifier was previously qualified in the TED foundation inventory but is not retained by the current production collector
\echo This audit does not request any new TED fields and does not print identifiers or source-row values.
'@

Write-Host "Auditing exact project-ID linkage paths already present in stored TED evidence (aggregate counts only)..."
$sql | ssh -T `
    -o ConnectTimeout=10 `
    -o ConnectionAttempts=1 `
    -i $SshKey `
    "${SshUser}@${Server}" `
    "sudo -u postgres psql -d procrun"

if ($LASTEXITCODE -ne 0) {
    throw "Could not audit exact project-ID paths in the central database."
}
