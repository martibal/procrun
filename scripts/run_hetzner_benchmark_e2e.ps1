param(
    [Parameter(Mandatory = $true)]
    [string]$SshKey,
    [string]$ServerName = "procrun-benchmark",
    [string]$ServerType = "cx33",
    [string]$Location = "hel1",
    [string]$Image = "ubuntu-24.04",
    [string]$IdentityFile = "",
    [switch]$KeepServer
)

$ErrorActionPreference = "Stop"
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$ProvisionScript = Join-Path $PSScriptRoot "provision_benchmark_server.ps1"
$DestroyScript = Join-Path $PSScriptRoot "destroy_benchmark_server.ps1"

function Require-Command {
    param([string]$Name)
    if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
        throw "Required command '$Name' was not found."
    }
}

Require-Command "hcloud"
Require-Command "git"
Require-Command "ssh"
Require-Command "scp"

if (-not $env:HCLOUD_TOKEN) {
    throw "HCLOUD_TOKEN must be set in the current PowerShell session."
}

if (-not (Test-Path (Join-Path $RepoRoot "pyproject.toml"))) {
    throw "Run this script from a complete ProcRun repository checkout."
}

$Dirty = & git -C $RepoRoot status --porcelain
if ($LASTEXITCODE -ne 0) {
    throw "Could not inspect the repository state."
}
if ($Dirty) {
    throw "Repository has uncommitted changes. Benchmark only committed, reproducible code."
}

$ArchivePath = Join-Path ([System.IO.Path]::GetTempPath()) (
    "procrun-benchmark-{0}.zip" -f ([guid]::NewGuid().ToString("N"))
)
$ServerCreated = $false
$BenchmarkSucceeded = $false
$Remote = $null

$SshOptions = @(
    "-o", "BatchMode=yes",
    "-o", "StrictHostKeyChecking=accept-new",
    "-o", "ConnectTimeout=5"
)
if ($IdentityFile) {
    $ResolvedIdentity = (Resolve-Path $IdentityFile).Path
    $SshOptions += @("-i", $ResolvedIdentity)
}

try {
    & $ProvisionScript `
        -ServerName $ServerName `
        -ServerType $ServerType `
        -Location $Location `
        -Image $Image `
        -SshKey $SshKey
    $ServerCreated = $true

    $IpAddress = (& hcloud server ip $ServerName).Trim()
    if ($LASTEXITCODE -ne 0 -or -not $IpAddress) {
        throw "Could not resolve the new server IPv4 address."
    }
    $Remote = "root@$IpAddress"

    $SshReady = $false
    for ($Attempt = 0; $Attempt -lt 60; $Attempt++) {
        $ProbeErrorActionPreference = $ErrorActionPreference
        try {
            $ErrorActionPreference = "SilentlyContinue"
            & ssh @SshOptions $Remote "true" *> $null
            $SshExitCode = $LASTEXITCODE
        }
        finally {
            $ErrorActionPreference = $ProbeErrorActionPreference
        }

        if ($SshExitCode -eq 0) {
            $SshReady = $true
            break
        }
        Start-Sleep -Seconds 2
    }
    if (-not $SshReady) {
        throw "SSH did not become reachable."
    }

    & ssh @SshOptions $Remote "cloud-init status --wait"
    if ($LASTEXITCODE -ne 0) {
        throw "cloud-init failed on the benchmark host."
    }

    & git -C $RepoRoot archive --format=zip -o $ArchivePath HEAD
    if ($LASTEXITCODE -ne 0 -or -not (Test-Path $ArchivePath)) {
        throw "Could not create the committed-code benchmark archive."
    }

    & scp @SshOptions $ArchivePath "${Remote}:/root/procrun.zip"
    if ($LASTEXITCODE -ne 0) {
        throw "Could not upload the committed-code benchmark archive."
    }

    $RemoteBenchmark = @'
set -euo pipefail
rm -rf /root/procrun
mkdir -p /root/procrun
unzip -q /root/procrun.zip -d /root/procrun
cd /root/procrun
bash scripts/bootstrap_benchmark_host.sh
bash scripts/download_benchmark_model.sh
bash scripts/run_target_benchmark.sh
tar -C /root/.local/share/procrun-benchmark/results \
  -czf /root/procrun-benchmark-results.tgz .
'@
    & ssh @SshOptions $Remote $RemoteBenchmark
    if ($LASTEXITCODE -ne 0) {
        throw "Remote benchmark execution failed."
    }

    $Timestamp = (Get-Date).ToUniversalTime().ToString("yyyyMMddTHHmmssZ")
    $LocalResultsDir = Join-Path $RepoRoot "data\exports\model-benchmark"
    New-Item -ItemType Directory -Force -Path $LocalResultsDir | Out-Null
    $LocalBundle = Join-Path $LocalResultsDir "target-benchmark-$Timestamp.tgz"

    & scp @SshOptions "${Remote}:/root/procrun-benchmark-results.tgz" $LocalBundle
    if ($LASTEXITCODE -ne 0 -or -not (Test-Path $LocalBundle)) {
        throw "Benchmark completed remotely, but the result bundle was not copied home."
    }

    $BenchmarkSucceeded = $true
    Write-Host "Benchmark result bundle: $LocalBundle"
}
finally {
    Remove-Item $ArchivePath -Force -ErrorAction SilentlyContinue

    if ($ServerCreated -and $BenchmarkSucceeded -and -not $KeepServer) {
        & $DestroyScript -ServerName $ServerName
    }
    elseif ($ServerCreated -and $BenchmarkSucceeded) {
        Write-Warning "Benchmark succeeded, but $ServerName was kept because -KeepServer was used."
    }
    elseif ($ServerCreated) {
        Write-Warning (
            "Benchmark did not complete. $ServerName is intentionally still running for diagnostics " +
            "and continues billing until explicitly deleted."
        )
        Write-Warning (
            "Delete with: .\scripts\destroy_benchmark_server.ps1 -ServerName $ServerName"
        )
    }
}
