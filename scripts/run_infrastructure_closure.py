#!/usr/bin/env python3
"""One-shot live proof for ProcRun's own-code production infrastructure.

This is not a subjective classifier benchmark. Production claims are deliberately narrower: every
component must be anchored to exact approved project wording; CLOSED requires exact TED evidence;
OPEN means only that no match satisfying the frozen rules exists in the complete TED query universe;
all ambiguity becomes UNRESOLVED. Those claims can therefore be verified mechanically end-to-end.
"""

from __future__ import annotations

import argparse
import json
import signal
import time
from datetime import datetime, timezone
from pathlib import Path

import procrun.production_delivery as production_delivery
from procrun.a21_identity import a21_projects_by_local_operation_id
from procrun.collectors.opencoesione import to_funding_projects
from procrun.collectors.opencoesione_live import collect_open_coesione_live
from procrun.component_engine import extract_components
from procrun.domain import ComponentState, ProjectState
from procrun.ledger import content_sha256
from procrun.matching import CandidateDisposition
from procrun.production_delivery import (
    ALL_COMPONENT_DOMAINS,
    PRODUCTION_DELIVERY_VERSION,
    build_live_runway_results,
    collect_complete_ted_italy,
    persist_live_results,
    write_customer_safe_jsonl,
)
from procrun.read_model import build_runway_read_model

FORBIDDEN_PUBLIC_KEYS = frozenset(
    {
        "beneficiary",
        "beneficiary_name",
        "beneficiary_tax_code",
        "contracting_authority_name",
        "contact_person",
        "email",
        "phone",
        "raw_response",
        "iterationNextToken",
        "model_prompt",
    }
)
BUILD_PASS_BUDGET_SECONDS = 180


def _walk_public(value: object) -> None:
    if isinstance(value, dict):
        forbidden = FORBIDDEN_PUBLIC_KEYS.intersection(value)
        if forbidden:
            raise RuntimeError(f"customer read model contains forbidden keys: {sorted(forbidden)}")
        for child in value.values():
            _walk_public(child)
    elif isinstance(value, list | tuple):
        for child in value:
            _walk_public(child)


def _validate_run(results, models) -> dict[str, int]:
    if len(results) != len(models):
        raise RuntimeError("result/read-model count mismatch")

    counts = {
        "projects": len(models),
        "projects_open": 0,
        "projects_closed": 0,
        "projects_partial": 0,
        "projects_unresolved": 0,
        "projects_without_components": 0,
        "components": 0,
        "components_open": 0,
        "components_closed": 0,
        "components_unresolved": 0,
    }

    for result, model in zip(results, models, strict=True):
        if model.operation_code != result.project.operation_code:
            raise RuntimeError("read-model project identity mismatch")
        _walk_public(model.model_dump(mode="json"))
        counts[f"projects_{model.state.value.lower()}"] += 1

        if not result.components:
            counts["projects_without_components"] += 1
            if model.state is not ProjectState.UNRESOLVED:
                raise RuntimeError("component-free project escaped UNRESOLVED")
            if not model.unresolved_source_evidence:
                raise RuntimeError("component-free UNRESOLVED lacks exact source wording")

        if result.extraction.model_fallback_required and model.state is not ProjectState.UNRESOLVED:
            raise RuntimeError("ambiguous/unmatched project scope escaped UNRESOLVED")

        for item, public_component in zip(result.components, model.components, strict=True):
            counts["components"] += 1
            counts[f"components_{public_component.state.value.lower()}"] += 1
            span = public_component.project_evidence
            source = result.project.project_scope_text
            if source[span.start : span.end] != span.text:
                raise RuntimeError("component project evidence is not verbatim")

            evaluations = item.match.evaluations
            if public_component.state is ComponentState.OPEN:
                if any(
                    evaluation.disposition
                    in {CandidateDisposition.HIGH_CONFIDENCE, CandidateDisposition.REVIEW}
                    for evaluation in evaluations
                ):
                    raise RuntimeError("OPEN has an accepted or plausible review candidate")
                if "frozen exact-evidence rules" not in public_component.state_explanation:
                    raise RuntimeError("OPEN wording escaped the rule-bounded claim")
            elif public_component.state is ComponentState.CLOSED:
                if not public_component.procurement_matches:
                    raise RuntimeError("CLOSED lacks exact procurement evidence")
                for match in public_component.procurement_matches:
                    evidence = match.evidence
                    if evidence.end <= evidence.start or not evidence.text:
                        raise RuntimeError("CLOSED procurement span is invalid")
            elif public_component.state is ComponentState.UNRESOLVED:
                pass
            else:
                raise RuntimeError("unknown component state")

    if not models:
        raise RuntimeError("live closure run produced zero projects")
    if counts["projects_open"] + counts["projects_closed"] + counts["projects_partial"] < 1:
        raise RuntimeError("live closure run produced no resolved customer result")
    return counts


def _timeout_handler(signum, frame) -> None:
    del signum, frame
    raise TimeoutError(
        f"runway build exceeded {BUILD_PASS_BUDGET_SECONDS}s preflight budget; optimize before retry"
    )


def _build_with_budget(batch, ted, *, cutoff):
    previous_handler = signal.signal(signal.SIGALRM, _timeout_handler)
    signal.alarm(BUILD_PASS_BUDGET_SECONDS)
    started = time.monotonic()
    try:
        result = build_live_runway_results(batch, ted, cutoff_date=cutoff)
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, previous_handler)
    return result, time.monotonic() - started


def _install_candidate_index_cache(batch, logical_projects, ted):
    operations = {operation.operation_id: operation for operation in batch.operations}
    categories: set[str] = set()
    for project in logical_projects:
        if project.operation_code not in operations:
            raise RuntimeError("logical project operation missing from source batch")
        extraction = extract_components(project, ALL_COMPONENT_DOMAINS)
        categories.update(item.component.category for item in extraction.components)

    category_set = frozenset(categories)
    started = time.monotonic()
    candidate_index = production_delivery._build_candidate_index(ted.records, category_set)
    index_seconds = time.monotonic() - started
    original_builder = production_delivery._build_candidate_index
    cache_hits = {"count": 0}

    def cached_builder(ted_records, requested_categories):
        if ted_records is ted.records and requested_categories == category_set:
            cache_hits["count"] += 1
            return candidate_index
        return original_builder(ted_records, requested_categories)

    production_delivery._build_candidate_index = cached_builder
    candidate_count = sum(len(records) for records in candidate_index.values())
    return index_seconds, candidate_count, cache_hits


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--database-url", required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--jsonl", type=Path, required=True)
    args = parser.parse_args()

    started = datetime.now(timezone.utc)
    cutoff = started.date()
    batch = collect_open_coesione_live()
    logical_projects = a21_projects_by_local_operation_id(
        batch.operations, to_funding_projects(batch)
    )
    ted = collect_complete_ted_italy(cutoff)

    index_seconds, indexed_candidate_count, cache_hits = _install_candidate_index_cache(
        batch, logical_projects, ted
    )

    serialized_runs: list[str] = []
    build_seconds: list[float] = []
    first_results = None
    first_models = None
    first_counts = None
    for _ in range(3):
        results, elapsed = _build_with_budget(batch, ted, cutoff=cutoff)
        build_seconds.append(elapsed)
        if len(results) != len(logical_projects):
            raise RuntimeError("one or more logical funded projects were omitted")
        models = tuple(build_runway_read_model(result) for result in results)
        counts = _validate_run(results, models)
        serialized_runs.append(
            content_sha256([model.model_dump(mode="json") for model in models])
        )
        if first_results is None:
            first_results = results
            first_models = models
            first_counts = counts

    if cache_hits["count"] != 3:
        raise RuntimeError(f"TED candidate index was not reused for all builds: {cache_hits['count']}")
    if len(set(serialized_runs)) != 1:
        raise RuntimeError(f"three-run determinism failure: {serialized_runs}")
    assert first_results is not None
    assert first_models is not None
    assert first_counts is not None

    completed = datetime.now(timezone.utc)
    persist_live_results(
        args.database_url,
        batch=batch,
        results=first_results,
        read_models=first_models,
        run_key=f"infrastructure-closure-{cutoff.isoformat()}",
        started_at=started,
        completed_at=completed,
        ted_count=len(ted.records),
    )
    written_hash = write_customer_safe_jsonl(args.jsonl, first_models)
    if written_hash != serialized_runs[0]:
        raise RuntimeError("persisted customer JSONL hash differs from in-memory proof hash")
    if len(args.jsonl.read_text(encoding="utf-8").splitlines()) != len(first_models):
        raise RuntimeError("customer JSONL line count mismatch")

    report = {
        "schema_version": "infrastructure-closure-v1",
        "decision": "PASS",
        "production_delivery_version": PRODUCTION_DELIVERY_VERSION,
        "cutoff_date": cutoff.isoformat(),
        "source_resource_sha256": batch.source_sha256,
        "logical_project_count": len(logical_projects),
        "ted_record_count": len(ted.records),
        "ted_page_count": ted.pages_fetched,
        "ted_complete": ted.complete,
        "three_run_determinism": True,
        "candidate_index_reused": True,
        "candidate_index_build_seconds": round(index_seconds, 3),
        "indexed_candidate_count": indexed_candidate_count,
        "runway_build_seconds": [round(value, 3) for value in build_seconds],
        "build_pass_budget_seconds": BUILD_PASS_BUDGET_SECONDS,
        "customer_output_sha256": serialized_runs[0],
        "sealed_holdout_required": False,
        "sealed_holdout_touched": False,
        "claim_semantics": "evidence-bounded exact-rule observation",
        "counts": first_counts,
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
