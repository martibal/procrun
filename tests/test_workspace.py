from __future__ import annotations

import os
from datetime import date

import psycopg
import pytest

from procrun.domain import ProjectState
from procrun.read_model import ProjectSourceEvidence, RunwayProject, SourceEvidenceType
from procrun.workspace import (
    Relevance,
    SupplierProfile,
    WorkspaceInvariantError,
    apply_workspace_migrations,
    delete_workspace,
    get_supplier_profile,
    market_summary,
    put_supplier_profile,
    rank_project,
    require_tenant_key,
    save_opportunity,
    saved_opportunities,
    unsave_opportunity,
)

DATABASE_URL = os.environ.get("PROCRUN_TEST_DATABASE_URL")
TENANT_A = "org_aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
TENANT_B = "org_bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"


def _project(*, value: int | None = 5_000_000) -> RunwayProject:
    source = ProjectSourceEvidence(
        source_type=SourceEvidenceType.PROJECT_TITLE,
        source_field="project_scope_text",
        text="Riqualificazione edificio pubblico",
        start=0,
        end=34,
        source_url="https://example.invalid/source",
    )
    return RunwayProject(
        operation_code="OP-1",
        project_title="Riqualificazione edificio pubblico",
        project_start=None,
        project_end=None,
        approved_funding_eur=value,
        programme="PR FESR Lombardia 2021-2027",
        region="Lombardia",
        nuts_code="ITC4",
        source_url="https://example.invalid/source",
        source_evidence=source,
        state=ProjectState.UNRESOLVED,
        cutoff_date=date(2026, 9, 10),
        components=(),
        unresolved_source_evidence=(),
        orchestration_version="runway-v1",
        component_rule_version="component-taxonomy-v2",
        match_rule_version="phase-b-conservative-v2-exact-evidence",
        project_classifier_version="project-state-v1",
        content_hash="a" * 64,
    )


def test_tenant_key_rejects_identity_shaped_values() -> None:
    assert require_tenant_key(TENANT_A) == TENANT_A
    for value in ("martin@example.com", "user_123", "Martin Balstad", "org_nothex"):
        with pytest.raises(WorkspaceInvariantError):
            require_tenant_key(value)


def test_supplier_profile_is_non_personal_and_fail_closed() -> None:
    profile = SupplierProfile(
        domains=("energy_efficiency",),
        cpv_prefixes=("45331",),
        nuts_prefixes=("ITC4",),
        min_project_value_eur=1_000_000,
    )
    assert profile.nuts_prefixes == ("ITC4",)
    with pytest.raises(ValueError):
        SupplierProfile(domains=("person_name",))


@pytest.mark.skipif(DATABASE_URL is None, reason="PostgreSQL test URL not configured")
def test_workspace_persistence_is_tenant_isolated_and_deletable() -> None:
    assert DATABASE_URL is not None
    with psycopg.connect(DATABASE_URL) as conn:
        apply_workspace_migrations(conn)
        delete_workspace(conn, TENANT_A)
        delete_workspace(conn, TENANT_B)
        profile = SupplierProfile(
            domains=("energy_efficiency",), nuts_prefixes=("ITC4",), min_project_value_eur=1
        )
        put_supplier_profile(conn, TENANT_A, profile)
        save_opportunity(conn, TENANT_A, "OP-1:cmp-1")
        save_opportunity(conn, TENANT_B, "OP-2:cmp-2")
        conn.commit()

        assert get_supplier_profile(conn, TENANT_A) == profile
        assert get_supplier_profile(conn, TENANT_B) is None
        assert saved_opportunities(conn, TENANT_A) == ("OP-1:cmp-1",)
        assert saved_opportunities(conn, TENANT_B) == ("OP-2:cmp-2",)

        unsave_opportunity(conn, TENANT_A, "OP-1:cmp-1")
        delete_workspace(conn, TENANT_B)
        conn.commit()
        assert saved_opportunities(conn, TENANT_A) == ()
        assert saved_opportunities(conn, TENANT_B) == ()


def test_relevance_never_changes_project_classification() -> None:
    project = _project()
    ranked = rank_project(
        project,
        SupplierProfile(nuts_prefixes=("ITC4",), min_project_value_eur=1_000_000),
    )
    assert ranked.relevance in {Relevance.MEDIUM, Relevance.HIGH}
    assert ranked.project.state is ProjectState.UNRESOLVED
    assert ranked.project.content_hash == project.content_hash


def test_market_summary_discloses_value_missingness() -> None:
    summary = market_summary((_project(value=5_000_000), _project(value=None)))
    assert summary["project_count"] == 2
    assert summary["known_approved_funding_eur"] == 5_000_000
    assert summary["missing_value_count"] == 1
    assert summary["value_coverage_ratio"] == 0.5
    assert summary["coverage_scope"] == "TED rule-bounded matching"
