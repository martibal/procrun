from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_remote_web_role_is_narrow_and_excludes_unapproved_fields() -> None:
    sql = (REPO_ROOT / "scripts/configure_web_dev_role.sql").read_text(encoding="utf-8")

    assert "GRANT SELECT ON ALL TABLES" not in sql
    assert "municipality" not in sql
    assert "contracting_authority_name" not in sql
    assert "beneficiary" not in sql.lower()
    assert "correction_reason" not in sql
    assert "procrun_web_dev" in sql
    assert "REVOKE ALL PRIVILEGES ON ALL TABLES IN SCHEMA procrun" in sql


def test_remote_web_dev_uses_ssh_loopback_tunnel() -> None:
    script = (REPO_ROOT / "scripts/start_web_dev_remote.ps1").read_text(encoding="utf-8")

    assert "127.0.0.1:${LocalDbPort}:127.0.0.1:5432" in script
    assert "ExitOnForwardFailure=yes" in script
    assert "PROCRUN_DATABASE_URL" in script
    assert 'Read-Host "Password for PostgreSQL role $DbUser" -AsSecureString' in script
    assert "npm run dev" in script


def test_remote_web_dev_does_not_persist_database_secret() -> None:
    script = (REPO_ROOT / "scripts/start_web_dev_remote.ps1").read_text(encoding="utf-8")

    assert ".env.local" not in script
    assert "SetEnvironmentVariable" not in script
    assert "PROCRUN_DEV_DB_PASSWORD" in script
