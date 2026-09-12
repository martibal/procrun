"""Database-backed application service for the future ProcRun visual interface."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from psycopg import Connection

from procrun.readiness_benchmark import compute_historical_dimensioning
from procrun.readiness_dossier import CANONICALIZATION_VERSION, DossierBlockedError
from procrun.readiness_matrix import AdvisorConfirmation, build_readiness_matrix
from procrun.readiness_persistence import (
    insert_dossier,
    load_benchmark_observations,
    load_benchmark_snapshot_metadata,
    load_latest_invalidation_at,
    load_latest_source_package,
)
from procrun.readiness_service import PreviewRequest, PreviewResponse, create_paid_dossier, preview
from procrun.readiness_source import SourcePackageState, package_manifest, package_sha256


class ReadinessNotFoundError(LookupError):
    pass


def preview_by_bando(
    conn: Connection[Any],
    *,
    bando_code: str,
    benchmark_snapshot_id: str,
    as_of: datetime,
) -> PreviewResponse:
    package = load_latest_source_package(conn, bando_code)
    if package is None:
        raise ReadinessNotFoundError(f"no source package for bando {bando_code}")
    observations = load_benchmark_observations(
        conn,
        snapshot_id=benchmark_snapshot_id,
        cohort_id=package.benchmark_cohort_id,
    )
    return preview(
        PreviewRequest(
            source_package=package,
            invalidated_at=load_latest_invalidation_at(conn, package.source_package_id),
            observations=observations,
            as_of=as_of,
        )
    )


def unlock_paid_analysis(
    conn: Connection[Any],
    *,
    bando_code: str,
    benchmark_snapshot_id: str,
    proposed_funding_eur: int,
    proposed_duration_months: int | None,
    as_of: datetime,
) -> dict[str, object]:
    """Return the purchased analysis before advisor confirmations freeze the dossier."""
    package = load_latest_source_package(conn, bando_code)
    if package is None:
        raise ReadinessNotFoundError(f"no source package for bando {bando_code}")
    invalidated_at = load_latest_invalidation_at(conn, package.source_package_id)
    state = package.state_at(as_of, invalidated_at=invalidated_at)
    if state is not SourcePackageState.FRESH:
        raise DossierBlockedError(f"paid analysis unavailable: source package state is {state.value}")
    snapshot = load_benchmark_snapshot_metadata(conn, benchmark_snapshot_id)
    if snapshot is None:
        raise ReadinessNotFoundError(f"unknown benchmark snapshot {benchmark_snapshot_id}")
    data_through, snapshot_sha256 = snapshot
    observations = load_benchmark_observations(
        conn,
        snapshot_id=benchmark_snapshot_id,
        cohort_id=package.benchmark_cohort_id,
    )
    project_inputs = {
        "proposed_funding_eur": proposed_funding_eur,
        "proposed_duration_months": proposed_duration_months,
    }
    return {
        "source_package": {
            "source_package_id": package.source_package_id,
            "bando_code": package.bando_code,
            "benchmark_cohort_id": package.benchmark_cohort_id,
            "verified_at": package.verified_at.isoformat(),
            "refresh_due_at": package.refresh_due_at.isoformat(),
            "package_sha256": package_sha256(package),
            "manifest": package_manifest(package),
        },
        "published_requirements_matrix": build_readiness_matrix(
            package,
            project_inputs=project_inputs,
            confirmations=(),
        ),
        "historical_dimensioning": {
            "snapshot_id": benchmark_snapshot_id,
            "data_through": data_through,
            "snapshot_sha256": snapshot_sha256,
            "analysis": compute_historical_dimensioning(
                observations,
                proposed_funding_eur=proposed_funding_eur,
                proposed_duration_months=proposed_duration_months,
            ),
        },
    }


def create_and_persist_dossier(
    conn: Connection[Any],
    *,
    dossier_id: str,
    tenant_key: str,
    purchase_reference: str,
    bando_code: str,
    benchmark_snapshot_id: str,
    proposed_funding_eur: int,
    proposed_duration_months: int | None,
    confirmations: tuple[AdvisorConfirmation, ...],
    created_at: datetime,
) -> tuple[dict[str, object], str]:
    package = load_latest_source_package(conn, bando_code)
    if package is None:
        raise ReadinessNotFoundError(f"no source package for bando {bando_code}")
    snapshot = load_benchmark_snapshot_metadata(conn, benchmark_snapshot_id)
    if snapshot is None:
        raise ReadinessNotFoundError(f"unknown benchmark snapshot {benchmark_snapshot_id}")
    data_through, snapshot_sha256 = snapshot
    observations = load_benchmark_observations(
        conn,
        snapshot_id=benchmark_snapshot_id,
        cohort_id=package.benchmark_cohort_id,
    )
    payload, canonical, digest = create_paid_dossier(
        dossier_id=dossier_id,
        tenant_key=tenant_key,
        purchase_reference=purchase_reference,
        source_package=package,
        invalidated_at=load_latest_invalidation_at(conn, package.source_package_id),
        benchmark_snapshot_id=benchmark_snapshot_id,
        benchmark_data_through=data_through,
        benchmark_snapshot_sha256=snapshot_sha256,
        observations=observations,
        proposed_funding_eur=proposed_funding_eur,
        proposed_duration_months=proposed_duration_months,
        confirmations=confirmations,
        created_at=created_at,
    )
    insert_dossier(
        conn,
        dossier_id=dossier_id,
        tenant_key=tenant_key,
        purchase_reference=purchase_reference,
        source_package_id=package.source_package_id,
        benchmark_snapshot_id=benchmark_snapshot_id,
        created_at=created_at,
        canonicalization_version=CANONICALIZATION_VERSION,
        canonical_sha256=digest,
        canonical_jcs_bytes=canonical,
        canonical_payload=payload,
    )
    return payload, digest
