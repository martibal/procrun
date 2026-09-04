"""Opaque-account control plane kept separate from ProcRun's intelligence ledger.

The intelligence plane must never contain natural-person data. This module therefore stores only an
opaque account subject plus organisation/supplier configuration and opaque billing references. Email,
name, phone and address are deliberately absent from the schema and API.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from psycopg import Connection

from procrun.customer_delivery import EntitlementStatus, SupplierProfile

CONTROL_SCHEMA_VERSION = "control-plane-v1"

_MIGRATION_001 = r"""
CREATE SCHEMA IF NOT EXISTS procrun_control;

CREATE TABLE procrun_control.supplier_profiles (
    account_subject text PRIMARY KEY,
    organization_name text NOT NULL,
    country_code char(3) NOT NULL CHECK (country_code ~ '^[A-Z]{3}$'),
    component_categories text[] NOT NULL DEFAULT '{}',
    cpv_prefixes text[] NOT NULL DEFAULT '{}',
    updated_at timestamptz NOT NULL
);

CREATE TABLE procrun_control.saved_opportunities (
    account_subject text NOT NULL,
    operation_code text NOT NULL,
    saved_at timestamptz NOT NULL,
    PRIMARY KEY (account_subject, operation_code)
);
CREATE INDEX saved_opportunities_account_idx
    ON procrun_control.saved_opportunities (account_subject, saved_at DESC);

CREATE TABLE procrun_control.billing_entitlements (
    account_subject text PRIMARY KEY,
    entitlement_status text NOT NULL CHECK (entitlement_status IN ('ACTIVE', 'INACTIVE')),
    plan_code text NOT NULL,
    external_customer_ref text,
    external_subscription_ref text,
    updated_at timestamptz NOT NULL
);
"""


class ControlPlaneInvariantError(ValueError):
    """Raised when an opaque-account control-plane contract is violated."""


@dataclass(frozen=True)
class BillingEntitlement:
    account_subject: str
    status: EntitlementStatus
    plan_code: str
    external_customer_ref: str | None
    external_subscription_ref: str | None
    updated_at: datetime


def _utc(value: datetime) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ControlPlaneInvariantError("control-plane timestamps must be timezone-aware")
    return value.astimezone(timezone.utc)


def apply_control_plane_migrations(conn: Connection[Any]) -> None:
    with conn.transaction():
        conn.execute("CREATE SCHEMA IF NOT EXISTS procrun_control")
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS procrun_control.schema_migrations (
                migration_id text PRIMARY KEY,
                applied_at timestamptz NOT NULL DEFAULT now()
            )
            """
        )
        exists = conn.execute(
            "SELECT 1 FROM procrun_control.schema_migrations WHERE migration_id = %s",
            ("001_control_plane",),
        ).fetchone()
        if exists is None:
            conn.execute(_MIGRATION_001)
            conn.execute(
                "INSERT INTO procrun_control.schema_migrations (migration_id) VALUES (%s)",
                ("001_control_plane",),
            )


def upsert_supplier_profile(
    conn: Connection[Any], profile: SupplierProfile, *, updated_at: datetime
) -> None:
    timestamp = _utc(updated_at)
    conn.execute(
        """
        INSERT INTO procrun_control.supplier_profiles (
            account_subject, organization_name, country_code, component_categories,
            cpv_prefixes, updated_at
        ) VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (account_subject) DO UPDATE SET
            organization_name = EXCLUDED.organization_name,
            country_code = EXCLUDED.country_code,
            component_categories = EXCLUDED.component_categories,
            cpv_prefixes = EXCLUDED.cpv_prefixes,
            updated_at = EXCLUDED.updated_at
        """,
        (
            profile.account_subject,
            profile.organization_name,
            profile.country_code,
            list(profile.component_categories),
            list(profile.cpv_prefixes),
            timestamp,
        ),
    )


def get_supplier_profile(conn: Connection[Any], account_subject: str) -> SupplierProfile | None:
    row = conn.execute(
        """
        SELECT account_subject, organization_name, country_code, component_categories, cpv_prefixes
        FROM procrun_control.supplier_profiles WHERE account_subject = %s
        """,
        (account_subject,),
    ).fetchone()
    if row is None:
        return None
    return SupplierProfile(
        account_subject=str(row[0]),
        organization_name=str(row[1]),
        country_code=str(row[2]).strip(),
        component_categories=tuple(row[3] or ()),
        cpv_prefixes=tuple(row[4] or ()),
    )


def save_opportunity(
    conn: Connection[Any], account_subject: str, operation_code: str, *, saved_at: datetime
) -> None:
    if not account_subject.strip() or not operation_code.strip():
        raise ControlPlaneInvariantError("account subject and operation code must not be blank")
    conn.execute(
        """
        INSERT INTO procrun_control.saved_opportunities (account_subject, operation_code, saved_at)
        VALUES (%s, %s, %s)
        ON CONFLICT (account_subject, operation_code) DO NOTHING
        """,
        (account_subject, operation_code, _utc(saved_at)),
    )


def unsave_opportunity(conn: Connection[Any], account_subject: str, operation_code: str) -> None:
    conn.execute(
        "DELETE FROM procrun_control.saved_opportunities WHERE account_subject = %s AND operation_code = %s",
        (account_subject, operation_code),
    )


def list_saved_opportunities(conn: Connection[Any], account_subject: str) -> tuple[str, ...]:
    rows = conn.execute(
        """
        SELECT operation_code FROM procrun_control.saved_opportunities
        WHERE account_subject = %s ORDER BY saved_at DESC, operation_code ASC
        """,
        (account_subject,),
    ).fetchall()
    return tuple(str(row[0]) for row in rows)


def set_billing_entitlement(
    conn: Connection[Any], entitlement: BillingEntitlement
) -> None:
    if not entitlement.account_subject.strip() or not entitlement.plan_code.strip():
        raise ControlPlaneInvariantError("billing account subject and plan code must not be blank")
    conn.execute(
        """
        INSERT INTO procrun_control.billing_entitlements (
            account_subject, entitlement_status, plan_code, external_customer_ref,
            external_subscription_ref, updated_at
        ) VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (account_subject) DO UPDATE SET
            entitlement_status = EXCLUDED.entitlement_status,
            plan_code = EXCLUDED.plan_code,
            external_customer_ref = EXCLUDED.external_customer_ref,
            external_subscription_ref = EXCLUDED.external_subscription_ref,
            updated_at = EXCLUDED.updated_at
        """,
        (
            entitlement.account_subject,
            entitlement.status.value,
            entitlement.plan_code,
            entitlement.external_customer_ref,
            entitlement.external_subscription_ref,
            _utc(entitlement.updated_at),
        ),
    )


def get_billing_entitlement(
    conn: Connection[Any], account_subject: str
) -> BillingEntitlement | None:
    row = conn.execute(
        """
        SELECT account_subject, entitlement_status, plan_code, external_customer_ref,
               external_subscription_ref, updated_at
        FROM procrun_control.billing_entitlements WHERE account_subject = %s
        """,
        (account_subject,),
    ).fetchone()
    if row is None:
        return None
    return BillingEntitlement(
        account_subject=str(row[0]),
        status=EntitlementStatus(str(row[1])),
        plan_code=str(row[2]),
        external_customer_ref=None if row[3] is None else str(row[3]),
        external_subscription_ref=None if row[4] is None else str(row[4]),
        updated_at=_utc(row[5]),
    )
