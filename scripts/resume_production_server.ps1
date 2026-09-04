param(
    [string]$ServerName = "procrun-prod"
)

$ErrorActionPreference = "Stop"
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$ComplianceGate = Join-Path $PSScriptRoot "check_compliance_gate.py"

foreach ($Command in @("python", "git", "hcloud", "ssh", "scp")) {
    if (-not (Get-Command $Command -ErrorAction SilentlyContinue)) {
        throw "$Command is required for ProcRun production resume."
    }
}
if (-not $env:HCLOUD_TOKEN) {
    throw "HCLOUD_TOKEN must be set in the current PowerShell session."
}

& python $ComplianceGate --service hetzner_cloud
if ($LASTEXITCODE -ne 0) {
    throw "Hetzner compliance review is not approved. Existing server was not changed."
}

Push-Location $RepoRoot
try {
    $Dirty = (& git status --porcelain)
    if ($LASTEXITCODE -ne 0) { throw "Unable to inspect Git working tree." }
    if ($Dirty) { throw "Production resume requires a clean committed Git tree." }
    $Commit = (& git rev-parse HEAD).Trim()
    if ($LASTEXITCODE -ne 0 -or -not $Commit) { throw "Unable to resolve deployment commit." }
}
finally {
    Pop-Location
}

$ServerJson = & hcloud server list -o json 2>$null
if ($LASTEXITCODE -ne 0) { throw "Unable to query existing Hetzner servers." }
$Matches = @($ServerJson | ConvertFrom-Json | Where-Object { $_.name -eq $ServerName })
if ($Matches.Count -ne 1) {
    throw "Expected exactly one existing server named '$ServerName'; found $($Matches.Count)."
}
$Server = $Matches[0]
if ($Server.labels.project -ne "procrun" -or $Server.labels.purpose -ne "production-delivery" -or $Server.labels.ephemeral -ne "false") {
    throw "Existing server '$ServerName' does not carry the frozen ProcRun production labels; refusing to reuse it."
}
if ($Server.status -ne "running") {
    throw "Existing server '$ServerName' is not running (status=$($Server.status))."
}

$IpAddress = (& hcloud server ip $ServerName).Trim()
if ($LASTEXITCODE -ne 0 -or -not $IpAddress) {
    throw "Existing server IP address could not be resolved."
}

# The initial create attempt stopped before this step, so ensure provider backups are enabled now.
$OldPreference = $ErrorActionPreference
$ErrorActionPreference = "Continue"
$BackupOutput = & hcloud server enable-backup $ServerName 2>&1
$BackupExit = $LASTEXITCODE
$ErrorActionPreference = $OldPreference
if ($BackupExit -ne 0 -and (($BackupOutput | Out-String) -notmatch "already")) {
    throw "Could not enable Hetzner backups: $(($BackupOutput | Out-String).Trim())"
}
$BackupOutput | ForEach-Object { Write-Host $_ }

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
        $OldPreference = $ErrorActionPreference
        $ErrorActionPreference = "Continue"
        & ssh @SshOptions "root@$IpAddress" "cloud-init status --wait >/dev/null 2>&1"
        $SshExit = $LASTEXITCODE
        $ErrorActionPreference = $OldPreference
        if ($SshExit -eq 0) { $Ready = $true; break }
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

if ! systemctl start procrun-delivery.service; then
  echo "=== procrun-delivery.service failure ===" >&2
  systemctl status procrun-delivery.service --no-pager >&2 || true
  journalctl -u procrun-delivery.service -n 120 --no-pager >&2 || true
  exit 1
fi
test -s /var/lib/procrun/published/runway.jsonl
/opt/procrun/venv/bin/python - <<'PY'
import json
from pathlib import Path
path = Path('/var/lib/procrun/published/runway.jsonl')
rows = [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines() if line]
if not rows:
    raise SystemExit('customer JSONL parsed but contained zero rows')
print(f'CUSTOMER_JSONL_PARSE=PASS rows={len(rows)}')
PY

if ! systemctl start procrun-backup.service; then
  echo "=== procrun-backup.service failure ===" >&2
  systemctl status procrun-backup.service --no-pager >&2 || true
  journalctl -u procrun-backup.service -n 120 --no-pager >&2 || true
  exit 1
fi
systemctl enable --now procrun-delivery.timer procrun-backup.timer

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
    $OldPreference = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    $Remote | ssh @SshOptions "root@$IpAddress" "bash -s"
    $RemoteExit = $LASTEXITCODE
    $ErrorActionPreference = $OldPreference
    if ($RemoteExit -ne 0) {
        throw "Production live acceptance failed. Server remains fail-closed for inspection; A20 stays BLOCKED."
    }
}
finally {
    Remove-Item $TempArchive -Force -ErrorAction SilentlyContinue
}

Write-Host "ProcRun production runtime accepted on existing $ServerName ($IpAddress), commit $Commit."
Write-Host "PROCRUN_PRODUCTION_ACCEPTANCE=PASS"
