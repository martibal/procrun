import pytest

from procrun.readiness_purchase import (
    PurchaseCapabilityError,
    PurchaseScope,
    sign_purchase_capability,
    verify_purchase_capability,
)


def _scope() -> PurchaseScope:
    return PurchaseScope(
        tenant_key="org_0123456789abcdef0123456789abcdef",
        purchase_reference="pay_opaque_123",
        bando_code="BANDO-X",
        benchmark_snapshot_id="snapshot-1",
        proposed_funding_eur=250_000,
        proposed_duration_months=12,
        expires_unix=2_000_000_000,
    )


def test_purchase_capability_is_bound_to_exact_analysis_scope() -> None:
    secret = "s" * 32
    scope = _scope()
    token = sign_purchase_capability(scope, secret)
    verify_purchase_capability(scope, token, secret, now_unix=1_900_000_000)

    changed = PurchaseScope(**{**scope.__dict__, "proposed_funding_eur": 260_000})
    with pytest.raises(PurchaseCapabilityError, match="signature"):
        verify_purchase_capability(changed, token, secret, now_unix=1_900_000_000)


def test_expired_purchase_capability_fails_closed() -> None:
    secret = "s" * 32
    scope = _scope()
    token = sign_purchase_capability(scope, secret)
    with pytest.raises(PurchaseCapabilityError, match="expired"):
        verify_purchase_capability(scope, token, secret, now_unix=2_000_000_001)
