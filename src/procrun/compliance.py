"""Executable licence/provider compliance metadata.

The registry makes external software/service assumptions visible to code review and CI.
It is not a substitute for upstream terms. Reviews deliberately expire so a one-time
terms check cannot become permanent by accident.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from enum import StrEnum


class ComplianceStatus(StrEnum):
    APPROVED = "APPROVED"
    CONDITIONAL = "CONDITIONAL"
    BLOCKED = "BLOCKED"


class ComplianceExpiredError(ValueError):
    """Raised when an approved compliance review is stale."""


_REVIEWED_ON = date(2026, 9, 1)
_REVIEW_DUE_ON = date(2026, 11, 30)


@dataclass(frozen=True)
class DependencyLicense:
    package: str
    version: str
    license_id: str
    license_url: str
    usage: str
    direct: bool
    reviewed_on: date
    review_due_on: date
    distribution_note: str


RUNTIME_DEPENDENCIES = {
    "annotated-types": DependencyLicense(
        "annotated-types",
        "0.8.0",
        "MIT",
        "https://github.com/annotated-types/annotated-types/blob/main/LICENSE",
        "Pydantic runtime dependency.",
        False,
        _REVIEWED_ON,
        _REVIEW_DUE_ON,
        "Preserve applicable MIT notice if software is distributed.",
    ),
    "anyio": DependencyLicense(
        "anyio",
        "4.14.2",
        "MIT",
        "https://github.com/agronholm/anyio/blob/master/LICENSE",
        "HTTPX concurrency/runtime dependency.",
        False,
        _REVIEWED_ON,
        _REVIEW_DUE_ON,
        "Preserve applicable MIT notice if software is distributed.",
    ),
    "certifi": DependencyLicense(
        "certifi",
        "2026.7.22",
        "MPL-2.0",
        "https://github.com/certifi/python-certifi/blob/master/LICENSE",
        "CA certificate bundle used by HTTPX.",
        False,
        _REVIEWED_ON,
        _REVIEW_DUE_ON,
        "Re-review MPL file-level obligations before software/container distribution.",
    ),
    "h11": DependencyLicense(
        "h11",
        "0.16.0",
        "MIT",
        "https://github.com/python-hyper/h11/blob/master/LICENSE.txt",
        "HTTP/1.1 protocol dependency of httpcore.",
        False,
        _REVIEWED_ON,
        _REVIEW_DUE_ON,
        "Preserve applicable MIT notice if software is distributed.",
    ),
    "httpcore": DependencyLicense(
        "httpcore",
        "1.0.9",
        "BSD-3-Clause",
        "https://github.com/encode/httpcore/blob/master/LICENSE.md",
        "HTTP transport dependency of HTTPX.",
        False,
        _REVIEWED_ON,
        _REVIEW_DUE_ON,
        "Preserve BSD notice/conditions if software is distributed.",
    ),
    "httpx": DependencyLicense(
        "httpx",
        "0.28.1",
        "BSD-3-Clause",
        "https://github.com/encode/httpx/blob/master/LICENSE.md",
        "Bounded HTTP client for approved public-source retrieval.",
        True,
        _REVIEWED_ON,
        _REVIEW_DUE_ON,
        "Preserve BSD notice/conditions if software is distributed.",
    ),
    "idna": DependencyLicense(
        "idna",
        "3.19",
        "BSD-3-Clause",
        "https://github.com/kjd/idna/blob/master/LICENSE.md",
        "Internationalized domain handling used by HTTPX.",
        False,
        _REVIEWED_ON,
        _REVIEW_DUE_ON,
        "Preserve BSD notice/conditions if software is distributed.",
    ),
    "psycopg": DependencyLicense(
        "psycopg",
        "3.3.5",
        "LGPL-3.0-only",
        "https://www.psycopg.org/psycopg3/docs/basic/install.html",
        "PostgreSQL client.",
        True,
        _REVIEWED_ON,
        _REVIEW_DUE_ON,
        (
            "Current mode is server-side SaaS; re-review LGPL obligations before "
            "on-prem/binary distribution or modifying Psycopg."
        ),
    ),
    "psycopg-binary": DependencyLicense(
        "psycopg-binary",
        "3.3.5",
        "LGPL-3.0-only",
        "https://www.psycopg.org/psycopg3/docs/basic/install.html",
        "Binary implementation installed by psycopg[binary].",
        False,
        _REVIEWED_ON,
        _REVIEW_DUE_ON,
        (
            "Current mode is server-side SaaS; re-review LGPL obligations before "
            "on-prem/binary distribution."
        ),
    ),
    "pydantic": DependencyLicense(
        "pydantic",
        "2.13.5",
        "MIT",
        "https://github.com/pydantic/pydantic/blob/main/LICENSE",
        "Strict validation of domain/source/model contracts.",
        True,
        _REVIEWED_ON,
        _REVIEW_DUE_ON,
        "Preserve applicable MIT notice if software is distributed.",
    ),
    "pydantic-core": DependencyLicense(
        "pydantic-core",
        "2.46.5",
        "MIT",
        "https://github.com/pydantic/pydantic-core/blob/main/LICENSE",
        "Pydantic validation runtime.",
        False,
        _REVIEWED_ON,
        _REVIEW_DUE_ON,
        "Preserve applicable MIT notice if software is distributed.",
    ),
    "typing-extensions": DependencyLicense(
        "typing-extensions",
        "4.16.0",
        "PSF-2.0",
        "https://github.com/python/typing_extensions/blob/main/LICENSE",
        "Typing compatibility runtime dependency.",
        False,
        _REVIEWED_ON,
        _REVIEW_DUE_ON,
        "Preserve applicable PSF licence notice if software is distributed.",
    ),
    "typing-inspection": DependencyLicense(
        "typing-inspection",
        "0.4.4",
        "MIT",
        "https://github.com/pydantic/typing-inspection/blob/main/LICENSE",
        "Pydantic typing inspection runtime dependency.",
        False,
        _REVIEWED_ON,
        _REVIEW_DUE_ON,
        "Preserve applicable MIT notice if software is distributed.",
    ),
}

DIRECT_RUNTIME_DEPENDENCIES = {
    name: dependency for name, dependency in RUNTIME_DEPENDENCIES.items() if dependency.direct
}


@dataclass(frozen=True)
class ExternalServiceContract:
    service_id: str
    status: ComplianceStatus
    purpose: str
    terms_url: str
    reviewed_on: date
    review_due_on: date
    conditions: tuple[str, ...]


EXTERNAL_SERVICE_CONTRACTS = {
    "github_development": ExternalServiceContract(
        "github_development",
        ComplianceStatus.APPROVED,
        "Private source repository and CI; not a production intelligence data store.",
        "https://docs.github.com/en/site-policy/github-terms/github-terms-of-service",
        _REVIEWED_ON,
        _REVIEW_DUE_ON,
        (
            "Keep the core repository private unless an explicit licensing decision is made.",
            "Do not store production source payloads, model weights, secrets or customer data.",
            "Respect GitHub API/rate/acceptable-use limits.",
        ),
    ),
    "hetzner_cloud": ExternalServiceContract(
        "hetzner_cloud",
        ComplianceStatus.APPROVED,
        "EU VPS hosting and ephemeral benchmark hosts.",
        "https://www.hetzner.com/legal/terms-and-conditions/",
        _REVIEWED_ON,
        _REVIEW_DUE_ON,
        (
            "Normal commercial hosting only.",
            (
                "Do not introduce prohibited activities such as cryptomining or abusive "
                "network scanning."
            ),
            "Keep independent backups because provider availability is not a backup strategy.",
        ),
    ),
    "huggingface_model_download": ExternalServiceContract(
        "huggingface_model_download",
        ComplianceStatus.APPROVED,
        "Download the exact public Qwen GGUF artifact; no hosted inference.",
        "https://huggingface.co/terms-of-service",
        _REVIEWED_ON,
        _REVIEW_DUE_ON,
        (
            "Use only the pinned public repository/revision and respect the model licence.",
            "Do not send project/customer data to Hugging Face inference services.",
            "Verify exact artifact size and SHA-256 before inference.",
        ),
    ),
    "stripe_payments": ExternalServiceContract(
        "stripe_payments",
        ComplianceStatus.CONDITIONAL,
        "Planned customer subscription/payment processing; not active in the core.",
        "https://stripe.com/legal/ssa/no",
        _REVIEWED_ON,
        _REVIEW_DUE_ON,
        (
            "Activate only after Stripe accepts the actual business/account.",
            "Recheck prohibited/restricted-business rules at activation.",
            "Keep payment/customer identity outside the intelligence ledger/model pipeline.",
            "Complete account-specific privacy, VAT and payment-flow review before launch.",
        ),
    ),
    "cloudflare_optional": ExternalServiceContract(
        "cloudflare_optional",
        ComplianceStatus.CONDITIONAL,
        "Optional DNS/CDN/DDoS layer; not required by the current architecture.",
        "https://www.cloudflare.com/terms/",
        _REVIEWED_ON,
        _REVIEW_DUE_ON,
        (
            "Do not add by default; direct hosting keeps the third-party surface smaller.",
            "Re-review exact plan/features and privacy/logging effects before activation.",
        ),
    ),
}


def _validate_registry() -> None:
    for dependency in RUNTIME_DEPENDENCIES.values():
        if dependency.reviewed_on > dependency.review_due_on:
            raise ValueError(f"invalid dependency review dates: {dependency.package}")
        if not dependency.license_id or not dependency.license_url:
            raise ValueError(f"incomplete dependency licence metadata: {dependency.package}")

    for contract in EXTERNAL_SERVICE_CONTRACTS.values():
        if contract.reviewed_on > contract.review_due_on:
            raise ValueError(f"invalid external-service review dates: {contract.service_id}")
        if not contract.terms_url or not contract.conditions:
            raise ValueError(f"incomplete external-service contract: {contract.service_id}")


_validate_registry()


def require_runtime_dependency_reviews(*, as_of: date | None = None) -> None:
    """Fail closed when any frozen production-runtime licence review is stale."""

    effective_date = as_of or date.today()
    expired = [
        dependency.package
        for dependency in RUNTIME_DEPENDENCIES.values()
        if effective_date > dependency.review_due_on
    ]
    if expired:
        raise ComplianceExpiredError(
            "runtime dependency licence review expired: " + ", ".join(sorted(expired))
        )


def require_direct_dependency_reviews(*, as_of: date | None = None) -> None:
    """Compatibility entry point; all runtime dependencies are checked."""

    require_runtime_dependency_reviews(as_of=as_of)


def require_external_service(
    service_id: str,
    *,
    as_of: date | None = None,
) -> ExternalServiceContract:
    """Fail closed if code relies on an unapproved or stale external service."""

    try:
        contract = EXTERNAL_SERVICE_CONTRACTS[service_id]
    except KeyError as exc:
        raise ValueError(f"unknown external service contract: {service_id}") from exc
    if contract.status is not ComplianceStatus.APPROVED:
        raise ValueError(
            f"external service {service_id} is {contract.status}; activation is prohibited"
        )

    effective_date = as_of or date.today()
    if effective_date > contract.review_due_on:
        raise ComplianceExpiredError(
            f"external service {service_id} review expired on {contract.review_due_on.isoformat()}"
        )
    return contract
