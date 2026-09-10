"""Authoritative A21a development-lineage state after the 2026-09-10 reproducibility incident."""

from __future__ import annotations

from typing import Final

INVALIDATED_V1_SAMPLE_SHA256: Final = (
    "f214a0ee54bec0de8ef67d29707e18562fee582db57c60448b7014841e8e0b37"
)
INVALIDATED_V1_WEAK_SAMPLE_SHA256: Final = (
    "d014391f1e6f0f4e10bc0041352a4ea15fb12e4fe03cc974d31709a2c0dee02b"
)
CLEAN_V2_SOURCE_POOL_SHA256: Final = (
    "b34974616732dd7a1b95f0f8f577ce9f5b939f5448fc02610d02a5bf43955424"
)
CLEAN_V2_SAMPLE_SHA256: Final = (
    "3a53c93484a2c2eac6ec2fa2942b803ac72f0112ea0c4b52fffde0dd0a67fbd9"
)
CLEAN_V2_CASE_COUNT: Final = 60
CLEAN_V2_REVIEW_COMPLETE: Final = False
A21A_PREREGISTRATION_ACTIVE: Final = False

INVALIDATED_DEVELOPMENT_HASHES: Final = frozenset(
    {INVALIDATED_V1_SAMPLE_SHA256, INVALIDATED_V1_WEAK_SAMPLE_SHA256}
)


def require_clean_development_hash(value: str) -> None:
    """Reject the known invalidated development lineage and any unknown baseline."""

    if value in INVALIDATED_DEVELOPMENT_HASHES:
        raise ValueError("A21a development hash belongs to invalidated download-then-filter lineage")
    if value != CLEAN_V2_SAMPLE_SHA256:
        raise ValueError("A21a development hash is not the frozen clean-v2 baseline")


def preregistration_ready() -> bool:
    """Only a fresh independent clean-v2 review may unlock threshold preregistration."""

    return CLEAN_V2_REVIEW_COMPLETE and A21A_PREREGISTRATION_ACTIVE
