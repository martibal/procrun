import re
import tomllib
from datetime import date
from pathlib import Path

import pytest

from procrun.compliance import (
    DIRECT_RUNTIME_DEPENDENCIES,
    EXTERNAL_SERVICE_CONTRACTS,
    RUNTIME_DEPENDENCIES,
    ComplianceExpiredError,
    ComplianceStatus,
    require_direct_dependency_reviews,
    require_external_service,
)

REPO_ROOT = Path(__file__).resolve().parents[1]


def _dependency_name(requirement: str) -> str:
    match = re.match(r"^[A-Za-z0-9_.-]+", requirement)
    if match is None:
        raise AssertionError(f"could not parse dependency requirement: {requirement}")
    return match.group(0).lower()


def _runtime_lock() -> dict[str, str]:
    result: dict[str, str] = {}
    lock_text = (REPO_ROOT / "requirements-runtime.lock").read_text(encoding="utf-8")
    for raw_line in lock_text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        name, separator, version = line.partition("==")
        assert separator == "==", f"runtime lock entry is not exact: {line}"
        result[name.lower()] = version
    return result


def test_every_direct_runtime_dependency_has_a_frozen_licence_record() -> None:
    pyproject = tomllib.loads((REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    requirements = pyproject["project"]["dependencies"]
    names = {_dependency_name(requirement) for requirement in requirements}
    assert names == set(DIRECT_RUNTIME_DEPENDENCIES)


def test_direct_runtime_versions_are_exactly_pinned_to_reviewed_versions() -> None:
    pyproject = tomllib.loads((REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    requirements = pyproject["project"]["dependencies"]
    for name, dependency in DIRECT_RUNTIME_DEPENDENCIES.items():
        matching = [item for item in requirements if _dependency_name(item) == name]
        assert len(matching) == 1
        assert f"=={dependency.version}" in matching[0]
        assert ">=" not in matching[0]
        assert "<" not in matching[0]


def test_runtime_lock_exactly_matches_reviewed_dependency_closure() -> None:
    locked = _runtime_lock()
    expected = {name: dependency.version for name, dependency in RUNTIME_DEPENDENCIES.items()}
    assert locked == expected


def test_runtime_licence_set_includes_nonpermissive_notice_cases() -> None:
    assert RUNTIME_DEPENDENCIES["certifi"].license_id == "MPL-2.0"
    assert RUNTIME_DEPENDENCIES["psycopg"].license_id == "LGPL-3.0-only"
    assert RUNTIME_DEPENDENCIES["typing-extensions"].license_id == "PSF-2.0"


def test_compliance_reviews_are_current_in_ci() -> None:
    require_direct_dependency_reviews()
    for service_id in ("github_development", "hetzner_cloud", "huggingface_model_download"):
        require_external_service(service_id)


def test_runtime_dependency_review_expiry_fails_closed() -> None:
    require_direct_dependency_reviews(as_of=date(2026, 9, 1))
    with pytest.raises(ComplianceExpiredError):
        require_direct_dependency_reviews(as_of=date(2026, 12, 1))


def test_currently_used_external_services_are_explicitly_approved() -> None:
    expected = {"github_development", "hetzner_cloud", "huggingface_model_download"}
    approved = {
        service_id
        for service_id, contract in EXTERNAL_SERVICE_CONTRACTS.items()
        if contract.status is ComplianceStatus.APPROVED
    }
    assert approved == expected
    for service_id in expected:
        assert require_external_service(service_id, as_of=date(2026, 9, 1)).conditions


def test_approved_service_review_expiry_fails_closed() -> None:
    with pytest.raises(ComplianceExpiredError):
        require_external_service("hetzner_cloud", as_of=date(2026, 12, 1))


@pytest.mark.parametrize("service_id", ["stripe_payments", "cloudflare_optional"])
def test_conditional_future_services_cannot_be_activated(service_id: str) -> None:
    with pytest.raises(ValueError, match="activation is prohibited"):
        require_external_service(service_id, as_of=date(2026, 9, 1))


def test_unknown_external_service_fails_closed() -> None:
    with pytest.raises(ValueError, match="unknown external service"):
        require_external_service("not-registered", as_of=date(2026, 9, 1))
