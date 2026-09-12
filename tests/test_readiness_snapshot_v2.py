from datetime import UTC, date, datetime

import pytest

from procrun.domain import FundingProject, TemporalProvenance
from procrun.readiness_snapshot import build_snapshot_payload


def _project(code: str, amount: int) -> FundingProject:
    return FundingProject(
        operation_code=code,
        first_seen_at=datetime(2026, 9, 10, tzinfo=UTC),
        temporal_provenance=TemporalProvenance.RESOLVED,
        project_title=f"Project {code}",
        project_start=date(2025, 1, 1),
        project_end=date(2026, 1, 1),
        approved_funding_eur=amount,
        project_scope_text="Public project scope",
        fund="FESR",
        programme="PR FESR Lombardia 2021-2027",
        region="Lombardia",
        source_url="https://example.invalid/opencoesione",
    )


def test_snapshot_binds_exact_structured_cohort_source() -> None:
    payload, canonical, digest = build_snapshot_payload(
        snapshot_id="snap-1",
        data_through=date(2026, 9, 10),
        ingested_at=datetime(2026, 9, 11, tzinfo=UTC),
        projects=(_project("A", 100_000), _project("B", 200_000)),
        cohort_memberships={"A": ("BANDO:X",), "B": ("BANDO:X", "ACTION:1.1.3")},
        funding_source_id="opencoesione",
        funding_source_sha256="a" * 64,
        cohort_source_id="lombardia-structured",
        cohort_source_sha256="b" * 64,
    )
    assert payload["source_binding"]["cohort_source_sha256"] == "b" * 64
    assert payload["raw_record_count"] == 2
    assert len(payload["memberships"]) == 3
    assert len(canonical) > 0
    assert len(digest) == 64


def test_snapshot_never_infers_unknown_membership() -> None:
    with pytest.raises(ValueError, match="unknown operations"):
        build_snapshot_payload(
            snapshot_id="snap-1",
            data_through=date(2026, 9, 10),
            ingested_at=datetime(2026, 9, 11, tzinfo=UTC),
            projects=(_project("A", 100_000),),
            cohort_memberships={"NOT-IN-PROJECTS": ("BANDO:X",)},
            funding_source_id="opencoesione",
            funding_source_sha256="a" * 64,
            cohort_source_id="lombardia-structured",
            cohort_source_sha256="b" * 64,
        )
