param(
    [string]$ServerName = "procrun-benchmark"
)

$ErrorActionPreference = "Stop"

if (-not (Get-Command hcloud -ErrorAction SilentlyContinue)) {
    throw "hcloud CLI is required."
}

if (-not $env:HCLOUD_TOKEN) {
    throw "HCLOUD_TOKEN must be set in the current PowerShell session."
}

& hcloud server describe $ServerName *> $null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Server '$ServerName' does not exist; nothing to delete."
    exit 0
}

& hcloud server delete $ServerName
if ($LASTEXITCODE -ne 0) {
    throw "Hetzner server deletion failed."
}

Write-Host "Deleted $ServerName. Billing for that server is stopped."
