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

# Query the server inventory instead of probing with `server describe`.
# Windows PowerShell promotes native stderr to a PowerShell error record; with
# ErrorActionPreference=Stop that can terminate the script before LASTEXITCODE
# is inspected. Temporarily use Continue around native calls, then handle their
# exit codes explicitly.
$previousErrorActionPreference = $ErrorActionPreference
try {
    $ErrorActionPreference = "Continue"
    $serverJson = & hcloud server list -o json 2>$null
    $lookupExitCode = $LASTEXITCODE
}
finally {
    $ErrorActionPreference = $previousErrorActionPreference
}

if ($lookupExitCode -ne 0) {
    throw "Hetzner server lookup failed."
}

try {
    $servers = @($serverJson | ConvertFrom-Json)
}
catch {
    throw "Hetzner server lookup returned invalid JSON."
}

$serverExists = @($servers | Where-Object { $_.name -eq $ServerName }).Count -gt 0
if (-not $serverExists) {
    Write-Host "Server '$ServerName' does not exist; nothing to delete."
    exit 0
}

try {
    $ErrorActionPreference = "Continue"
    & hcloud server delete $ServerName
    $deleteExitCode = $LASTEXITCODE
}
finally {
    $ErrorActionPreference = $previousErrorActionPreference
}

if ($deleteExitCode -ne 0) {
    throw "Hetzner server deletion failed."
}

Write-Host "Deleted $ServerName. Billing for that server is stopped."
