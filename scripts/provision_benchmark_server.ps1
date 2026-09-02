param(
    [string]$ServerName = "procrun-benchmark",
    [string]$ServerType = "cx33",
    [string]$Location = "hel1",
    [string]$Image = "ubuntu-24.04",
    [Parameter(Mandatory = $true)]
    [string]$SshKey,
    [ValidateRange(1, 20)]
    [int]$CreateAttempts = 6,
    [ValidateRange(1, 300)]
    [int]$RetryDelaySeconds = 15
)

$ErrorActionPreference = "Stop"
$CloudInit = Join-Path $PSScriptRoot "..\infra\benchmark\cloud-init.yaml"
$ComplianceGate = Join-Path $PSScriptRoot "check_compliance_gate.py"

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    throw "Python 3.12+ is required to run the repository compliance gate."
}

& python $ComplianceGate --service hetzner_cloud
if ($LASTEXITCODE -ne 0) {
    throw "Hetzner compliance review is not currently approved. No server was created."
}

if (-not (Get-Command hcloud -ErrorAction SilentlyContinue)) {
    throw "hcloud CLI is required. Install the official Hetzner Cloud CLI before proceeding."
}

if (-not $env:HCLOUD_TOKEN) {
    throw "HCLOUD_TOKEN must be set in the current PowerShell session."
}

function Get-HetznerServers {
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
        throw "Unable to query existing Hetzner servers."
    }

    try {
        return @($serverJson | ConvertFrom-Json)
    }
    catch {
        throw "Hetzner server lookup returned invalid JSON."
    }
}

$ExistingServers = @(Get-HetznerServers)
if ($ExistingServers | Where-Object { $_.name -eq $ServerName }) {
    throw "Server '$ServerName' already exists. Refusing to create a duplicate billable server."
}

$ServerCreated = $false
for ($Attempt = 1; $Attempt -le $CreateAttempts; $Attempt++) {
    $previousErrorActionPreference = $ErrorActionPreference
    try {
        $ErrorActionPreference = "Continue"
        $CreateOutput = & hcloud server create `
            --name $ServerName `
            --type $ServerType `
            --image $Image `
            --location $Location `
            --ssh-key $SshKey `
            --label "project=procrun" `
            --label "purpose=model-benchmark" `
            --label "ephemeral=true" `
            --user-data-from-file $CloudInit 2>&1
        $CreateExitCode = $LASTEXITCODE
    }
    finally {
        $ErrorActionPreference = $previousErrorActionPreference
    }

    if ($CreateExitCode -eq 0) {
        $CreateOutput | ForEach-Object { Write-Host $_ }
        $ServerCreated = $true
        break
    }

    $CreateMessage = ($CreateOutput | Out-String).Trim()

    # A create action can fail after Hetzner has already allocated a server ID.
    # Never retry while a same-name billable resource exists.
    $ServersAfterFailure = @(Get-HetznerServers)
    if ($ServersAfterFailure | Where-Object { $_.name -eq $ServerName }) {
        throw "Hetzner create returned an error but server '$ServerName' now exists. Refusing to retry or create a duplicate. Inspect or delete that server explicitly."
    }

    if ($CreateMessage -notmatch "resource_unavailable") {
        throw "Hetzner server creation failed: $CreateMessage No fallback server type or location is selected automatically."
    }

    if ($Attempt -eq $CreateAttempts) {
        throw "Hetzner capacity remained unavailable for $ServerType in $Location after $CreateAttempts attempts. No fallback server type or location is selected automatically."
    }

    Write-Host "Hetzner capacity unavailable for $ServerType in $Location (attempt $Attempt/$CreateAttempts). Retrying the same approved target after $RetryDelaySeconds seconds."
    Start-Sleep -Seconds $RetryDelaySeconds
}

if (-not $ServerCreated) {
    throw "Hetzner server creation did not complete."
}

$IpAddress = (& hcloud server ip $ServerName).Trim()
if ($LASTEXITCODE -ne 0 -or -not $IpAddress) {
    throw "Server was created but its IP address could not be resolved."
}

Write-Host "Created $ServerName at $IpAddress"
Write-Host "SSH: ssh root@$IpAddress"
Write-Host "After login: cloud-init status --wait"
Write-Host "Delete after benchmark: .\scripts\destroy_benchmark_server.ps1 -ServerName $ServerName"
