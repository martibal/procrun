param(
    [string]$Server = "62.238.117.62",
    [string]$SshUser = "root"
)

$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent $PSScriptRoot
$SshKey = Join-Path $env:USERPROFILE ".ssh\procrun_hetzner"
$SqlFile = Join-Path $PSScriptRoot "configure_web_dev_role.sql"
$LocalProcrunPackage = Join-Path $RepoRoot "src\procrun"
$RemoteSql = "/tmp/procrun_web_dev_role.sql"
$RemoteMigrationRoot = "/tmp/procrun-web-migrate-src"
$RemoteMigrationScript = "/tmp/procrun-web-migrate.sh"
$LocalMigrationScript = Join-Path ([System.IO.Path]::GetTempPath()) "procrun-web-migrate.sh"

$SshOptions = @(
    "-o", "ConnectTimeout=10",
    "-o", "ServerAliveInterval=10",
    "-o", "ServerAliveCountMax=2",
    "-o", "BatchMode=yes"
)

if (-not (Test-Path $SshKey)) {
    throw "Missing SSH key: $SshKey"
}

if (-not (Test-Path $SqlFile)) {
    throw "Missing SQL role definition: $SqlFile"
}

if (-not (Test-Path $LocalProcrunPackage)) {
    throw "Missing local ProcRun Python package: $LocalProcrunPackage"
}

Write-Host "[1/6] Preparing temporary migration directory on central server..."
& ssh @SshOptions -i $SshKey "${SshUser}@${Server}" "rm -rf $RemoteMigrationRoot && mkdir -p $RemoteMigrationRoot"
if ($LASTEXITCODE -ne 0) {
    throw "Step 1 failed: could not prepare the temporary migration directory on the server."
}
Write-Host "[1/6] OK"

Write-Host "[2/6] Uploading current ProcRun migration code..."
& scp @SshOptions -r -i $SshKey $LocalProcrunPackage "${SshUser}@${Server}:${RemoteMigrationRoot}/"
if ($LASTEXITCODE -ne 0) {
    & ssh @SshOptions -i $SshKey "${SshUser}@${Server}" "rm -rf $RemoteMigrationRoot" | Out-Null
    throw "Step 2 failed: could not copy the current ProcRun migration code to the server."
}
Write-Host "[2/6] OK"

$remoteMigration = @"
set -e
echo '[remote] Starting canonical migrations' >&2
ACL_BACKUP=/tmp/procrun-web-migrate.acl
cleanup() {
    if [ -f "`$ACL_BACKUP" ]; then
        setfacl --restore="`$ACL_BACKUP" >/dev/null 2>&1 || true
        rm -f "`$ACL_BACKUP"
    fi
    rm -rf $RemoteMigrationRoot
}
trap cleanup EXIT

if ! command -v getfacl >/dev/null 2>&1 || ! command -v setfacl >/dev/null 2>&1; then
    echo '[remote] ERROR: getfacl/setfacl are required for temporary least-privilege migration access.' >&2
    exit 41
fi

getfacl -p /opt/procrun /opt/procrun/venv /opt/procrun/venv/bin > "`$ACL_BACKUP"
setfacl -m u:postgres:--x /opt/procrun
setfacl -m u:postgres:--x /opt/procrun/venv
setfacl -m u:postgres:--x /opt/procrun/venv/bin

if ! sudo -u postgres test -x /opt/procrun/venv/bin/python; then
    echo '[remote] ERROR: postgres still cannot execute the production virtualenv Python after temporary ACL grant.' >&2
    exit 42
fi

sudo -u postgres env PYTHONPATH=$RemoteMigrationRoot PGOPTIONS='-c lock_timeout=15s -c statement_timeout=60s' /opt/procrun/venv/bin/python -c 'import psycopg; from procrun.migrations import apply_all_migrations; conn=psycopg.connect("dbname=procrun"); apply_all_migrations(conn); conn.close()'
echo '[remote] Migrations completed; verifying required tables' >&2
sudo -u postgres psql -d procrun -Atqc "SELECT CASE WHEN to_regclass('procrun.procurement_observations') IS NOT NULL AND to_regclass('procrun.sync_runs') IS NOT NULL AND to_regclass('procrun.accounts') IS NOT NULL THEN 'READY' ELSE 'MISSING' END;"
"@

$remoteMigrationLf = $remoteMigration.Replace("`r`n", "`n").Replace("`r", "")
[System.IO.File]::WriteAllText(
    $LocalMigrationScript,
    $remoteMigrationLf,
    [System.Text.UTF8Encoding]::new($false)
)

try {
    Write-Host "[3/6] Uploading migration runner..."
    & scp @SshOptions -i $SshKey $LocalMigrationScript "${SshUser}@${Server}:${RemoteMigrationScript}"
    if ($LASTEXITCODE -ne 0) {
        throw "Step 3 failed: could not copy the migration runner to the server."
    }
    Write-Host "[3/6] OK"

    Write-Host "[4/6] Running and verifying central database migrations (hard timeout: 90 seconds)..."
    $migrationResult = & ssh @SshOptions -i $SshKey "${SshUser}@${Server}" "timeout 90s bash $RemoteMigrationScript"
    $migrationExit = $LASTEXITCODE
    if ($migrationExit -eq 124) {
        throw "Step 4 timed out after 90 seconds. No further bootstrap steps were attempted."
    }
    if ($migrationExit -ne 0) {
        throw "Step 4 failed: central database migrations/verification returned exit code $migrationExit."
    }
    if (-not $migrationResult -or (($migrationResult | Select-Object -Last 1).Trim() -ne "READY")) {
        throw "Step 4 failed: central database schema verification did not return READY."
    }
    Write-Host "[4/6] OK - central database schema is ready."
}
finally {
    Remove-Item $LocalMigrationScript -Force -ErrorAction SilentlyContinue
    & ssh @SshOptions -i $SshKey "${SshUser}@${Server}" "rm -f $RemoteMigrationScript; rm -rf $RemoteMigrationRoot; if [ -f /tmp/procrun-web-migrate.acl ]; then setfacl --restore=/tmp/procrun-web-migrate.acl >/dev/null 2>&1 || true; rm -f /tmp/procrun-web-migrate.acl; fi" | Out-Null
}

Write-Host "[5/6] Uploading least-privilege web-development role definition..."
& scp @SshOptions -i $SshKey $SqlFile "${SshUser}@${Server}:${RemoteSql}"
if ($LASTEXITCODE -ne 0) {
    throw "Step 5 failed: could not copy role definition to the server."
}
Write-Host "[5/6] OK"

try {
    Write-Host "[6/6] Applying grants and setting the procrun_web_dev password..."
    Write-Host "      PostgreSQL remains loopback-only. The password prompt is interactive by design."
    & ssh @SshOptions -t -i $SshKey "${SshUser}@${Server}" "sudo -u postgres psql -d procrun -f $RemoteSql && sudo -u postgres psql -d procrun -c '\password procrun_web_dev'"
    if ($LASTEXITCODE -ne 0) {
        throw "Step 6 failed: remote role setup failed."
    }
}
finally {
    & ssh @SshOptions -i $SshKey "${SshUser}@${Server}" "rm -f $RemoteSql" | Out-Null
}

Write-Host "[6/6] OK"
Write-Host "Remote web-development access is configured."
Write-Host "From web/, run: npm run dev:remote"
