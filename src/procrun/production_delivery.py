"""Fail-closed non-web production delivery orchestration."""

from __future__ import annotations

import json
import os
import re
import tempfile
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Final

import psycopg

from procrun.collectors.opencoesione import (
    OPENCOESIONE_SOURCE_ID,
    OpenCoesioneBatch,
    to_funding_projects,
)
from procrun.collectors.opencoesione_live import collect_open_coesione_live
from procrun.collectors.ted import TED_SOURCE_ID, TedCollectionResult, collect_ted_notices
from procrun.component_engine import (
    COMPONENT_RULE_VERSION,
    RULES,
    ComponentDomain,
    ComponentRule,
    extract_components,
)
from procrun.domain import ProcurementEvidence, ProjectState, PurchaseComponent
from procrun.ingest.ted import normalize_ted_record
from procrun.ledger import (
    append_assessment_version,
    append_component_version,
    append_funding_project_version,
    append_procurement_evidence_version,
    append_project_assessment_version,
    append_run_manifest,
    apply_migrations,
    content_sha256,
    record_source_snapshot,
)
from procrun.matching import CandidateDisposition
from procrun.read_model import RunwayProject, build_runway_read_model
from procrun.runway import (
    PROJECT_CLASSIFIER_VERSION,
    ComponentCoverage,
    RunwayComponentResult,
    RunwayResult,
    assess_project_runway,
)

PRODUCTION_DELIVERY_VERSION: Final = "production-delivery-v1"
OPENCOESIONE_SCHEMA_VERSION: Final = "opencoesione-2021-2027-lombardia-v1"
TED_SCHEMA_VERSION: Final = "ted-projected-v1"
TED_COVERAGE_NOTE: Final = (
    "Coverage: TED. No relevant procurement means no matching procurement was found in the "
    "complete TED query universe through the stated cutoff. This does not establish absence "
    "outside TED, including national or below-threshold procedures."
)
TED_ITALY_QUERY_TEMPLATE: Final = (
    "buyer-country = ITA AND publication-date >= {start} AND publication-date <= {cutoff}"
)
TED_BOOTSTRAP_START: Final = date(2021, 1, 1)
ALL_COMPONENT_DOMAINS: Final = tuple(ComponentDomain)


class ProductionDeliveryError(RuntimeError):
    """Raised when a live run cannot satisfy the launch delivery contract."""


@dataclass(frozen=True)
class ProductionRunSummary:
    run_key: str
    cutoff_date: date
    funded_projects: int
    ted_records: int
    ted_pages: int
    projects_with_components: int
    published_projects: int
    useful_projects: int
    unresolved_projects: int
    source_sha256: str
    output_sha256: str


def ted_italy_query(cutoff_date: date, *, start_date: date = TED_BOOTSTRAP_START) -> str:
    if cutoff_date < start_date:
        raise ValueError("TED cutoff cannot predate bootstrap start")
    return TED_ITALY_QUERY_TEMPLATE.format(
        start=start_date.strftime("%Y%m%d"), cutoff=cutoff_date.strftime("%Y%m%d")
    )


def collect_complete_ted_italy(
    cutoff_date: date, *, page_size: int = 250, max_pages: int = 5000
) -> TedCollectionResult:
    result = collect_ted_notices(
        ted_italy_query(cutoff_date),
        page_size=page_size,
        max_pages=max_pages,
        scope="ALL",
    )
    if not result.complete:
        raise ProductionDeliveryError(
            "TED Italy coverage is incomplete; publication is prohibited: "
            f"stop_reason={result.stop_reason}, pages={result.pages_fetched}, "
            f"records={len(result.records)}, expected={result.total_notice_count}"
        )
    if result.total_notice_count is not None and len(result.records) != result.total_notice_count:
        raise ProductionDeliveryError("TED complete flag/count invariant failed")
    return result


def _rule_for_component(component: PurchaseComponent) -> ComponentRule:
    matches = tuple(
        rule for rule in RULES if f"{rule.domain.value}:{rule.category}" == component.category
    )
    if len(matches) != 1:
        raise ProductionDeliveryError(
            f"component category is not uniquely frozen: {component.category}"
        )
    return matches[0]


def _contains_phrase(text: str, phrase: str) -> bool:
    return re.search(rf"(?<!\w){re.escape(phrase)}(?!\w)", text, flags=re.IGNORECASE) is not None


def _candidate_record(record: dict[str, Any], component: PurchaseComponent) -> bool:
    rule = _rule_for_component(component)
    text = "\n".join(
        value
        for value in (
            str(record.get("title") or ""),
            str(record.get("scope_description") or ""),
        )
        if value
    )
    return any(_contains_phrase(text, phrase) for phrase in rule.phrases)


def _evidence_id(component_id: str, notice_id: str) -> str:
    digest = content_sha256(
        {"component_id": component_id, "notice_id": notice_id, "source": TED_SOURCE_ID}
    )
    return f"ted_{digest[:24]}"


def _component_evidence(
    component: PurchaseComponent,
    ted_records: tuple[dict[str, Any], ...],
    cutoff_date: date,
) -> tuple[ProcurementEvidence, ...]:
    evidence: list[ProcurementEvidence] = []
    for record in ted_records:
        if not _candidate_record(record, component):
            continue
        normalized = normalize_ted_record(
            record,
            evidence_id=_evidence_id(component.component_id, str(record["notice_id"])),
            component_id=component.component_id,
        )
        if normalized.publication_date <= cutoff_date:
            evidence.append(normalized)
    return tuple(evidence)


def build_live_runway_results(
    batch: OpenCoesioneBatch,
    ted: TedCollectionResult,
    *,
    cutoff_date: date,
) -> tuple[RunwayResult, ...]:
    if not ted.complete:
        raise ProductionDeliveryError("incomplete TED coverage cannot enter runway assessment")
    results: list[RunwayResult] = []
    for project in to_funding_projects(batch):
        extraction = extract_components(project, ALL_COMPONENT_DOMAINS)
        if not extraction.components:
            continue
        evidence_by_component: dict[str, tuple[ProcurementEvidence, ...]] = {}
        coverage_by_component: dict[str, ComponentCoverage] = {}
        for extracted in extraction.components:
            component = extracted.component
            evidence_by_component[component.component_id] = _component_evidence(
                component, ted.records, cutoff_date
            )
            coverage_by_component[component.component_id] = ComponentCoverage(
                required_source_ids=frozenset({TED_SOURCE_ID}),
                complete_source_ids=frozenset({TED_SOURCE_ID}),
                boundary_resolved=True,
                note=TED_COVERAGE_NOTE,
            )
        results.append(
            assess_project_runway(
                project,
                domains=ALL_COMPONENT_DOMAINS,
                cutoff_date=cutoff_date,
                evidence_by_component=evidence_by_component,
                coverage_by_component=coverage_by_component,
            )
        )
    return tuple(results)


def _candidate_audit(result_component: RunwayComponentResult) -> list[dict[str, Any]]:
    by_id = {
        candidate.evidence.evidence_id: candidate for candidate in result_component.candidates
    }
    rows: list[dict[str, Any]] = []
    for evaluation in result_component.match.evaluations:
        candidate = by_id[evaluation.evidence_id]
        rows.append(
            {
                "evidence_id": evaluation.evidence_id,
                "tier": evaluation.tier.value,
                "disposition": evaluation.disposition.value,
                "pre_cutoff": evaluation.pre_cutoff,
                "reason": evaluation.reason,
                "features": {
                    "exact_project_identifier": candidate.features.exact_project_identifier,
                    "geography_match": candidate.features.geography_match,
                    "high_scope_overlap": candidate.features.high_scope_overlap,
                    "cpv_or_category_match": candidate.features.cpv_or_category_match,
                    "compatible_date_window": candidate.features.compatible_date_window,
                    "project_title_or_location_match": (
                        candidate.features.project_title_or_location_match
                    ),
                },
            }
        )
    return rows


def persist_live_results(
    database_url: str,
    *,
    batch: OpenCoesioneBatch,
    results: tuple[RunwayResult, ...],
    read_models: tuple[RunwayProject, ...],
    run_key: str,
    started_at: datetime,
    completed_at: datetime,
    ted_count: int,
) -> None:
    projects = {project.operation_code: project for project in to_funding_projects(batch)}
    operations = {(item.cup or item.operation_id): item for item in batch.operations}
    with psycopg.connect(database_url) as conn:
        apply_migrations(conn)
        with conn.transaction():
            for result in results:
                project = projects[result.project.operation_code]
                operation = operations[project.operation_code]
                project_source = record_source_snapshot(
                    conn,
                    source_id=OPENCOESIONE_SOURCE_ID,
                    source_record_id=operation.operation_id,
                    source_url=project.source_url,
                    retrieved_at=batch.observed_at,
                    normalized=project,
                    schema_version=OPENCOESIONE_SCHEMA_VERSION,
                    run_key=run_key,
                )
                append_funding_project_version(
                    conn,
                    project=project,
                    source_record_version_id=project_source.version_id,
                    as_of=completed_at,
                )
                assessment_versions = []
                for component_result in result.components:
                    component = component_result.extracted.component
                    append_component_version(
                        conn,
                        component=component,
                        as_of=completed_at,
                        extractor_version=COMPONENT_RULE_VERSION,
                    )
                    evidence_versions = {}
                    for candidate in component_result.candidates:
                        evidence = candidate.evidence
                        source_write = record_source_snapshot(
                            conn,
                            source_id=TED_SOURCE_ID,
                            source_record_id=f"{evidence.notice_id}:{component.component_id}",
                            source_url=evidence.source_url,
                            retrieved_at=completed_at,
                            normalized=evidence,
                            schema_version=TED_SCHEMA_VERSION,
                            run_key=run_key,
                        )
                        evidence_write = append_procurement_evidence_version(
                            conn,
                            evidence=evidence,
                            source_record_version_id=source_write.version_id,
                            as_of=completed_at,
                        )
                        evidence_versions[evidence.evidence_id] = evidence_write.version_id
                    audit = _candidate_audit(component_result)
                    referenced = tuple(
                        evidence_versions[evidence_id]
                        for evidence_id in component_result.match.assessment.evidence_ids
                        if evidence_id in evidence_versions
                    )
                    rejected = [
                        row
                        for row in audit
                        if row["disposition"] == CandidateDisposition.REJECTED.value
                    ]
                    assessment_write = append_assessment_version(
                        conn,
                        assessment_id=(
                            f"{project.operation_code}:{component.component_id}:"
                            f"{result.cutoff_date.isoformat()}"
                        ),
                        operation_code=project.operation_code,
                        assessment=component_result.match.assessment,
                        as_of=completed_at,
                        rule_version=result.match_rule_version,
                        model_version=None,
                        matching_candidates=audit,
                        accepted_evidence_version_ids=referenced,
                        rejected_evidence=rejected,
                    )
                    assessment_versions.append(assessment_write.version_id)
                append_project_assessment_version(
                    conn,
                    assessment=result.assessment,
                    component_assessment_version_ids=tuple(assessment_versions),
                    as_of=completed_at,
                    classifier_version=PROJECT_CLASSIFIER_VERSION,
                )
            output_hash = content_sha256(
                [model.model_dump(mode="json") for model in read_models]
            )
            append_run_manifest(
                conn,
                run_key=run_key,
                started_at=started_at,
                completed_at=completed_at,
                classifier_version=PRODUCTION_DELIVERY_VERSION,
                counts={
                    "open_coesione_projects": len(batch.operations),
                    "ted_records": ted_count,
                    "runway_projects": len(results),
                    "published_projects": len(read_models),
                },
                input_sha256=batch.source_sha256,
                output_sha256=output_hash,
            )


def write_customer_safe_jsonl(path: Path, models: tuple[RunwayProject, ...]) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = "".join(
        json.dumps(model.model_dump(mode="json"), sort_keys=True, separators=(",", ":")) + "\n"
        for model in models
    )
    output_sha256 = content_sha256([model.model_dump(mode="json") for model in models])
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", dir=path.parent, delete=False, prefix=f".{path.name}."
    ) as handle:
        handle.write(payload)
        handle.flush()
        os.fsync(handle.fileno())
        temp_path = Path(handle.name)
    temp_path.replace(path)
    return output_sha256


def run_live_delivery(
    *, database_url: str, output_path: Path, cutoff_date: date | None = None
) -> ProductionRunSummary:
    started_at = datetime.now(timezone.utc)
    cutoff = cutoff_date or started_at.date()
    run_key = f"live-{cutoff.isoformat()}"
    batch = collect_open_coesione_live()
    projects = to_funding_projects(batch)
    if not projects:
        raise ProductionDeliveryError("OpenCoesione produced zero canonical funded projects")
    ted = collect_complete_ted_italy(cutoff)
    results = build_live_runway_results(batch, ted, cutoff_date=cutoff)
    read_models = tuple(build_runway_read_model(result) for result in results)
    useful = tuple(model for model in read_models if model.state is not ProjectState.UNRESOLVED)
    if not useful:
        raise ProductionDeliveryError(
            "live sources produced zero resolved customer runway projects; web build remains blocked"
        )
    completed_at = datetime.now(timezone.utc)
    persist_live_results(
        database_url,
        batch=batch,
        results=results,
        read_models=read_models,
        run_key=run_key,
        started_at=started_at,
        completed_at=completed_at,
        ted_count=len(ted.records),
    )
    output_sha256 = write_customer_safe_jsonl(output_path, read_models)
    return ProductionRunSummary(
        run_key=run_key,
        cutoff_date=cutoff,
        funded_projects=len(projects),
        ted_records=len(ted.records),
        ted_pages=ted.pages_fetched,
        projects_with_components=len(results),
        published_projects=len(read_models),
        useful_projects=len(useful),
        unresolved_projects=sum(model.state is ProjectState.UNRESOLVED for model in read_models),
        source_sha256=batch.source_sha256,
        output_sha256=output_sha256,
    )
