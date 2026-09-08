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
\set ON_ERROR_STOP on

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
        c.component_id,
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
SELECT label || E'\t' || value::text
FROM (
    SELECT 1 AS sort_order, 'evidence rows' AS label, count(*)::bigint AS value
    FROM joined

    UNION ALL

    SELECT 2, 'project_reference exact raw', count(*)::bigint
    FROM joined
    WHERE nullif(project_reference,'') IS NOT NULL
      AND lower(trim(project_reference)) = lower(trim(operation_code))

    UNION ALL

    SELECT 3, 'project_reference exact normalized', count(*)::bigint
    FROM joined
    WHERE op_norm <> '' AND ref_norm = op_norm

    UNION ALL

    SELECT 4, 'operation_code embedded in TED title (normalized)', count(*)::bigint
    FROM joined
    WHERE op_norm <> '' AND position(op_norm in title_norm) > 0

    UNION ALL

    SELECT 5, 'operation_code embedded in TED scope (normalized)', count(*)::bigint
    FROM joined
    WHERE op_norm <> '' AND position(op_norm in scope_norm) > 0

    UNION ALL

    SELECT 6, 'operation_code embedded in TED title OR scope (normalized)', count(*)::bigint
    FROM joined
    WHERE op_norm <> ''
      AND (position(op_norm in title_norm) > 0 OR position(op_norm in scope_norm) > 0)

    UNION ALL

    SELECT 7, 'distinct components with exact id in title/scope', count(DISTINCT component_id)::bigint
    FROM joined
    WHERE op_norm <> ''
      AND (position(op_norm in title_norm) > 0 OR position(op_norm in scope_norm) > 0)
) counts
ORDER BY sort_order;

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
