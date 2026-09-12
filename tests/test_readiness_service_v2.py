from datetime import UTC, datetime

from procrun.readiness_benchmark import BenchmarkObservation
from procrun.readiness_service import PreviewRequest, preview
from procrun.readiness_source import SourceDocument, SourcePackage


def _package() -> SourcePackage:
    verified = datetime(2026, 9, 10, tzinfo=UTC)
    return SourcePackage(
        source_package_id="pkg",
        bando_code="BANDO-X",
        benchmark_cohort_id="SAME_BANDO:BANDO-X",
        version=1,
        verified_at=verified,
        documents=(
            SourceDocument(
                document_id="bando",
                document_type="BANDO",
                title="Bando",
                public_url="https://example.invalid/bando",
                sha256="e" * 64,
                observed_at=verified,
            ),
        ),
        requirements=(),
        completeness_attested=True,
    )


def test_preview_does_not_leak_reference_count_or_statistics() -> None:
    observations = tuple(
        BenchmarkObservation(
            operation_code=f"OP-{i}",
            approved_funding_eur=100_000 + i,
            project_start=None,
            project_end=None,
            project_title=f"Secret comparable {i}",
        )
        for i in range(30)
    )
    result = preview(
        PreviewRequest(
            source_package=_package(),
            invalidated_at=None,
            observations=observations,
            as_of=datetime(2026, 9, 11, tzinfo=UTC),
        )
    )
    rendered = str(result)
    assert result.analysis_available is True
    assert result.historical_reference == "ANALYSIS_AVAILABLE"
    assert "30" not in rendered
    assert "Secret comparable" not in rendered
    assert "percentile" not in rendered.lower()
    assert "median" not in rendered.lower()


def test_preview_discloses_limited_reference_without_exact_n() -> None:
    observations = tuple(
        BenchmarkObservation(f"OP-{i}", 100_000 + i, None, None) for i in range(4)
    )
    result = preview(
        PreviewRequest(
            source_package=_package(),
            invalidated_at=None,
            observations=observations,
            as_of=datetime(2026, 9, 11, tzinfo=UTC),
        )
    )
    assert result.historical_reference == "LIMITED_REFERENCE"
    assert "4" not in result.customer_message
