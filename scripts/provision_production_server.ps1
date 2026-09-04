param(
    [string]$ServerName = "procrun-prod",
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
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$CloudInit = Join-Path $RepoRoot "infra\production\cloud-init.yaml"
$ComplianceGate = Join-Path $PSScriptRoot "check_compliance_gate.py"

foreach ($Command in @("python", "git", "hcloud", "ssh", "scp")) {
    if (-not (Get-Command $Command -ErrorAction SilentlyContinue)) {
        throw "$Command is required for ProcRun production provisioning."
    }
}
if (-not $env:HCLOUD_TOKEN) {
    throw "HCLOUD_TOKEN must be set in the current PowerShell session."
}

& python $ComplianceGate --service hetzner_cloud
if ($LASTEXITCODE -ne 0) {
    throw "Hetzner compliance review is not approved. No server was created."
}

Push-Location $RepoRoot
try {
    $Dirty = (& git status --porcelain)
    if ($LASTEXITCODE -ne 0) { throw "Unable to inspect Git working tree." }
    if ($Dirty) { throw "Production provisioning requires a clean committed Git tree." }
    $Commit = (& git rev-parse HEAD).Trim()
    if ($LASTEXITCODE -ne 0 -or -not $Commit) { throw "Unable to resolve deployment commit." }
}
finally {
    Pop-Location
}

function Get-HetznerServers {
    $json = & hcloud server list -o json 2>$null
    if ($LASTEXITCODE -ne 0) { throw "Unable to query existing Hetzner servers." }
    return @($json | ConvertFrom-Json)
}

if ((Get-HetznerServers) | Where-Object { $_.name -eq $ServerName }) {
    throw "Server '$ServerName' already exists. Refusing to create a duplicate billable runtime."
}

$Created = $false
for ($Attempt = 1; $Attempt -le $CreateAttempts; $Attempt++) {
    $CreateOutput = & hcloud server create `
        --name $ServerName `
        --type $ServerType `
        --image $Image `
        --location $Location `
        --ssh-key $SshKey `
        --label "project=procrun" `
        --label "purpose=production-delivery" `
        --label "ephemeral=false" `
        --user-data-from-file $CloudInit 2>&1
    $Exit = $LASTEXITCODE
    if ($Exit -eq 0) {
        $CreateOutput | ForEach-Object { Write-Host $_ }
        $Created = $true
        break
    }
    if ((Get-HetznerServers) | Where-Object { $_.name -eq $ServerName }) {
        throw "Create returned an error but '$ServerName' exists. Refusing to retry a billable create."
    }
    $Message = ($CreateOutput | Out-String).Trim()
    if ($Message -notmatch "resource_unavailable" -or $Attempt -eq $CreateAttempts) {
        throw "Hetzner create failed without a safe automatic fallback: $Message"
    }
    Start-Sleep -Seconds $RetryDelaySeconds
}
if (-not $Created) { throw "Production server creation did not complete." }

$IpAddress = (& hcloud server ip $ServerName).Trim()
if ($LASTEXITCODE -ne 0 -or -not $IpAddress) {
    throw "Server exists but its IP address could not be resolved."
}

# Provider backups are a separate recovery path from ProcRun's verified logical pg_dump.
& hcloud server enable-backup $ServerName
if ($LASTEXITCODE -ne 0) {
    throw "Production server was created but daily Hetzner backups could not be enabled."
}

$TempArchive = Join-Path ([System.IO.Path]::GetTempPath()) "procrun-$Commit.tar.gz"
try {
    Push-Location $RepoRoot
    try {
        & git archive --format=tar.gz --output=$TempArchive HEAD
        if ($LASTEXITCODE -ne 0) { throw "git archive failed." }
    }
    finally { Pop-Location }

    $SshOptions = @("-o", "StrictHostKeyChecking=accept-new", "-o", "ConnectTimeout=15")
    $Ready = $false
    for ($i = 1; $i -le 40; $i++) {
        & ssh @SshOptions "root@$IpAddress" "cloud-init status --wait >/dev/null 2>&1"
        if ($LASTEXITCODE -eq 0) { $Ready = $true; break }
        Start-Sleep -Seconds 10
    }
    if (-not $Ready) { throw "Server did not reach a completed cloud-init state." }

    & scp @SshOptions $TempArchive "root@${IpAddress}:/tmp/procrun-release.tar.gz"
    if ($LASTEXITCODE -ne 0) { throw "Release upload failed." }

    $Remote = @'
set -euo pipefail
COMMIT="__COMMIT__"
RELEASE="/opt/procrun/releases/$COMMIT"
install -d -o procrun -g procrun -m 0750 "$RELEASE"
tar -xzf /tmp/procrun-release.tar.gz -C "$RELEASE"
rm -f /tmp/procrun-release.tar.gz
python3 -m venv /opt/procrun/venv
/opt/procrun/venv/bin/python -m pip install --upgrade pip
/opt/procrun/venv/bin/python -m pip install -c "$RELEASE/requirements-runtime.lock" -e "$RELEASE"
ln -sfn "$RELEASE" /opt/procrun/current
chown -R procrun:procrun /opt/procrun
chmod 0750 /opt/procrun/current/scripts/run_live_delivery.py
chmod 0750 /opt/procrun/current/scripts/backup_and_verify.sh
install -m 0644 /opt/procrun/current/infra/production/procrun-delivery.service /etc/systemd/system/procrun-delivery.service
install -m 0644 /opt/procrun/current/infra/production/procrun-delivery.timer /etc/systemd/system/procrun-delivery.timer
install -m 0644 /opt/procrun/current/infra/production/procrun-backup.service /etc/systemd/system/procrun-backup.service
install -m 0644 /opt/procrun/current/infra/production/procrun-backup.timer /etc/systemd/system/procrun-backup.timer
systemctl daemon-reload

# First real run is the production acceptance gate. Timers are enabled only after it succeeds.
systemctl start procrun-delivery.service
systemctl is-failed --quiet procrun-delivery.service && exit 1 || true
test -s /var/lib/procrun/published/runway.jsonl
systemctl start procrun-backup.service
systemctl is-failed --quiet procrun-backup.service && exit 1 || true
systemctl enable --now procrun-delivery.timer procrun-backup.timer

# No ProcRun application/database listener may be publicly exposed before web phase.
if ss -lnt | awk 'NR>1 {print $4}' | grep -Ev '(^127\.0\.0\.1:5432$|^\[::1\]:5432$|:22$)' | grep -q .; then
  echo "Unexpected public TCP listener detected" >&2
  ss -lnt >&2
  exit 1
fi

runuser -u postgres -- psql -d procrun -Atqc "SELECT count(*) FROM procrun.run_manifests" | grep -Eq '^[1-9][0-9]*$'
systemctl is-enabled --quiet procrun-delivery.timer
systemctl is-enabled --quiet procrun-backup.timer
echo "PROCRUN_PRODUCTION_ACCEPTANCE=PASS commit=$COMMIT"
'@
    $Remote = $Remote.Replace("__COMMIT__", $Commit)
    $Remote | ssh @SshOptions "root@$IpAddress" "bash -s"
    if ($LASTEXITCODE -ne 0) {
        throw "Production live acceptance failed. The server remains fail-closed for inspection; A20 stays BLOCKED."
    }
}
finally {
    Remove-Item $TempArchive -Force -ErrorAction SilentlyContinue
}

Write-Host "ProcRun production runtime accepted on $ServerName ($IpAddress), commit $Commit."
Write-Host "This does not by itself change A20; repository CI/status reconciliation must still pass."
