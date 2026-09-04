import os
from datetime import datetime, timezone

import psycopg
import pytest

from procrun.control_plane import (
    BillingEntitlement,
    apply_control_plane_migrations,
    get_billing_entitlement,
    get_supplier_profile,
    list_saved_opportunities,
    save_opportunity,
    set_billing_entitlement,
    unsave_opportunity,
    upsert_supplier_profile,
)
from procrun.customer_delivery import EntitlementStatus, SupplierProfile

DATABASE_URL = os.environ.get("PROCRUN_TEST_DATABASE_URL")
pytestmark = pytest.mark.skipif(DATABASE_URL is None, reason="PostgreSQL integration DB not configured")


def connect() -> psycopg.Connection[tuple[object, ...]]:
    assert DATABASE_URL is not None
    return psycopg.connect(DATABASE_URL, autocommit=True)


def reset() -> None:
    with connect() as conn:
        conn.execute("DROP SCHEMA IF EXISTS procrun_control CASCADE")
        apply_control_plane_migrations(conn)


def test_control_plane_schema_contains_no_person_identity_columns() -> None:
    reset()
    with connect() as conn:
        rows = conn.execute(
            """
            SELECT column_name FROM information_schema.columns
            WHERE table_schema = 'procrun_control'
            """
        ).fetchall()
    columns = {str(row[0]).lower() for row in rows}
    forbidden = {"email", "name", "phone", "address", "contact_name", "full_name"}
    assert not forbidden & columns


def test_supplier_profile_saved_and_entitlement_roundtrip() -> None:
    reset()
    now = datetime(2026, 9, 4, 12, tzinfo=timezone.utc)
    profile = SupplierProfile(
        account_subject="acct_opaque_1",
        organization_name="Infrastructure Supplier S.p.A.",
        country_code="ita",
        component_categories=("water_wastewater:pumps",),
        cpv_prefixes=("42122",),
    )
    entitlement = BillingEntitlement(
        account_subject="acct_opaque_1",
        status=EntitlementStatus.ACTIVE,
        plan_code="procrun-launch",
        external_customer_ref="cus_opaque",
        external_subscription_ref="sub_opaque",
        updated_at=now,
    )
    with connect() as conn:
        upsert_supplier_profile(conn, profile, updated_at=now)
        save_opportunity(conn, profile.account_subject, "OP-1", saved_at=now)
        save_opportunity(conn, profile.account_subject, "OP-1", saved_at=now)
        set_billing_entitlement(conn, entitlement)

        loaded = get_supplier_profile(conn, profile.account_subject)
        assert loaded == profile.model_copy(update={"country_code": "ITA"})
        assert list_saved_opportunities(conn, profile.account_subject) == ("OP-1",)
        assert get_billing_entitlement(conn, profile.account_subject) == entitlement

        unsave_opportunity(conn, profile.account_subject, "OP-1")
        assert list_saved_opportunities(conn, profile.account_subject) == ()
