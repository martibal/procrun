from datetime import date

from procrun.canonical_report import canonicalize_and_hash
from procrun.funding_benchmark import BenchmarkObservation
from procrun.preapplication_assessment import build_assessment_payload


def test_combined_payload_is_canonicalizable_and_descriptive_only() -> None:
    observations = tuple(
        BenchmarkObservation(
            operation_code=f"OP-{i:03d}",
            approved_funding_eur=100_000 + i * 10_000,
            project_start=date(2025, 1, 1),
            project_end=date(2026, 1, 1),
            project_title=f"Project {i}",
            source_url=f"https://example.invalid/{i}",
        )
        for i in range(30)
    )
    payload = build_assessment_payload(
        snapshot_id="snapshot-1",
        cohort_id="SAME_BANDO:BANDO-X",
        bando_code="BANDO-X",
        observations=observations,
        proposed_funding_eur=250_000,
        proposed_duration_months=12,
        ruleset=None,
        self_reported_inputs={},
    )
    canonical, digest = canonicalize_and_hash(payload)
    assert len(digest) == 64
    assert canonical.startswith(b"{")
    historical = payload["historical_dimensioning"]
    assert isinstance(historical, dict)
    results = historical["results"]
    assert isinstance(results, dict)
    funding = results["funding"]
    assert isinstance(funding, dict)
    assert isinstance(funding["user_percentile_bps"], int)
    assert "approval_probability" not in str(payload).lower()
    assert "recommended_funding" not in str(payload).lower()
