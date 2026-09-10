"""Provider-neutral customer workspace core with a strict non-personal tenant boundary.

The intelligence plane never receives customer identity data. Workspace persistence is keyed only
by an internally generated organisation tenant key (``org_<32 hex>``). Names, email addresses,
phone numbers, user IDs and arbitrary identity strings are not accepted by this module.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import IntEnum
from typing import Final

from psycopg import Connection
from pydantic import BaseModel, ConfigDict, Field, field_validator

from procrun.domain import ProjectState
from procrun.read_model import RunwayProject

WORKSPACE_SCHEMA_VERSION: Final = "workspace-v1"
_TENANT_RE: Final = re.compile(r"^org_[0-9a-f]{32}$")
_ALLOWED_DOMAINS: Final = frozenset(
    {
        "water_wastewater",
        "rail_transport",
        "ports_coastal",
        "energy_efficiency",
        "resilience_fire",
    }
)


class WorkspaceInvariantError(ValueError):
    """Raised before customer-control-plane data can cross a frozen boundary."""


def require_tenant_key(value: str) -> str:
    """Accept only non-semantic random organisation keys, never person identifiers."""

    if _TENANT_RE.fullmatch(value) is None:
        raise WorkspaceInvariantError("tenant key must be an opaque org_<32 hex> identifier")
    return value


class SupplierProfile(BaseModel):
    """Only non-personal organisation buying-fit criteria are permitted."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    domains: tuple[str, ...] = ()
    cpv_prefixes: tuple[str, ...] = ()
    nuts_prefixes: tuple[str, ...] = ()
    min_project_value_eur: int = Field(default=0, ge=0)

    @field_validator("domains")
    @classmethod
    def validate_domains(cls, values: tuple[str, ...]) -> tuple[str, ...]:
        normalized = tuple(dict.fromkeys(value.strip() for value in values if value.strip()))
        unknown = set(normalized) - _ALLOWED_DOMAINS
        if unknown:
            raise ValueError(f"unsupported supplier domains: {sorted(unknown)}")
        return normalized

    @field_validator("cpv_prefixes")
    @classmethod
    def validate_cpv(cls, values: tuple[str, ...]) -> tuple[str, ...]:
        normalized = tuple(dict.fromkeys(value.strip() for value in values if value.strip()))
        if any(not value.isdigit() or not 2 <= len(value) <= 8 for value in normalized):
            raise ValueError("CPV prefixes must contain 2-8 digits")
        return normalized

    @field_validator("nuts_prefixes")
    @classmethod
    def validate_nuts(cls, values: tuple[str, ...]) -> tuple[str, ...]:
        normalized = tuple(
            dict.fromkeys(value.strip().upper() for value in values if value.strip())
        )
        if any(not re.fullmatch(r"[A-Z0-9]{2,5}", value) for value in normalized):
            raise ValueError("NUTS prefixes must contain 2-5 uppercase letters/digits")
        return normalized


class Relevance(IntEnum):
    NOT_RELEVANT = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3


@dataclass(frozen=True)
class RankedProject:
    project: RunwayProject
    relevance: Relevance
    reasons: tuple[str, ...]


_WORKSPACE_MIGRATION = r"""
CREATE SCHEMA IF NOT EXISTS procrun_workspace;
CREATE TABLE IF NOT EXISTS procrun_workspace.schema_migrations (
    migration_id text PRIMARY KEY,
    applied_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS procrun_workspace.supplier_profiles (
    tenant_key text PRIMARY KEY CHECK (tenant_key ~ '^org_[0-9a-f]{32}$'),
    domains text[] NOT NULL DEFAULT '{}',
    cpv_prefixes text[] NOT NULL DEFAULT '{}',
    nuts_prefixes text[] NOT NULL DEFAULT '{}',
    min_project_value_eur bigint NOT NULL DEFAULT 0 CHECK (min_project_value_eur >= 0),
    updated_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS procrun_workspace.saved_opportunities (
    tenant_key text NOT NULL CHECK (tenant_key ~ '^org_[0-9a-f]{32}$'),
    opportunity_key text NOT NULL CHECK (length(opportunity_key) BETWEEN 1 AND 512),
    saved_at timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (tenant_key, opportunity_key)
);
REVOKE ALL ON SCHEMA procrun FROM PUBLIC;
"""


def apply_workspace_migrations(conn: Connection[object]) -> None:
    with conn.transaction():
        conn.execute(_WORKSPACE_MIGRATION)
        conn.execute(
            """
            INSERT INTO procrun_workspace.schema_migrations (migration_id)
            VALUES (%s) ON CONFLICT DO NOTHING
            """,
            ("001_workspace_non_personal",),
        )


def put_supplier_profile(
    conn: Connection[object], tenant_key: str, profile: SupplierProfile
) -> None:
    tenant = require_tenant_key(tenant_key)
    conn.execute(
        """
        INSERT INTO procrun_workspace.supplier_profiles
            (tenant_key, domains, cpv_prefixes, nuts_prefixes, min_project_value_eur)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (tenant_key) DO UPDATE SET
            domains = EXCLUDED.domains,
            cpv_prefixes = EXCLUDED.cpv_prefixes,
            nuts_prefixes = EXCLUDED.nuts_prefixes,
            min_project_value_eur = EXCLUDED.min_project_value_eur,
            updated_at = now()
        """,
        (
            tenant,
            list(profile.domains),
            list(profile.cpv_prefixes),
            list(profile.nuts_prefixes),
            profile.min_project_value_eur,
        ),
    )


def get_supplier_profile(
    conn: Connection[object], tenant_key: str
) -> SupplierProfile | None:
    tenant = require_tenant_key(tenant_key)
    row = conn.execute(
        """
        SELECT domains, cpv_prefixes, nuts_prefixes, min_project_value_eur
        FROM procrun_workspace.supplier_profiles WHERE tenant_key = %s
        """,
        (tenant,),
    ).fetchone()
    if row is None:
        return None
    return SupplierProfile(
        domains=tuple(row[0]),
        cpv_prefixes=tuple(row[1]),
        nuts_prefixes=tuple(row[2]),
        min_project_value_eur=int(row[3]),
    )


def save_opportunity(
    conn: Connection[object], tenant_key: str, opportunity_key: str
) -> None:
    tenant = require_tenant_key(tenant_key)
    key = opportunity_key.strip()
    if not key or len(key) > 512:
        raise WorkspaceInvariantError("invalid opportunity key")
    conn.execute(
        """
        INSERT INTO procrun_workspace.saved_opportunities (tenant_key, opportunity_key)
        VALUES (%s, %s) ON CONFLICT DO NOTHING
        """,
        (tenant, key),
    )


def unsave_opportunity(
    conn: Connection[object], tenant_key: str, opportunity_key: str
) -> None:
    tenant = require_tenant_key(tenant_key)
    conn.execute(
        """
        DELETE FROM procrun_workspace.saved_opportunities
        WHERE tenant_key = %s AND opportunity_key = %s
        """,
        (tenant, opportunity_key),
    )


def saved_opportunities(
    conn: Connection[object], tenant_key: str
) -> tuple[str, ...]:
    tenant = require_tenant_key(tenant_key)
    rows = conn.execute(
        """
        SELECT opportunity_key FROM procrun_workspace.saved_opportunities
        WHERE tenant_key = %s ORDER BY opportunity_key
        """,
        (tenant,),
    ).fetchall()
    return tuple(str(row[0]) for row in rows)


def delete_workspace(conn: Connection[object], tenant_key: str) -> None:
    """Delete the non-intelligence workspace without touching the append-only evidence ledger."""

    tenant = require_tenant_key(tenant_key)
    with conn.transaction():
        conn.execute(
            """
            DELETE FROM procrun_workspace.saved_opportunities
            WHERE tenant_key = %s
            """,
            (tenant,),
        )
        conn.execute(
            "DELETE FROM procrun_workspace.supplier_profiles WHERE tenant_key = %s",
            (tenant,),
        )


def rank_project(project: RunwayProject, profile: SupplierProfile | None) -> RankedProject:
    """Compute deterministic fit without changing evidence or classification state."""

    if profile is None:
        return RankedProject(
            project=project,
            relevance=Relevance.LOW,
            reasons=("profile_not_set",),
        )

    domains = {component.category.split(":", 1)[0] for component in project.components}
    domain_match = not profile.domains or bool(domains.intersection(profile.domains))
    geography_match = not profile.nuts_prefixes or bool(
        project.nuts_code
        and any(
            project.nuts_code.upper().startswith(prefix)
            for prefix in profile.nuts_prefixes
        )
    )
    if profile.min_project_value_eur:
        value_match = (
            project.approved_funding_eur is not None
            and project.approved_funding_eur >= profile.min_project_value_eur
        )
    else:
        value_match = True
    cpv_match = not profile.cpv_prefixes or any(
        any(
            code.replace("-", "").startswith(prefix)
            for match in component.procurement_matches
            for code in match.cpv_codes
        )
        for component in project.components
        for prefix in profile.cpv_prefixes
    )

    checks = (domain_match, geography_match, value_match, cpv_match)
    score = sum(checks)
    if score == 4:
        relevance = Relevance.HIGH
    elif score == 3:
        relevance = Relevance.MEDIUM
    elif score == 2:
        relevance = Relevance.LOW
    else:
        relevance = Relevance.NOT_RELEVANT
    reasons = tuple(
        name
        for name, matched in zip(
            ("domain", "geography", "project_value", "cpv"), checks, strict=True
        )
        if matched
    )
    return RankedProject(project=project, relevance=relevance, reasons=reasons)


def market_summary(projects: tuple[RunwayProject, ...]) -> dict[str, object]:
    """Aggregate only customer-safe read-model fields with explicit missingness."""

    state_counts = {state.value: 0 for state in ProjectState}
    known_value_eur = 0
    missing_value_count = 0
    for project in projects:
        state_counts[project.state.value] += 1
        if project.approved_funding_eur is None:
            missing_value_count += 1
        else:
            known_value_eur += project.approved_funding_eur
    return {
        "project_count": len(projects),
        "state_counts": state_counts,
        "known_approved_funding_eur": known_value_eur,
        "missing_value_count": missing_value_count,
        "value_coverage_ratio": (
            0.0 if not projects else (len(projects) - missing_value_count) / len(projects)
        ),
        "coverage_scope": "TED rule-bounded matching",
    }
