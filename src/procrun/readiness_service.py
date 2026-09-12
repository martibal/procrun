"""Headless service contract consumed by the future visual interface."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from procrun.readiness_benchmark import BenchmarkObservation, SampleTier, sample_tier
from procrun.readiness_dossier import DossierBuildInput, build_dossier
from procrun.readiness_matrix import AdvisorConfirmation
from procrun.readiness_source import SourcePackage, SourcePackageState


@dataclass(frozen=True)
class PreviewRequest:
    source_package: SourcePackage
    invalidated_at: datetime | None
    observations: tuple[BenchmarkObservation, ...]
    as_of: datetime


@dataclass(frozen=True)
class PreviewResponse:
    analysis_available: bool
    source_state: SourcePackageState
    historical_reference: str
    customer_message: str


def preview(request: PreviewRequest) -> PreviewResponse:
    """Return a leak-free pre-payment preview: no n, percentile, median or comparable names."""
    state = request.source_package.state_at(request.as_of, invalidated_at=request.invalidated_at)
    funding_n = sum(1 for item in request.observations if item.approved_funding_eur is not None)
    tier = sample_tier(funding_n)
    if state is not SourcePackageState.FRESH:
        return PreviewResponse(
            analysis_available=False,
            source_state=state,
            historical_reference="UNAVAILABLE",
            customer_message="Source package must be refreshed before a paid dossier can be created.",
        )
    if tier is SampleTier.REFERENCE_ONLY:
        return PreviewResponse(
            analysis_available=True,
            source_state=state,
            historical_reference="LIMITED_REFERENCE",
            customer_message=(
                "Limited historical reference is available. The paid dossier can show the observed "
                "funded projects, but not a full statistical benchmark."
            ),
        )
    return PreviewResponse(
        analysis_available=True,
        source_state=state,
        historical_reference="ANALYSIS_AVAILABLE",
        customer_message=(
            "Historical analysis is available for the selected source package. Unlock the dossier "
            "to see the reference population, project position and funded comparables."
        ),
    )


def create_paid_dossier(
    *,
    dossier_id: str,
    tenant_key: str,
    purchase_reference: str,
    source_package: SourcePackage,
    invalidated_at: datetime | None,
    benchmark_snapshot_id: str,
    benchmark_data_through: str,
    benchmark_snapshot_sha256: str,
    observations: tuple[BenchmarkObservation, ...],
    proposed_funding_eur: int,
    proposed_duration_months: int | None,
    confirmations: tuple[AdvisorConfirmation, ...],
    created_at: datetime,
) -> tuple[dict[str, object], bytes, str]:
    """Single production entrypoint for paid dossier generation."""
    return build_dossier(
        DossierBuildInput(
            dossier_id=dossier_id,
            tenant_key=tenant_key,
            purchase_reference=purchase_reference,
            source_package=source_package,
            invalidated_at=invalidated_at,
            benchmark_snapshot_id=benchmark_snapshot_id,
            benchmark_data_through=benchmark_data_through,
            benchmark_snapshot_sha256=benchmark_snapshot_sha256,
            observations=observations,
            proposed_funding_eur=proposed_funding_eur,
            proposed_duration_months=proposed_duration_months,
            confirmations=confirmations,
            created_at=created_at,
        )
    )
