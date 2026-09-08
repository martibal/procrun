param(
    [string]$Server = "62.238.117.62",
    [string]$SshUser = "root",
    [int]$TimeoutMinutes = 45
)

$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent $PSScriptRoot
$SshKey = Join-Path $env:USERPROFILE ".ssh\procrun_hetzner"
$LocalPackage = Join-Path $RepoRoot "src\procrun"
$LocalReclassifier = Join-Path $PSScriptRoot "phase_m_apply_projected_cup_linkage.py"
$RemoteRoot = "/tmp/procrun-phase-m-cup-linkage"
$RemoteRunner = "/tmp/procrun-phase-m-cup-linkage.sh"
$LocalRunner = Join-Path ([System.IO.Path]::GetTempPath()) "procrun-phase-m-cup-linkage.sh"

$SshOptions = @(
    "-o", "ConnectTimeout=10",
    "-o", "ConnectionAttempts=1",
    "-o", "ServerAliveInterval=15",
    "-o", "ServerAliveCountMax=3",
    "-o", "BatchMode=yes"
)

if (-not (Test-Path $SshKey)) { throw "Missing SSH key: $SshKey" }
if (-not (Test-Path $LocalPackage)) { throw "Missing local ProcRun package: $LocalPackage" }
if (-not (Test-Path $LocalReclassifier)) { throw "Missing CUP linkage reclassifier: $LocalReclassifier" }

Write-Host "Phase M: applying exact CUP linkage from the approved server-side TED projection."
Write-Host "No ANAC/BDNCP page, buyer, winner, contact or municipality data is requested."
Write-Host "Production checkout, timers and published runway.jsonl are not modified."
Write-Host "Only append-only assessment/project-assessment versions are written."

Write-Host "[1/5] Preparing isolated remote source..."
& ssh @SshOptions -i $SshKey "${SshUser}@${Server}" "timeout 20s sh -c 'rm -rf $RemoteRoot $RemoteRunner && mkdir -p $RemoteRoot'"
if ($LASTEXITCODE -ne 0) { throw "Step 1 failed." }
Write-Host "[1/5] OK"

try {
    Write-Host "[2/5] Uploading current ProcRun source and CUP reclassifier..."
    & scp @SshOptions -r -i $SshKey $LocalPackage "${SshUser}@${Server}:${RemoteRoot}/"
    if ($LASTEXITCODE -ne 0) { throw "Step 2 failed while uploading src/procrun." }
    & scp @SshOptions -i $SshKey $LocalReclassifier "${SshUser}@${Server}:${RemoteRoot}/phase_m_apply_projected_cup_linkage.py"
    if ($LASTEXITCODE -ne 0) { throw "Step 2 failed while uploading reclassifier." }
    Write-Host "[2/5] OK"

    $remoteScript = @"
set -euo pipefail
ACL_BACKUP=/tmp/procrun-phase-m-cup-linkage.acl
REMOTE_ROOT=$RemoteRoot

cleanup() {
    if [ -f "`$ACL_BACKUP" ]; then
        setfacl --restore="`$ACL_BACKUP" >/dev/null 2>&1 || true
        rm -f "`$ACL_BACKUP"
    fi
    rm -rf "`$REMOTE_ROOT"
}
trap cleanup EXIT

cutoff=`$(sudo -u postgres psql -d procrun -Atqc "SELECT max(cutoff_date)::text FROM procrun.assessment_versions;")
if [ -z "`$cutoff" ]; then
    echo '[remote] ERROR: no production cutoff found.' >&2
    exit 42
fi

echo "[remote] Frozen comparison cutoff: `$cutoff"
echo '[remote] BEFORE latest component states:'
sudo -u postgres psql -d procrun -Atqc "WITH latest AS (SELECT DISTINCT ON (component_id) component_id,state FROM procrun.assessment_versions ORDER BY component_id,cutoff_date DESC,as_of DESC,inserted_at DESC,version_id DESC) SELECT state || E'\\t' || count(*) FROM latest GROUP BY state ORDER BY state;"

getfacl -p /opt/procrun /opt/procrun/venv /opt/procrun/venv/bin > "`$ACL_BACKUP"
setfacl -m u:postgres:--x /opt/procrun
setfacl -m u:postgres:--x /opt/procrun/venv
setfacl -m u:postgres:--x /opt/procrun/venv/bin
chown -R postgres:postgres "`$REMOTE_ROOT"

if ! sudo -u postgres test -x /opt/procrun/venv/bin/python; then
    echo '[remote] ERROR: postgres cannot execute production virtualenv Python.' >&2
    exit 43
fi

echo '[remote] Fetching only the approved TED projected fields, including the qualified lot-level financing identifier.'
sudo -u postgres env PYTHONPATH="`$REMOTE_ROOT" /opt/procrun/venv/bin/python "`$REMOTE_ROOT/phase_m_apply_projected_cup_linkage.py" \
    --database-url 'dbname=procrun' \
    --cutoff "`$cutoff"

echo '[remote] AFTER latest component states:'
sudo -u postgres psql -d procrun -Atqc "WITH latest AS (SELECT DISTINCT ON (component_id) component_id,state FROM procrun.assessment_versions ORDER BY component_id,cutoff_date DESC,as_of DESC,inserted_at DESC,version_id DESC) SELECT state || E'\\t' || count(*) FROM latest GROUP BY state ORDER BY state;"
"@

    [System.IO.File]::WriteAllText(
        $LocalRunner,
        $remoteScript.Replace("`r`n", "`n").Replace("`r", ""),
        [System.Text.UTF8Encoding]::new($false)
    )

    Write-Host "[3/5] Uploading fail-closed remote runner..."
    & scp @SshOptions -i $SshKey $LocalRunner "${SshUser}@${Server}:${RemoteRunner}"
    if ($LASTEXITCODE -ne 0) { throw "Step 3 failed." }
    Write-Host "[3/5] OK"

    Write-Host "[4/5] Applying projected CUP linkage (hard timeout: $TimeoutMinutes minutes)..."
    $timeoutSeconds = $TimeoutMinutes * 60
    & ssh @SshOptions -i $SshKey "${SshUser}@${Server}" "timeout ${timeoutSeconds}s bash $RemoteRunner"
    $runExit = $LASTEXITCODE
    if ($runExit -eq 124) { throw "Step 4 timed out after $TimeoutMinutes minutes." }
    if ($runExit -ne 0) { throw "Step 4 failed with remote exit code $runExit." }
    Write-Host "[4/5] OK"

    Write-Host "[5/5] CUP linkage applied."
    Write-Host "Now run: .\scripts\phase_m_append_audit.ps1"
}
finally {
    Remove-Item $LocalRunner -Force -ErrorAction SilentlyContinue
    & ssh @SshOptions -i $SshKey "${SshUser}@${Server}" "timeout 15s sh -c 'rm -f $RemoteRunner; rm -rf $RemoteRoot; if [ -f /tmp/procrun-phase-m-cup-linkage.acl ]; then setfacl --restore=/tmp/procrun-phase-m-cup-linkage.acl >/dev/null 2>&1 || true; rm -f /tmp/procrun-phase-m-cup-linkage.acl; fi'" | Out-Null
}
