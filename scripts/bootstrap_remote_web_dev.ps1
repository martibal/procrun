param(
    [string]$Server = "62.238.117.62",
    [string]$SshUser = "root"
)

$ErrorActionPreference = "Stop"

$SshKey = Join-Path $env:USERPROFILE ".ssh\procrun_hetzner"
$SqlFile = Join-Path $PSScriptRoot "configure_web_dev_role.sql"
$RemoteSql = "/tmp/procrun_web_dev_role.sql"
$RemoteWorktree = "/tmp/procrun-web-migrate"

if (-not (Test-Path $SshKey)) {
    throw "Missing SSH key: $SshKey"
}

if (-not (Test-Path $SqlFile)) {
    throw "Missing SQL role definition: $SqlFile"
}

Write-Host "Checking the central ProcRun database schema before granting web-development access..."

$remoteMigration = @"
set -e
cd /opt/procrun
git fetch origin web/customer-site-foundation
git worktree remove --force $RemoteWorktree >/dev/null 2>&1 || true
git worktree add --detach $RemoteWorktree origin/web/customer-site-foundation >/dev/null
cleanup() {
    git -C /opt/procrun worktree remove --force $RemoteWorktree >/dev/null 2>&1 || true
}
trap cleanup EXIT
sudo -u postgres env PYTHONPATH=$RemoteWorktree/src /opt/procrun/venv/bin/python -c 'import psycopg; from procrun.migrations import apply_all_migrations; conn=psycopg.connect("dbname=procrun"); apply_all_migrations(conn); conn.close()'
sudo -u postgres psql -d procrun -Atqc "SELECT CASE WHEN to_regclass('procrun.procurement_observations') IS NOT NULL AND to_regclass('procrun.sync_runs') IS NOT NULL AND to_regclass('procrun.accounts') IS NOT NULL THEN 'READY' ELSE 'MISSING' END;"
"@

$migrationResult = & ssh -i $SshKey "${SshUser}@${Server}" $remoteMigration
if ($LASTEXITCODE -ne 0) {
    throw "Could not apply/verify the required central database migrations."
}

if (($migrationResult | Select-Object -Last 1).Trim() -ne "READY") {
    throw "Central database schema is still missing required web tables."
}

Write-Host "Central database schema is ready."
Write-Host "Copying the least-privilege web-development role definition to ProcRun production..."
& scp -i $SshKey $SqlFile "${SshUser}@${Server}:${RemoteSql}"
if ($LASTEXITCODE -ne 0) {
    throw "Could not copy role definition to the server."
}

try {
    Write-Host "Applying role grants. PostgreSQL remains bound to loopback only."
    & ssh -t -i $SshKey "${SshUser}@${Server}" "sudo -u postgres psql -d procrun -f $RemoteSql && sudo -u postgres psql -d procrun -c '\password procrun_web_dev'"
    if ($LASTEXITCODE -ne 0) {
        throw "Remote role setup failed."
    }
}
finally {
    & ssh -i $SshKey "${SshUser}@${Server}" "rm -f $RemoteSql" | Out-Null
}

Write-Host "Remote web-development access is configured."
Write-Host "From web/, run: npm run dev:remote"
