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
WITH latest AS (
    SELECT DISTINCT ON (component_id)
        component_id,
        state,
        rationale,
        cutoff_date,
        as_of,
        inserted_at,
        version_id
    FROM procrun.assessment_versions
    ORDER BY component_id, cutoff_date DESC, as_of DESC, inserted_at DESC, version_id DESC
)
SELECT
    count(*)::text || E'\t' || rationale
FROM latest
WHERE state = 'UNRESOLVED'
GROUP BY rationale
ORDER BY count(*) DESC, rationale;
'@

Write-Host "Current UNRESOLVED components grouped by stored rationale:"
$sql | ssh -T `
    -o ConnectTimeout=10 `
    -o ConnectionAttempts=1 `
    -i $SshKey `
    "${SshUser}@${Server}" `
    "sudo -u postgres psql -d procrun -At"

if ($LASTEXITCODE -ne 0) {
    throw "Could not read aggregate unresolved-reason counts from the central database."
}
