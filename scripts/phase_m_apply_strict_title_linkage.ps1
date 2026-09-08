param(
    [string]$Server = "62.238.117.62",
    [string]$SshUser = "root",
    [int]$TimeoutMinutes = 15
)
$ErrorActionPreference = "Stop"
$SshKey = Join-Path $env:USERPROFILE ".ssh\procrun_hetzner"
$LocalScript = Join-Path $PSScriptRoot "phase_m_apply_strict_title_linkage.py"
$Remote = "/tmp/procrun-phase-m-strict-title.py"
if (-not (Test-Path $SshKey)) { throw "Missing SSH key: $SshKey" }
if (-not (Test-Path $LocalScript)) { throw "Missing strict-title linkage script: $LocalScript" }
$opts = @("-o","ConnectTimeout=10","-o","ConnectionAttempts=1","-o","ServerAliveInterval=15","-o","ServerAliveCountMax=3","-o","BatchMode=yes")
Write-Host "Phase M: applying pre-registered strict project-title linkage to stored evidence only."
Write-Host "No new source is contacted. No person, buyer, winner or contact field is read."
& scp @opts -i $SshKey $LocalScript "${SshUser}@${Server}:${Remote}"
if ($LASTEXITCODE -ne 0) { throw "Upload failed." }
try {
    $timeoutSeconds = $TimeoutMinutes * 60
    & ssh @opts -i $SshKey "${SshUser}@${Server}" "timeout ${timeoutSeconds}s sudo -u postgres env PYTHONPATH=/opt/procrun /opt/procrun/venv/bin/python $Remote --database-url 'dbname=procrun'"
    if ($LASTEXITCODE -eq 124) { throw "Strict-title linkage timed out after $TimeoutMinutes minutes." }
    if ($LASTEXITCODE -ne 0) { throw "Strict-title linkage failed with exit code $LASTEXITCODE." }
    Write-Host "Now run: .\scripts\phase_m_append_audit.ps1"
}
finally {
    & ssh @opts -i $SshKey "${SshUser}@${Server}" "rm -f $Remote" | Out-Null
}
