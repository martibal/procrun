"""Fail-closed field validation for zero-PII source adapters.

Adapters must project source responses server-side whenever the source supports field
projection. This module is a second boundary: only exact, pre-approved keys may enter
normalization. Unknown fields are rejected rather than silently dropped.
"""

from collections.abc import Mapping, Set
from typing import Any


class UnexpectedFieldError(ValueError):
    """Raised when a source record contains a field outside its frozen allowlist."""


def require_exact_allowlist(record: Mapping[str, Any], allowed_fields: Set[str]) -> None:
    """Reject a record if any returned key is outside the source-specific allowlist."""

    unexpected = set(record) - set(allowed_fields)
    if unexpected:
        names = ", ".join(sorted(unexpected))
        raise UnexpectedFieldError(f"source returned non-allowlisted fields: {names}")


def project_allowlisted(record: Mapping[str, Any], allowed_fields: Set[str]) -> dict[str, Any]:
    """Return only allowed fields after first proving there are no unexpected fields.

    The validation-before-projection order is intentional. Silently discarding an unexpected
    field would hide a source-contract change and could allow prohibited data into process memory.
    """

    require_exact_allowlist(record, allowed_fields)
    return {key: record[key] for key in allowed_fields if key in record}
