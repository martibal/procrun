"""Opaque purchase capability verification for the zero-PII readiness boundary."""

from __future__ import annotations

import hashlib
import hmac
from dataclasses import dataclass


class PurchaseCapabilityError(ValueError):
    pass


@dataclass(frozen=True)
class PurchaseScope:
    tenant_key: str
    purchase_reference: str
    bando_code: str
    benchmark_snapshot_id: str
    proposed_funding_eur: int
    proposed_duration_months: int | None
    expires_unix: int


def _message(scope: PurchaseScope) -> bytes:
    duration = "" if scope.proposed_duration_months is None else str(scope.proposed_duration_months)
    return "|".join(
        (
            scope.tenant_key,
            scope.purchase_reference,
            scope.bando_code,
            scope.benchmark_snapshot_id,
            str(scope.proposed_funding_eur),
            duration,
            str(scope.expires_unix),
        )
    ).encode("utf-8")


def sign_purchase_capability(scope: PurchaseScope, secret: str) -> str:
    """Used by a trusted merchant boundary after it has confirmed payment."""
    if len(secret) < 32:
        raise PurchaseCapabilityError("purchase capability secret must be at least 32 characters")
    digest = hmac.new(secret.encode("utf-8"), _message(scope), hashlib.sha256).hexdigest()
    return f"v1.{scope.expires_unix}.{digest}"


def verify_purchase_capability(
    scope: PurchaseScope,
    token: str,
    secret: str,
    *,
    now_unix: int,
) -> None:
    if len(secret) < 32:
        raise PurchaseCapabilityError("purchase capability secret is not configured safely")
    parts = token.split(".")
    if len(parts) != 3 or parts[0] != "v1" or not parts[1].isdigit():
        raise PurchaseCapabilityError("invalid purchase capability format")
    token_expiry = int(parts[1])
    if token_expiry != scope.expires_unix:
        raise PurchaseCapabilityError("purchase capability scope mismatch")
    if scope.expires_unix < now_unix:
        raise PurchaseCapabilityError("purchase capability expired")
    expected = sign_purchase_capability(scope, secret).split(".", 2)[2]
    if not hmac.compare_digest(expected, parts[2]):
        raise PurchaseCapabilityError("invalid purchase capability signature")
