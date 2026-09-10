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

from procrun.a21_identity import a21_projects_by_local_operation_id
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
    cpv_matches_prefixes,
    extract_components,
)
from procrun.domain import FundingProject, ProcurementEvidence, ProjectState, PurchaseComponent
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

PRODUCTION_DELIVERY_VERSION: Final = "production-delivery-v2-evidence-bounded"
OPENCOESIONE_SCHEMA_VERSION: Final = "opencoesione-2021-2027-lombardia-v1"
TED_SCHEMA_VERSION: Final = "ted-projected-v1"
TED_COVERAGE_NOTE: Final = (
    "Coverage: complete TED Italy query universe through the stated cutoff. OPEN means only that "
    "no procurement match satisfying ProcRun's frozen exact-evidence rules was found in that "
    "universe. It does not establish absence outside TED or under different wording/classification."
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


def _ted_year_ranges(cutoff_date: date) -> tuple[tuple[date, date], ...]:
    """Return non-overlapping chronological year segments covering the complete TED window."""
    if cutoff_date < TED_BOOTSTRAP_START:
        raise ValueError("TED cutoff cannot predate bootstrap start")
    return tuple(
        (
            max(TED_BOOTSTRAP_START, date(year, 1, 1)),
            min(cutoff_date, date(year, 12, 31)),
        )
        for year in range(TED_BOOTSTRAP_START.year, cutoff_date.year + 1)
    )


def _collect_complete_ted_segment(
    start_date: date,
    end_date: date,
    *,
    page_size: int,
    max_pages: int,
) -> TedCollectionResult:
    result = collect_ted_notices(
        ted_italy_query(end_date, start_date=start_date),
        page_size=page_size,
        max_pages=max_pages,
        scope="ALL",
    )
    segment = f"{start_date.isoformat()}..{end_date.isoformat()}"
    if not result.complete:
        raise ProductionDeliveryError(
            "TED Italy segment coverage is incomplete; publication is prohibited: "
            f"segment={segment}, stop_reason={result.stop_reason}, pages={result.pages_fetched}, "
            f"records={len(result.records)}, expected={result.total_notice_count}"
        )
    if result.total_notice_count is not None and len(result.records) != result.total_notice_count:
        raise ProductionDeliveryError(f"TED segment complete flag/count invariant failed: {segment}")
    return result


def collect_complete_ted_italy(
    cutoff_date: date, *, page_size: int = 250, max_pages: int = 5000
) -> TedCollectionResult:
    """Collect the complete TED universe using deterministic sequential year segments.

    Year segmentation preserves the exact publication-date universe while avoiding concurrent
    request bursts that trigger TED throttling. Each segment is independently count-checked and the
    merged result is deterministically ordered before classification.
    """
    ranges = _ted_year_ranges(cutoff_date)
    results_by_start: dict[date, TedCollectionResult] = {}
    for start, end in ranges:
        results_by_start[start] = _collect_complete_ted_segment(
            start,
            end,
            page_size=page_size,
            max_pages=max_pages,
        )

    records: list[dict[str, Any]] = []
    pages_fetched = 0
    expected_total = 0
    total_known = True
    seen_records: set[tuple[str, str]] = set()
    for start, _ in ranges:
        result = results_by_start[start]
        pages_fetched += result.pages_fetched
        if result.total_notice_count is None:
            total_known = False
        else:
            expected_total += result.total_notice_count
        for record in result.records:
            identity = (
                str(record.get("notice_id") or ""),
                str(record.get("publication_date") or ""),
            )
            if not all(identity):
                raise ProductionDeliveryError("TED segmented merge encountered missing record identity")
            if identity in seen_records:
                raise ProductionDeliveryError(
                    "TED segmented merge encountered duplicate/overlapping record identity: "
                    f"{identity[0]}@{identity[1]}"
                )
            seen_records.add(identity)
            records.append(record)

    records.sort(
        key=lambda record: (
            str(record.get("publication_date") or ""),
            str(record.get("notice_id") or ""),
        )
    )
    total_notice_count = expected_total if total_known else None
    if total_notice_count is not None and len(records) != total_notice_count:
        raise ProductionDeliveryError("TED segmented complete-count invariant failed")
    return TedCollectionResult(
        records=tuple(records),
        total_notice_count=total_notice_count,
        pages_fetched=pages_fetched,
        complete=True,
        stop_reason="complete_segmented",
    )


def _rule_key(rule: ComponentRule) -> str:
    return f"{rule.domain.value}:{rule.category}"


def _rule_for_component(component: PurchaseComponent) -> ComponentRule:
    matches = tuple(rule for rule in RULES if _rule_key(rule) == component.category)
    if len(matches) != 1:
        raise ProductionDeliveryError(
            f"component category is not uniquely frozen: {component.category}"
        )
    return matches[0]


def _contains_phrase(text: str, phrase: str) -> bool:
    return re.search(rf"(?<!\w){re.escape(phrase)}(?!\w)", text, flags=re.IGNORECASE) is not None


def _record_cpv_codes(record: dict[str, Any]) -> tuple[str, ...]:
    raw = record.get("cpv_codes") or ()
    if isinstance(raw, str):
        return (raw,)
    if isinstance(raw, list | tuple):
        return tuple(str(value) for value in raw)
    return ()


def _candidate_record_for_rule(
    record: dict[str, Any],
    rule: ComponentRule,
    *,
    text: str | None = None,
    cpv_codes: tuple[str, ...] | None = None,
) -> bool:
    candidate_text = text
    if candidate_text is None:
        candidate_text = "\n".join(
            value
            for value in (
                str(record.get("title") or ""),
                str(record.get("scope_description") or ""),
            )
            if value
        )
    candidate_cpv_codes = cpv_codes if cpv_codes is not None else _record_cpv_codes(record)
    phrase_match = any(_contains_phrase(candidate_text, phrase) for phrase in rule.phrases)
    cpv_match = bool(rule.cpv_prefixes) and any(
        cpv_matches_prefixes(code, rule.cpv_prefixes) for code in candidate_cpv_codes
    )
    return phrase_match or cpv_match


def _candidate_record(record: dict[str, Any], component: PurchaseComponent) -> bool:
    return _candidate_record_for_rule(record, _rule_for_component(component))


def _build_candidate_index(
    ted_records: tuple[dict[str, Any], ...],
    categories: frozenset[str],
) -> dict[str, tuple[dict[str, Any], ...]]:
    rules_by_category = {_rule_key(rule): rule for rule in RULES if _rule_key(rule) in categories}
    if set(rules_by_category) != set(categories):
        missing = sorted(set(categories) - set(rules_by_category))
        raise ProductionDeliveryError(f"component categories are not uniquely frozen: {missing}")
    mutable: dict[str, list[dict[str, Any]]] = {category: [] for category in categories}
    for record in ted_records:
        text = "\n".join(
            value
            for value in (
                str(record.get("title") or ""),
                str(record.get("scope_description") or ""),
            )
            if value
        )
        cpv_codes = _record_cpv_codes(record)
        for category, rule in rules_by_category.items():
            if _candidate_record_for_rule(record, rule, text=text, cpv_codes=cpv_codes):
                mutable[category].append(record)
    return {category: tuple(records) for category, records in mutable.items()}


def _evidence_id(component_id: str, notice_id: str) -> str:
    digest = content_sha256(
        {"component_id": component_id, "notice_id": notice_id, "source": TED_SOURCE_ID}
    )
    return f"ted_{digest[:24]}"


def _component_evidence(
    component: PurchaseComponent,
    candidate_records: tuple[dict[str, Any], ...],
    cutoff_date: date,
) -> tuple[ProcurementEvidence, ...]:
    evidence: list[ProcurementEvidence] = []
    for record in candidate_records:
        normalized = normalize_ted_record(
            record,
            evidence_id=_evidence_id(component.component_id, str(record["notice_id"])),
            component_id=component.component_id,
        )
        if normalized.publication_date <= cutoff_date:
            evidence.append(normalized)
    return tuple(evidence)


def _logical_projects(batch: OpenCoesioneBatch) -> tuple[FundingProject, ...]:
    return a21_projects_by_local_operation_id(batch.operations, to_funding_projects(batch))


def build_live_runway_results(
    batch: OpenCoesioneBatch,
    ted: TedCollectionResult,
    *,
    cutoff_date: date,
) -> tuple[RunwayResult, ...]:
    if not ted.complete:
        raise ProductionDeliveryError("incomplete TED coverage cannot enter runway assessment")
    operations = {operation.operation_id: operation for operation in batch.operations}
    prepared: list[tuple[FundingProject, Any, Any]] = []
    categories: set[str] = set()
    for project in _logical_projects(batch):
        operation = operations[project.operation_code]
        extraction = extract_components(project, ALL_COMPONENT_DOMAINS)
        prepared.append((project, operation, extraction))
        categories.update(item.component.category for item in extraction.components)
    candidate_index = _build_candidate_index(ted.records, frozenset(categories))
    results: list[RunwayResult] = []
    for project, operation, extraction in prepared:
        evidence_by_component: dict[str, tuple[ProcurementEvidence, ...]] = {}
        coverage_by_component: dict[str, ComponentCoverage] = {}
        for extracted in extraction.components:
            component = extracted.component
            evidence_by_component[component.component_id] = _component_evidence(
                component, candidate_index[component.category], cutoff_date
            )
            coverage_by_component[component.component_id] = ComponentCoverage(
                required_source_ids=frozenset({TED_SOURCE_ID}),
                complete_source_ids=frozenset({TED_SOURCE_ID}),
                boundary_resolved=True,
                note=TED_COVERAGE_NOTE,
            )
        references = tuple(
            dict.fromkeys(
                value
                for value in (operation.operation_id, operation.cup)
                if value is not None and value.strip()
            )
        )
        results.append(
            assess_project_runway(
                project,
                domains=ALL_COMPONENT_DOMAINS,
                cutoff_date=cutoff_date,
                evidence_by_component=evidence_by_component,
                coverage_by_component=coverage_by_component,
                project_reference_codes=references,
            )
        )
    return tuple(results)


def _candidate_audit(result_component: RunwayComponentResult) -> list[dict[str, Any]]:
    by_id = {candidate.evidence.evidence_id: candidate for candidate in result_component.candidates}
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
                    "project_title_or_location_match": candidate.features.project_title_or_location_match,
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
    projects = {project.operation_code: project for project in _logical_projects(batch)}
    operations = {item.operation_id: item for item in batch.operations}
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
                        row for row in audit if row["disposition"] == CandidateDisposition.REJECTED.value
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
            output_hash = content_sha256([model.model_dump(mode="json") for model in read_models])
            append_run_manifest(
                conn,
                run_key=run_key,
                started_at=started_at,
                completed_at=completed_at,
                classifier_version=PRODUCTION_DELIVERY_VERSION,
                counts={
                    "open_coesione_raw_rows": len(batch.operations),
                    "open_coesione_logical_projects": len(projects),
                    "ted_records": ted_count,
                    "runway_projects": len(results),
                    "published_projects": len(read_models),
                    "projects_with_components": sum(bool(item.components) for item in results),
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
    projects = _logical_projects(batch)
    if not projects:
        raise ProductionDeliveryError("OpenCoesione produced zero canonical funded projects")
    ted = collect_complete_ted_italy(cutoff)
    results = build_live_runway_results(batch, ted, cutoff_date=cutoff)
    if len(results) != len(projects):
        raise ProductionDeliveryError("production runway omitted one or more funded projects")
    read_models = tuple(build_runway_read_model(result) for result in results)
    useful = tuple(model for model in read_models if model.state is not ProjectState.UNRESOLVED)
    if not useful:
        raise ProductionDeliveryError(
            "live sources produced zero resolved customer runway projects; publication is prohibited"
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
        projects_with_components=sum(bool(result.components) for result in results),
        published_projects=len(read_models),
        useful_projects=len(useful),
        unresolved_projects=sum(model.state is ProjectState.UNRESOLVED for model in read_models),
        source_sha256=batch.source_sha256,
        output_sha256=output_sha256,
    )
