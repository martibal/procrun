param(
    [string]$Server = "62.238.117.62",
    [string]$SshUser = "root"
)

$ErrorActionPreference = "Stop"

$SshKey = Join-Path $env:USERPROFILE ".ssh\procrun_hetzner"
$SqlFile = Join-Path $PSScriptRoot "configure_web_dev_role.sql"
$RemoteSql = "/tmp/procrun_web_dev_role.sql"

if (-not (Test-Path $SshKey)) {
    throw "Missing SSH key: $SshKey"
}

if (-not (Test-Path $SqlFile)) {
    throw "Missing SQL role definition: $SqlFile"
}

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
