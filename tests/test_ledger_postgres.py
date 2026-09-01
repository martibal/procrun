import os
from datetime import date, datetime, timezone

import psycopg
import pytest

from procrun.domain import (
    ComponentAssessment,
    ComponentState,
    ProcurementEvidence,
    ProjectAssessment,
    ProjectState,
    PurchaseComponent,
)
from procrun.ledger import (
    append_assessment_version,
    append_component_version,
    append_outcome_version,
    append_procurement_evidence_version,
    append_project_assessment_version,
    append_run_manifest,
    apply_migrations,
    content_sha256,
    record_source_snapshot,
)
from procrun.source_contracts import SourceNotApprovedError

DATABASE_URL = os.environ.get("PROCRUN_TEST_DATABASE_URL")
pytestmark = pytest.mark.skipif(
    DATABASE_URL is None,
    reason="PostgreSQL integration DB not configured",
)


def connect() -> psycopg.Connection[tuple[object, ...]]:
    assert DATABASE_URL is not None
    return psycopg.connect(DATABASE_URL, autocommit=True)


def reset_schema() -> None:
    with connect() as conn:
        conn.execute("DROP SCHEMA IF EXISTS procrun CASCADE")
        apply_migrations(conn)


def evidence(title: str = "Water infrastructure works") -> ProcurementEvidence:
    return ProcurementEvidence(
        evidence_id="ev-1",
        component_id="component-water",
        notice_id="notice-1",
        publication_date=date(2026, 8, 20),
        title=title,
        cpv_codes=("45200000",),
        procedure_value_eur=500_000,
        project_reference="PACS-FC-TEST",
        source_url="https://example.invalid/notice/notice-1",
    )


def test_schema_has_pg_trgm_and_append_only_trigger() -> None:
    reset_schema()
    with connect() as conn:
        assert conn.execute(
            "SELECT 1 FROM pg_extension WHERE extname = 'pg_trgm'"
        ).fetchone() == (1,)
        source = record_source_snapshot(
            conn,
            source_id="ted_search_api",
            source_record_id="notice-1",
            source_url="https://example.invalid/notice/notice-1",
            retrieved_at=datetime(2026, 9, 1, 12, tzinfo=timezone.utc),
            normalized=evidence(),
            schema_version="ted-projection-v1",
            run_key="2026-09-01-daily",
        )
        with pytest.raises(psycopg.Error):
            conn.execute(
                "UPDATE procrun.source_record_versions SET source_url = %s WHERE version_id = %s",
                ("https://mutated.invalid", source.version_id),
            )


def test_source_versions_are_idempotent_superseding_and_revertible() -> None:
    reset_schema()
    with connect() as conn:
        first = record_source_snapshot(
            conn,
            source_id="ted_search_api",
            source_record_id="notice-1",
            source_url="https://example.invalid/notice/notice-1",
            retrieved_at=datetime(2026, 9, 1, 12, tzinfo=timezone.utc),
            normalized=evidence(),
            schema_version="ted-projection-v1",
            run_key="2026-09-01-daily",
        )
        repeat = record_source_snapshot(
            conn,
            source_id="ted_search_api",
            source_record_id="notice-1",
            source_url="https://example.invalid/notice/notice-1",
            retrieved_at=datetime(2026, 9, 1, 12, 5, tzinfo=timezone.utc),
            normalized=evidence(),
            schema_version="ted-projection-v1",
            run_key="2026-09-01-daily",
        )
        assert repeat.version_id == first.version_id
        assert not repeat.inserted
        source_count = conn.execute(
            "SELECT count(*) FROM procrun.source_record_versions"
        ).fetchone()
        assert source_count == (1,)
        assert conn.execute("SELECT count(*) FROM procrun.source_retrievals").fetchone() == (1,)

        corrected = record_source_snapshot(
            conn,
            source_id="ted_search_api",
            source_record_id="notice-1",
            source_url="https://example.invalid/notice/notice-1",
            retrieved_at=datetime(2026, 9, 2, 12, tzinfo=timezone.utc),
            normalized=evidence("Corrected water infrastructure works"),
            schema_version="ted-projection-v1",
            run_key="2026-09-02-daily",
        )
        assert corrected.version_id != first.version_id
        assert corrected.supersedes_version_id == first.version_id

        reverted = record_source_snapshot(
            conn,
            source_id="ted_search_api",
            source_record_id="notice-1",
            source_url="https://example.invalid/notice/notice-1",
            retrieved_at=datetime(2026, 9, 3, 12, tzinfo=timezone.utc),
            normalized=evidence(),
            schema_version="ted-projection-v1",
            run_key="2026-09-03-daily",
        )
        assert reverted.content_sha256 == first.content_sha256
        assert reverted.version_id not in {first.version_id, corrected.version_id}
        assert reverted.supersedes_version_id == corrected.version_id
        source_count = conn.execute(
            "SELECT count(*) FROM procrun.source_record_versions"
        ).fetchone()
        assert source_count == (3,)


def test_unapproved_source_is_rejected_before_persistence() -> None:
    reset_schema()
    with connect() as conn, pytest.raises(SourceNotApprovedError):
        record_source_snapshot(
            conn,
            source_id="pt2030_project_search",
            source_record_id="PACS-FC-TEST",
            source_url="https://example.invalid/project",
            retrieved_at=datetime(2026, 9, 1, 12, tzinfo=timezone.utc),
            normalized=evidence(),
            schema_version="pt2030-v1",
        )


def test_component_project_outcome_and_manifest_are_versioned() -> None:
    reset_schema()
    with connect() as conn:
        source = record_source_snapshot(
            conn,
            source_id="ted_search_api",
            source_record_id="notice-1",
            source_url="https://example.invalid/notice/notice-1",
            retrieved_at=datetime(2026, 9, 1, 12, tzinfo=timezone.utc),
            normalized=evidence(),
            schema_version="ted-projection-v1",
            run_key="2026-09-01-daily",
        )
        component = PurchaseComponent(
            component_id="component-water",
            operation_code="PACS-FC-TEST",
            category="civil-works",
            description="Water infrastructure civil works",
            scope_evidence="Construction of water infrastructure.",
        )
        component_write = append_component_version(
            conn,
            component=component,
            as_of=datetime(2026, 9, 1, 13, tzinfo=timezone.utc),
            extractor_version="rules-v1",
        )
        evidence_write = append_procurement_evidence_version(
            conn,
            evidence=evidence(),
            source_record_version_id=source.version_id,
            as_of=datetime(2026, 9, 1, 13, tzinfo=timezone.utc),
        )
        assessment = ComponentAssessment(
            component_id="component-water",
            state=ComponentState.CLOSED,
            cutoff_date=date(2026, 8, 31),
            rationale="Pre-cutoff procurement covers the component.",
            evidence_ids=("ev-1",),
            coverage_note="TED indexed through cutoff.",
        )
        assessment_write = append_assessment_version(
            conn,
            assessment_id="assessment-water",
            operation_code="PACS-FC-TEST",
            assessment=assessment,
            as_of=datetime(2026, 9, 1, 13, tzinfo=timezone.utc),
            rule_version="match-rules-v1",
            model_version=None,
            matching_candidates=({"evidence_id": "ev-1", "score": 1.0},),
            accepted_evidence_version_ids=(evidence_write.version_id,),
            rejected_evidence=(),
        )
        project_assessment = ProjectAssessment(
            operation_code="PACS-FC-TEST",
            state=ProjectState.CLOSED,
            cutoff_date=date(2026, 8, 31),
            components=(assessment,),
        )
        project_write = append_project_assessment_version(
            conn,
            assessment=project_assessment,
            component_assessment_version_ids=(assessment_write.version_id,),
            as_of=datetime(2026, 9, 1, 13, tzinfo=timezone.utc),
            classifier_version="match-rules-v1",
        )
        outcome = append_outcome_version(
            conn,
            outcome_id="outcome-water-1",
            assessment_version_id=assessment_write.version_id,
            procurement_evidence_version_id=evidence_write.version_id,
            original_signal_at=datetime(2026, 9, 1, 13, tzinfo=timezone.utc),
            outcome_date=date(2027, 2, 14),
            as_of=datetime(2027, 2, 14, 12, tzinfo=timezone.utc),
        )
        assert component_write.inserted
        assert project_write.inserted
        assert outcome.inserted
        assert conn.execute(
            "SELECT lead_days FROM procrun.outcome_versions WHERE version_id = %s",
            (outcome.version_id,),
        ).fetchone() == (166,)

        digest = content_sha256({"source": source.content_sha256})
        manifest = append_run_manifest(
            conn,
            run_key="2026-09-01-daily",
            started_at=datetime(2026, 9, 1, 12, tzinfo=timezone.utc),
            completed_at=datetime(2026, 9, 1, 13, tzinfo=timezone.utc),
            classifier_version="match-rules-v1",
            counts={"source_records": 1, "components": 1, "assessments": 1},
            input_sha256=digest,
            output_sha256=project_write.content_sha256,
        )
        repeat = append_run_manifest(
            conn,
            run_key="2026-09-01-daily",
            started_at=datetime(2026, 9, 1, 12, tzinfo=timezone.utc),
            completed_at=datetime(2026, 9, 1, 13, 5, tzinfo=timezone.utc),
            classifier_version="match-rules-v1",
            counts={"source_records": 1, "components": 1, "assessments": 1},
            input_sha256=digest,
            output_sha256=project_write.content_sha256,
        )
        assert repeat.version_id == manifest.version_id
        assert not repeat.inserted
        assert conn.execute("SELECT count(*) FROM procrun.run_manifests").fetchone() == (1,)
