"""Fail-closed validation for already-projected zero-PII source responses.

The transport layer must request only approved fields from a source whenever server-side
projection exists. This module is the second boundary: if the projected response schema drifts,
the record is rejected before normalization, persistence, logging, or model use.
"""

from collections.abc import Mapping, Set
from typing import Any


class UnexpectedFieldError(ValueError):
    """Raised when a projected source record contains a field outside its frozen allowlist."""


def require_exact_allowlist(record: Mapping[str, Any], allowed_fields: Set[str]) -> None:
    """Reject a projected record if any returned key is outside the source allowlist."""

    unexpected = set(record) - set(allowed_fields)
    if unexpected:
        names = ", ".join(sorted(unexpected))
        raise UnexpectedFieldError(f"source returned non-allowlisted fields: {names}")


def validate_projected_record(
    record: Mapping[str, Any], allowed_fields: Set[str]
) -> dict[str, Any]:
    """Validate an already-server-projected response and return its approved fields."""

    require_exact_allowlist(record, allowed_fields)
    return {key: record[key] for key in allowed_fields if key in record}
