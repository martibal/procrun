param(
    [string]$ServerName = "procrun-prod",
    [string]$SshPrivateKey = (Join-Path $HOME ".ssh\procrun_hetzner")
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
if (-not (Test-Path -LiteralPath $SshPrivateKey -PathType Leaf)) {
    throw "ProcRun SSH private key not found: $SshPrivateKey"
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

# Ensure provider backups are enabled before any deployment changes.
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

    $SshOptions = @(
        "-i", $SshPrivateKey,
        "-o", "IdentitiesOnly=yes",
        "-o", "BatchMode=yes",
        "-o", "StrictHostKeyChecking=accept-new",
        "-o", "ConnectTimeout=15"
    )

    $Ready = $false
    $CloudInitStatus = $null
    for ($i = 1; $i -le 12; $i++) {
        $OldPreference = $ErrorActionPreference
        $ErrorActionPreference = "Continue"
        $StatusOutput = & ssh @SshOptions "root@$IpAddress" "cloud-init status 2>&1"
        $StatusExit = $LASTEXITCODE
        $ErrorActionPreference = $OldPreference
        $CloudInitStatus = ($StatusOutput | Out-String).Trim()

        if ($CloudInitStatus -match "status:\s*done") {
            $Ready = $true
            break
        }
        if ($CloudInitStatus -match "status:\s*(error|degraded|disabled)") {
            break
        }
        if ($StatusExit -ne 0 -and $CloudInitStatus -notmatch "status:\s*(running|not run)") {
            break
        }
        Start-Sleep -Seconds 10
    }

    if (-not $Ready) {
        Write-Host "=== cloud-init status ==="
        if ($CloudInitStatus) { Write-Host $CloudInitStatus }
        $OldPreference = $ErrorActionPreference
        $ErrorActionPreference = "Continue"
        & ssh @SshOptions "root@$IpAddress" "echo '=== cloud-init status --long ==='; cloud-init status --long 2>&1 || true; echo '=== cloud-init result ==='; cat /var/lib/cloud/data/result.json 2>/dev/null || true; echo '=== cloud-init log tail ==='; tail -n 120 /var/log/cloud-init-output.log 2>/dev/null || true"
        $ErrorActionPreference = $OldPreference
        throw "Server cloud-init is not in a clean completed state. A20 stays BLOCKED."
    }

    & scp @SshOptions $TempArchive "root@${IpAddress}:/tmp/procrun-release.tar.gz"
    if ($LASTEXITCODE -ne 0) { throw "Release upload failed." }

    $Remote = @'
set -euo pipefail
COMMIT="__COMMIT__"
RELEASE="/opt/procrun/releases/$COMMIT"

# Recover idempotently from an interrupted/partial initial cloud-init bootstrap.
if ! getent group procrun >/dev/null 2>&1; then
  groupadd --system procrun
fi
if ! id -u procrun >/dev/null 2>&1; then
  useradd --system --gid procrun --home-dir /var/lib/procrun --no-create-home --shell /usr/sbin/nologin procrun
fi

export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install -y python3 python3-venv python3-pip postgresql postgresql-client ufw ca-certificates curl jq rsync openssl
systemctl enable --now postgresql

install -d -o procrun -g procrun -m 0750 /opt/procrun
install -d -o procrun -g procrun -m 0750 /var/lib/procrun
install -d -o procrun -g procrun -m 0750 /var/lib/procrun/published
install -d -o root -g procrun -m 0750 /var/backups/procrun
install -d -o root -g procrun -m 0750 /etc/procrun

if [ ! -s /etc/procrun/procrun.env ]; then
  DB_PASS="$(openssl rand -hex 24)"
  printf 'PROCRUN_DATABASE_URL=postgresql://procrun:%s@127.0.0.1:5432/procrun\n' "$DB_PASS" > /etc/procrun/procrun.env
  chmod 0640 /etc/procrun/procrun.env
  chown root:procrun /etc/procrun/procrun.env

  if runuser -u postgres -- psql -Atqc "SELECT 1 FROM pg_roles WHERE rolname='procrun'" | grep -qx 1; then
    runuser -u postgres -- psql -v ON_ERROR_STOP=1 -c "ALTER ROLE procrun LOGIN PASSWORD '$DB_PASS';"
  else
    runuser -u postgres -- psql -v ON_ERROR_STOP=1 -c "CREATE ROLE procrun LOGIN PASSWORD '$DB_PASS';"
  fi
  if ! runuser -u postgres -- psql -Atqc "SELECT 1 FROM pg_database WHERE datname='procrun'" | grep -qx 1; then
    runuser -u postgres -- createdb -O procrun procrun
  fi
else
  chown root:procrun /etc/procrun/procrun.env
  chmod 0640 /etc/procrun/procrun.env
  if ! runuser -u postgres -- psql -Atqc "SELECT 1 FROM pg_roles WHERE rolname='procrun'" | grep -qx 1; then
    echo "Existing /etc/procrun/procrun.env found but PostgreSQL role 'procrun' is missing; refusing to rotate credentials implicitly." >&2
    exit 1
  fi
  if ! runuser -u postgres -- psql -Atqc "SELECT 1 FROM pg_database WHERE datname='procrun'" | grep -qx 1; then
    runuser -u postgres -- createdb -O procrun procrun
  fi
fi

PGCONF="$(runuser -u postgres -- psql -Atqc 'show config_file')"
sed -ri "s/^#?listen_addresses\s*=.*/listen_addresses = '127.0.0.1'/" "$PGCONF"
systemctl restart postgresql

ufw default deny incoming
ufw default allow outgoing
ufw allow OpenSSH
ufw --force enable

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
    $RemoteLf = $Remote -replace "`r`n", "`n"
    $OldPreference = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    $RemoteLf | ssh @SshOptions "root@$IpAddress" "bash -s"
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
