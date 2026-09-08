param(
    [string]$Server = "62.238.117.62",
    [string]$SshUser = "root",
    [int]$TimeoutMinutes = 45
)

$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent $PSScriptRoot
$SshKey = Join-Path $env:USERPROFILE ".ssh\procrun_hetzner"
$LocalProcrunPackage = Join-Path $RepoRoot "src\procrun"
$LocalDeliveryScript = Join-Path $PSScriptRoot "run_live_delivery.py"
$RemoteRoot = "/tmp/procrun-phase-m-reclassify"
$RemoteRunner = "/tmp/procrun-phase-m-reclassify.sh"
$LocalRunner = Join-Path ([System.IO.Path]::GetTempPath()) "procrun-phase-m-reclassify.sh"

$SshOptions = @(
    "-o", "ConnectTimeout=10",
    "-o", "ConnectionAttempts=1",
    "-o", "ServerAliveInterval=15",
    "-o", "ServerAliveCountMax=3",
    "-o", "BatchMode=yes"
)

if (-not (Test-Path $SshKey)) {
    throw "Missing SSH key: $SshKey"
}
if (-not (Test-Path $LocalProcrunPackage)) {
    throw "Missing local ProcRun package: $LocalProcrunPackage"
}
if (-not (Test-Path $LocalDeliveryScript)) {
    throw "Missing canonical live-delivery runner: $LocalDeliveryScript"
}

Write-Host "Phase M A2: controlled reclassification using the current local matching code."
Write-Host "The production checkout, timers and published runway.jsonl are not modified."
Write-Host "The run appends new ledger versions to the central production database."

Write-Host "[1/5] Preparing isolated temporary source directory..."
& ssh @SshOptions -i $SshKey "${SshUser}@${Server}" "timeout 20s sh -c 'rm -rf $RemoteRoot $RemoteRunner && mkdir -p $RemoteRoot'"
if ($LASTEXITCODE -ne 0) {
    throw "Step 1 failed: could not prepare the remote temporary directory."
}
Write-Host "[1/5] OK"

try {
    Write-Host "[2/5] Uploading current ProcRun source and canonical delivery runner..."
    & scp @SshOptions -r -i $SshKey $LocalProcrunPackage "${SshUser}@${Server}:${RemoteRoot}/"
    if ($LASTEXITCODE -ne 0) {
        throw "Step 2 failed while uploading src/procrun."
    }
    & scp @SshOptions -i $SshKey $LocalDeliveryScript "${SshUser}@${Server}:${RemoteRoot}/run_live_delivery.py"
    if ($LASTEXITCODE -ne 0) {
        throw "Step 2 failed while uploading run_live_delivery.py."
    }
    Write-Host "[2/5] OK"

    $remoteScript = @"
set -euo pipefail
ACL_BACKUP=/tmp/procrun-phase-m-reclassify.acl
REMOTE_ROOT=$RemoteRoot
PROD_OC_CACHE=/var/lib/procrun/cache/opencoesione-lombardia.json
TEMP_OC_CACHE="`$REMOTE_ROOT/opencoesione-lombardia.json"

cleanup() {
    if [ -f "`$ACL_BACKUP" ]; then
        setfacl --restore="`$ACL_BACKUP" >/dev/null 2>&1 || true
        rm -f "`$ACL_BACKUP"
    fi
    rm -rf "`$REMOTE_ROOT"
}
trap cleanup EXIT

if ! command -v getfacl >/dev/null 2>&1 || ! command -v setfacl >/dev/null 2>&1; then
    echo '[remote] ERROR: getfacl/setfacl are required.' >&2
    exit 41
fi

cutoff=`$(sudo -u postgres psql -d procrun -Atqc "SELECT max(cutoff_date)::text FROM procrun.assessment_versions;")
if [ -z "`$cutoff" ]; then
    echo '[remote] ERROR: no existing production assessment cutoff was found.' >&2
    exit 42
fi

echo "[remote] Frozen comparison cutoff: `$cutoff"
echo '[remote] BEFORE latest component states:'
sudo -u postgres psql -d procrun -Atqc "WITH latest AS (SELECT DISTINCT ON (component_id) component_id,state FROM procrun.assessment_versions ORDER BY component_id,cutoff_date DESC,as_of DESC,inserted_at DESC,version_id DESC) SELECT state || E'\\t' || count(*) FROM latest GROUP BY state ORDER BY state;"

getfacl -p /opt/procrun /opt/procrun/venv /opt/procrun/venv/bin > "`$ACL_BACKUP"
setfacl -m u:postgres:--x /opt/procrun
setfacl -m u:postgres:--x /opt/procrun/venv
setfacl -m u:postgres:--x /opt/procrun/venv/bin

# Do not broaden postgres access to /var/lib/procrun. Root copies the already-approved
# OpenCoesione production cache into the isolated Phase M directory, then postgres reads only
# that temporary copy. If the canonical cache is absent, fail closed instead of changing source
# behavior during the validation run.
if [ ! -f "`$PROD_OC_CACHE" ]; then
    echo "[remote] ERROR: canonical OpenCoesione cache is missing at `$PROD_OC_CACHE; Phase M will not bootstrap a new cache." >&2
    exit 44
fi
cp --preserve=timestamps "`$PROD_OC_CACHE" "`$TEMP_OC_CACHE"
chown -R postgres:postgres "`$REMOTE_ROOT"
chmod 600 "`$TEMP_OC_CACHE"

if ! sudo -u postgres test -x /opt/procrun/venv/bin/python; then
    echo '[remote] ERROR: postgres cannot execute the production virtualenv Python.' >&2
    exit 43
fi
if ! sudo -u postgres test -r "`$TEMP_OC_CACHE"; then
    echo '[remote] ERROR: postgres cannot read the isolated OpenCoesione cache copy.' >&2
    exit 45
fi

echo '[remote] Running canonical live delivery with current branch code.'
echo '[remote] OpenCoesione input is the isolated copy of the already-approved production cache.'
echo '[remote] TED is re-read through the same approved canonical route; this may take several minutes.'
sudo -u postgres env \
    PYTHONPATH="`$REMOTE_ROOT" \
    PROCRUN_OPENCOESIONE_CACHE="`$TEMP_OC_CACHE" \
    /opt/procrun/venv/bin/python "`$REMOTE_ROOT/run_live_delivery.py" \
    --database-url 'dbname=procrun' \
    --output "`$REMOTE_ROOT/phase-m-runway.jsonl" \
    --cutoff "`$cutoff"

echo '[remote] AFTER latest component states:'
sudo -u postgres psql -d procrun -Atqc "WITH latest AS (SELECT DISTINCT ON (component_id) component_id,state,rationale FROM procrun.assessment_versions ORDER BY component_id,cutoff_date DESC,as_of DESC,inserted_at DESC,version_id DESC) SELECT state || E'\\t' || count(*) FROM latest GROUP BY state ORDER BY state;"

echo '[remote] AFTER unresolved reasons:'
sudo -u postgres psql -d procrun -Atqc "WITH latest AS (SELECT DISTINCT ON (component_id) component_id,state,rationale FROM procrun.assessment_versions ORDER BY component_id,cutoff_date DESC,as_of DESC,inserted_at DESC,version_id DESC) SELECT count(*)::text || E'\\t' || rationale FROM latest WHERE state='UNRESOLVED' GROUP BY rationale ORDER BY count(*) DESC,rationale;"
"@

    $remoteScriptLf = $remoteScript.Replace("`r`n", "`n").Replace("`r", "")
    [System.IO.File]::WriteAllText($LocalRunner, $remoteScriptLf, [System.Text.UTF8Encoding]::new($false))

    Write-Host "[3/5] Uploading fail-closed remote runner..."
    & scp @SshOptions -i $SshKey $LocalRunner "${SshUser}@${Server}:${RemoteRunner}"
    if ($LASTEXITCODE -ne 0) {
        throw "Step 3 failed: could not upload the remote runner."
    }
    Write-Host "[3/5] OK"

    Write-Host "[4/5] Reclassifying against the frozen production cutoff (hard timeout: $TimeoutMinutes minutes)..."
    $timeoutSeconds = $TimeoutMinutes * 60
    & ssh @SshOptions -i $SshKey "${SshUser}@${Server}" "timeout ${timeoutSeconds}s bash $RemoteRunner"
    $runExit = $LASTEXITCODE
    if ($runExit -eq 124) {
        throw "Step 4 timed out after $TimeoutMinutes minutes."
    }
    if ($runExit -ne 0) {
        throw "Step 4 failed with remote exit code $runExit."
    }
    Write-Host "[4/5] OK"

    Write-Host "[5/5] Reclassification complete."
    Write-Host "Now run: .\scripts\phase_m_append_audit.ps1"
}
finally {
    Remove-Item $LocalRunner -Force -ErrorAction SilentlyContinue
    & ssh @SshOptions -i $SshKey "${SshUser}@${Server}" "timeout 15s sh -c 'rm -f $RemoteRunner; rm -rf $RemoteRoot; if [ -f /tmp/procrun-phase-m-reclassify.acl ]; then setfacl --restore=/tmp/procrun-phase-m-reclassify.acl >/dev/null 2>&1 || true; rm -f /tmp/procrun-phase-m-reclassify.acl; fi'" | Out-Null
}
