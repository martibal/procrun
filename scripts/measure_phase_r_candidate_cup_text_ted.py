#!/usr/bin/env python3
"""Aggregate-only exact CUP-in-TED-text validation for Phase R candidates."""

from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

from procrun.a21_identity import a21_projects_by_local_operation_id
from procrun.collectors.opencoesione import to_funding_projects
from procrun.collectors.opencoesione_live import collect_open_coesione_live
from procrun.phase_r_candidate_component_design import candidate_cpv_match
from procrun.production_delivery import collect_complete_ted_italy
from scripts.measure_lombardia_socrata_structured_coverage import (
    FROZEN_PROJECT_COUNT,
    FROZEN_SOURCE_SHA256,
    _classification_signature,
    _fetch_safe_rows,
    _normalize_cup,
    _normalize_intervention_code,
)
from scripts.measure_phase_r_candidate_domains import CANDIDATE_RULES

REPORT_PATH = Path("artifacts/phase-r-candidate-cup-text-ted-validation.json")
FROZEN_TED_CUTOFF = date(2026, 9, 12)


def _action(value: object) -> str:
    return str(value or "").strip()


def _normalized_cpv(value: object) -> str:
    return "".join(ch for ch in str(value or "") if ch.isdigit())[:8]


def _contains_exact_cup(text: object, cup: str) -> bool:
    if not isinstance(text, str) or not text:
        return False
    return re.search(rf"(?<![A-Z0-9]){re.escape(cup)}(?![A-Z0-9])", text.upper()) is not None


def main() -> int:
    batch = collect_open_coesione_live()
    if batch.source_sha256 != FROZEN_SOURCE_SHA256:
        raise RuntimeError("candidate CUP text validation requires exact frozen OpenCoesione source")

    projects = a21_projects_by_local_operation_id(batch.operations, to_funding_projects(batch))
    if len(projects) != FROZEN_PROJECT_COUNT:
        raise RuntimeError("frozen Phase R project count drift")

    cup_by_operation_id: dict[str, str | None] = {}
    for operation in batch.operations:
        cup = _normalize_cup(operation.cup)
        existing = cup_by_operation_id.get(operation.operation_id)
        if operation.operation_id in cup_by_operation_id and existing != cup:
            raise RuntimeError("conflicting CUP values in frozen OpenCoesione source")
        cup_by_operation_id[operation.operation_id] = cup

    source_by_cup: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in _fetch_safe_rows():
        cup = _normalize_cup(row.get("cup"))
        if cup is not None:
            source_by_cup[cup].append(row)

    safe_row_by_cup: dict[str, dict[str, object]] = {}
    conflicting_cups: set[str] = set()
    for cup, rows in source_by_cup.items():
        signatures = {_classification_signature(row) for row in rows}
        if len(signatures) != 1:
            conflicting_cups.add(cup)
        else:
            safe_row_by_cup[cup] = rows[0]

    candidate_projects_by_domain: dict[str, dict[str, str]] = {
        name: {} for name in CANDIDATE_RULES
    }
    for project in projects:
        cup = cup_by_operation_id.get(project.operation_code)
        if cup is None or cup in conflicting_cups:
            continue
        row = safe_row_by_cup.get(cup)
        if row is None:
            continue
        code = _normalize_intervention_code(row.get("codice_tipologia_intervento"))
        action = _action(row.get("azione"))
        for name, rule in CANDIDATE_RULES.items():
            if code == rule["intervention_code"] and action == rule["azione"]:
                candidate_projects_by_domain[name][project.operation_code] = cup

    for name, rule in CANDIDATE_RULES.items():
        expected = int(rule["expected_projects"])
        actual = len(candidate_projects_by_domain[name])
        if actual != expected:
            raise RuntimeError(
                f"candidate project cohort drift for {name}: expected={expected}, actual={actual}"
            )

    ted = collect_complete_ted_italy(FROZEN_TED_CUTOFF)
    if not ted.complete:
        raise RuntimeError("TED universe is incomplete")

    hit_notices_by_domain: Counter[str] = Counter()
    hit_notices_by_field: Counter[str] = Counter()
    hit_projects_by_domain: dict[str, set[str]] = {name: set() for name in CANDIDATE_RULES}
    title_hit_projects_by_domain: dict[str, set[str]] = {name: set() for name in CANDIDATE_RULES}
    scope_hit_projects_by_domain: dict[str, set[str]] = {name: set() for name in CANDIDATE_RULES}

    cups_to_projects: dict[str, dict[str, set[str]]] = {}
    for domain, project_map in candidate_projects_by_domain.items():
        index: dict[str, set[str]] = defaultdict(set)
        for operation_code, cup in project_map.items():
            index[cup].add(operation_code)
        cups_to_projects[domain] = index

    for record in ted.records:
        cpv_codes = tuple(_normalized_cpv(code) for code in record.get("cpv_codes", ()))
        cpv_codes = tuple(code for code in cpv_codes if code)
        title = record.get("title")
        scope = record.get("scope_description")

        for domain in CANDIDATE_RULES:
            if not any(candidate_cpv_match(domain, code) for code in cpv_codes):
                continue
            notice_hit = False
            for cup, operation_codes in cups_to_projects[domain].items():
                in_title = _contains_exact_cup(title, cup)
                in_scope = _contains_exact_cup(scope, cup)
                if not in_title and not in_scope:
                    continue
                notice_hit = True
                hit_projects_by_domain[domain].update(operation_codes)
                if in_title:
                    title_hit_projects_by_domain[domain].update(operation_codes)
                if in_scope:
                    scope_hit_projects_by_domain[domain].update(operation_codes)
            if notice_hit:
                hit_notices_by_domain[domain] += 1
                if any(
                    _contains_exact_cup(title, cup)
                    for cup in cups_to_projects[domain]
                ):
                    hit_notices_by_field[f"{domain}:title"] += 1
                if any(
                    _contains_exact_cup(scope, cup)
                    for cup in cups_to_projects[domain]
                ):
                    hit_notices_by_field[f"{domain}:scope_description"] += 1

    report = {
        "schema_version": "phase-r-candidate-cup-text-ted-validation-v1",
        "ted_cutoff": FROZEN_TED_CUTOFF.isoformat(),
        "ted_complete": ted.complete,
        "ted_stop_reason": ted.stop_reason,
        "ted_notice_count": len(ted.records),
        "ted_pages_fetched": ted.pages_fetched,
        "candidate_project_count_by_domain": {
            name: len(projects_by_id)
            for name, projects_by_id in sorted(candidate_projects_by_domain.items())
        },
        "exact_cup_text_hit_notices_by_domain": dict(sorted(hit_notices_by_domain.items())),
        "exact_cup_text_hit_notices_by_field": dict(sorted(hit_notices_by_field.items())),
        "candidate_projects_with_exact_cup_text_plus_cpv_hit_by_domain": {
            name: len(ids) for name, ids in sorted(hit_projects_by_domain.items())
        },
        "candidate_projects_with_title_hit_by_domain": {
            name: len(ids) for name, ids in sorted(title_hit_projects_by_domain.items())
        },
        "candidate_projects_with_scope_description_hit_by_domain": {
            name: len(ids) for name, ids in sorted(scope_hit_projects_by_domain.items())
        },
        "candidate_project_exact_text_hit_pct_by_domain": {
            name: round(
                len(hit_projects_by_domain[name]) / len(candidate_projects_by_domain[name]) * 100,
                4,
            )
            for name in sorted(candidate_projects_by_domain)
        },
        "interpretation": {
            "requires_exact_cup_token_in_already_projected_text": True,
            "requires_candidate_cpv_match": True,
            "fuzzy_or_semantic_matching_used": False,
            "production_open_closed_changed": False,
        },
        "boundary": {
            "uses_existing_ted_safe_projection": True,
            "uses_only_notice_title_and_description_proc_for_text_match": True,
            "new_ted_fields_requested": False,
            "beneficiary_fields_requested": False,
            "row_level_artifact_emitted": False,
            "notice_ids_emitted": False,
            "cup_values_emitted": False,
            "production_mapping_changed": False,
            "customer_output_changed": False,
        },
    }

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
