param(
    [string]$ServerName = "procrun-benchmark",
    [string]$ServerType = "cx33",
    [string]$Location = "hel1",
    [string]$Image = "ubuntu-24.04",
    [Parameter(Mandatory = $true)]
    [string]$SshKey
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

& hcloud server describe $ServerName *> $null
if ($LASTEXITCODE -eq 0) {
    throw "Server '$ServerName' already exists. Refusing to create a duplicate billable server."
}

& hcloud server create `
    --name $ServerName `
    --type $ServerType `
    --image $Image `
    --location $Location `
    --ssh-key $SshKey `
    --label "project=procrun" `
    --label "purpose=model-benchmark" `
    --label "ephemeral=true" `
    --user-data-from-file $CloudInit

if ($LASTEXITCODE -ne 0) {
    throw "Hetzner server creation failed. No fallback server type is selected automatically."
}

$IpAddress = (& hcloud server ip $ServerName).Trim()
Write-Host "Created $ServerName at $IpAddress"
Write-Host "SSH: ssh root@$IpAddress"
Write-Host "After login: cloud-init status --wait"
Write-Host "Delete after benchmark: .\scripts\destroy_benchmark_server.ps1 -ServerName $ServerName"
