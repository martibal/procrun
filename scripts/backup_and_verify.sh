#!/usr/bin/env bash
set -euo pipefail

BACKUP_DIR="${PROCRUN_BACKUP_DIR:-/var/backups/procrun}"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
BACKUP="$BACKUP_DIR/procrun-$STAMP.dump"
RESTORE_DB="procrun_restore_${STAMP//[^0-9]/}"

# The backup service runs as root, while pg_dump/pg_restore run as the local postgres user.
# Keep the directory non-public but traversable/readable by postgres for restore verification.
install -d -o root -g postgres -m 0750 "$BACKUP_DIR"

as_postgres() {
  runuser -u postgres -- "$@"
}

cleanup() {
  as_postgres dropdb --if-exists "$RESTORE_DB" >/dev/null 2>&1 || true
}
trap cleanup EXIT

# Root owns the shell redirection, so postgres does not need directory write permission.
as_postgres pg_dump --format=custom --no-owner --no-acl procrun > "$BACKUP"
chown root:postgres "$BACKUP"
chmod 0640 "$BACKUP"

test -s "$BACKUP"
as_postgres createdb "$RESTORE_DB"
as_postgres pg_restore --exit-on-error --no-owner --no-acl --dbname="$RESTORE_DB" "$BACKUP"

MIGRATIONS="$(as_postgres psql -Atqc "SELECT count(*) FROM procrun.schema_migrations" "$RESTORE_DB")"
if [[ -z "$MIGRATIONS" || "$MIGRATIONS" -lt 1 ]]; then
  echo "restore verification failed: no ProcRun schema migration found" >&2
  exit 1
fi

MANIFESTS="$(as_postgres psql -Atqc "SELECT count(*) FROM procrun.run_manifests" "$RESTORE_DB")"
echo "backup=$BACKUP migrations=$MIGRATIONS manifests=$MANIFESTS restore_verified=true"

# Logical backups are a second recovery path in addition to provider server backups.
# Keep two weeks locally; provider backups retain their own seven-slot rotation.
find "$BACKUP_DIR" -maxdepth 1 -type f -name 'procrun-*.dump' -mtime +14 -delete
