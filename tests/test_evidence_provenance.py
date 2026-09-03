import os
from datetime import date, datetime, timezone

import psycopg
import pytest

from procrun.domain import EvidenceField, ProcurementEvidence, PurchaseComponent
from procrun.evidence_provenance import (
    append_component_source_span,
    append_procurement_source_span,
    load_component_source_span,
    load_procurement_source_span,
)
from procrun.ledger import (
    append_component_version,
    append_procurement_evidence_version,
    record_source_snapshot,
)
from procrun.migrations import apply_all_migrations

DATABASE_URL = os.environ.get("PROCRUN_TEST_DATABASE_URL")
pytestmark = pytest.mark.skipif(
    DATABASE_URL is None,
    reason="PostgreSQL integration DB not configured",
)


def connect() -> psycopg.Connection[tuple[object, ...]]:
    assert DATABASE_URL is not None
    return psycopg.connect(DATABASE_URL, autocommit=True)


def test_exact_source_spans_round_trip_from_empty_database() -> None:
    with connect() as conn:
        conn.execute("DROP SCHEMA IF EXISTS procrun CASCADE")
        apply_all_migrations(conn)

        component_text = "Fornecimento de bombas e sistemas de bombagem."
        component = PurchaseComponent(
            component_id="cmp-water-pumps",
            operation_code="PRR-TEST",
            category="water_wastewater:pumps",
            description="Pumps and pumping systems",
            scope_evidence=component_text,
            scope_evidence_start=0,
            scope_evidence_end=len(component_text),
        )
        component_write = append_component_version(
            conn,
            component=component,
            as_of=datetime(2026, 9, 3, 12, tzinfo=timezone.utc),
            extractor_version="component-taxonomy-v1",
        )
        append_component_source_span(
            conn,
            component_version_id=component_write.version_id,
            component=component,
        )

        scope = "Contrato para fornecimento de bombas e sistemas de bombagem."
        evidence_text = scope
        evidence = ProcurementEvidence(
            evidence_id="ev-1",
            component_id=component.component_id,
            notice_id="123456-2026",
            publication_date=date(2026, 6, 1),
            title="Equipamento de água",
            scope_description=scope,
            cpv_codes=("42122000",),
            project_reference="PRR-TEST",
            source_url="https://ted.europa.eu/en/notice/-/detail/123456-2026",
            evidence_field=EvidenceField.SCOPE_DESCRIPTION,
            evidence_text=evidence_text,
            evidence_start=0,
            evidence_end=len(evidence_text),
        )
        source_write = record_source_snapshot(
            conn,
            source_id="ted_search_api",
            source_record_id=evidence.notice_id,
            source_url=evidence.source_url,
            retrieved_at=datetime(2026, 9, 3, 12, tzinfo=timezone.utc),
            normalized=evidence,
            schema_version="ted-projection-v1",
            run_key="2026-09-03-test",
        )
        evidence_write = append_procurement_evidence_version(
            conn,
            evidence=evidence,
            source_record_version_id=source_write.version_id,
            as_of=datetime(2026, 9, 3, 12, tzinfo=timezone.utc),
        )
        append_procurement_source_span(
            conn,
            procurement_evidence_version_id=evidence_write.version_id,
            evidence=evidence,
        )

        persisted_component = load_component_source_span(conn, component_write.version_id)
        persisted_procurement = load_procurement_source_span(conn, evidence_write.version_id)

        assert persisted_component.text == component.scope_evidence
        assert persisted_component.start == component.scope_evidence_start
        assert persisted_component.end == component.scope_evidence_end
        assert persisted_procurement.text == evidence.evidence_text
        assert persisted_procurement.source_field == "scope_description"

        with pytest.raises(psycopg.Error):
            conn.execute(
                "UPDATE procrun.procurement_source_spans SET evidence_text = 'changed' "
                "WHERE procurement_evidence_version_id = %s",
                (evidence_write.version_id,),
            )
