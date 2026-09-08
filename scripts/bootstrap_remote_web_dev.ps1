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

if (-not (Test-Path $SshKey)) {
    throw "Missing SSH key: $SshKey"
}

if (-not (Test-Path $SqlFile)) {
    throw "Missing SQL role definition: $SqlFile"
}

if (-not (Test-Path $LocalProcrunPackage)) {
    throw "Missing local ProcRun Python package: $LocalProcrunPackage"
}

Write-Host "Checking the central ProcRun database schema before granting web-development access..."
Write-Host "Uploading the current local migration code to a temporary server directory..."

& ssh -i $SshKey "${SshUser}@${Server}" "rm -rf $RemoteMigrationRoot && mkdir -p $RemoteMigrationRoot"
if ($LASTEXITCODE -ne 0) {
    throw "Could not prepare the temporary migration directory on the server."
}

& scp -r -i $SshKey $LocalProcrunPackage "${SshUser}@${Server}:${RemoteMigrationRoot}/"
if ($LASTEXITCODE -ne 0) {
    & ssh -i $SshKey "${SshUser}@${Server}" "rm -rf $RemoteMigrationRoot" | Out-Null
    throw "Could not copy the current ProcRun migration code to the server."
}

$remoteMigration = @"
set -e
cleanup() {
    rm -rf $RemoteMigrationRoot
}
trap cleanup EXIT
sudo -u postgres env PYTHONPATH=$RemoteMigrationRoot /opt/procrun/venv/bin/python -c 'import psycopg; from procrun.migrations import apply_all_migrations; conn=psycopg.connect("dbname=procrun"); apply_all_migrations(conn); conn.close()'
sudo -u postgres psql -d procrun -Atqc "SELECT CASE WHEN to_regclass('procrun.procurement_observations') IS NOT NULL AND to_regclass('procrun.sync_runs') IS NOT NULL AND to_regclass('procrun.accounts') IS NOT NULL THEN 'READY' ELSE 'MISSING' END;"
"@

$remoteMigrationLf = $remoteMigration.Replace("`r`n", "`n").Replace("`r", "")
[System.IO.File]::WriteAllText(
    $LocalMigrationScript,
    $remoteMigrationLf,
    [System.Text.UTF8Encoding]::new($false)
)

try {
    & scp -i $SshKey $LocalMigrationScript "${SshUser}@${Server}:${RemoteMigrationScript}"
    if ($LASTEXITCODE -ne 0) {
        throw "Could not copy the migration bootstrap to the server."
    }

    $migrationResult = & ssh -i $SshKey "${SshUser}@${Server}" "bash $RemoteMigrationScript"
    if ($LASTEXITCODE -ne 0) {
        throw "Could not apply/verify the required central database migrations."
    }
}
finally {
    Remove-Item $LocalMigrationScript -Force -ErrorAction SilentlyContinue
    & ssh -i $SshKey "${SshUser}@${Server}" "rm -f $RemoteMigrationScript; rm -rf $RemoteMigrationRoot" | Out-Null
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
