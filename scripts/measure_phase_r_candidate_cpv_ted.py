#!/usr/bin/env python3
"""Aggregate-only TED validation for Phase R candidate CPV families."""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

from procrun.a21_identity import a21_projects_by_local_operation_id
from procrun.collectors.opencoesione import to_funding_projects
from procrun.collectors.opencoesione_live import collect_open_coesione_live
from procrun.phase_r_candidate_component_design import (
    CANDIDATE_COMPONENT_RULES,
    candidate_cpv_match,
)
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

REPORT_PATH = Path("artifacts/phase-r-candidate-cpv-ted-validation.json")
FROZEN_TED_CUTOFF = date(2026, 9, 12)


def _action(value: object) -> str:
    return str(value or "").strip()


def _normalized_cpv(value: object) -> str:
    return "".join(ch for ch in str(value or "") if ch.isdigit())[:8]


def main() -> int:
    batch = collect_open_coesione_live()
    if batch.source_sha256 != FROZEN_SOURCE_SHA256:
        raise RuntimeError("candidate TED validation requires exact frozen OpenCoesione source")

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

    candidate_project_ids: dict[str, set[str]] = {name: set() for name in CANDIDATE_RULES}
    candidate_cups: dict[str, set[str]] = {name: set() for name in CANDIDATE_RULES}
    candidate_projects_by_cup: dict[str, dict[str, set[str]]] = {
        name: defaultdict(set) for name in CANDIDATE_RULES
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
                candidate_project_ids[name].add(project.operation_code)
                candidate_cups[name].add(cup)
                candidate_projects_by_cup[name][cup].add(project.operation_code)

    for name, rule in CANDIDATE_RULES.items():
        expected = int(rule["expected_projects"])
        actual = len(candidate_project_ids[name])
        if actual != expected:
            raise RuntimeError(
                f"candidate project cohort drift for {name}: expected={expected}, actual={actual}"
            )

    ted = collect_complete_ted_italy(FROZEN_TED_CUTOFF)
    if not ted.complete:
        raise RuntimeError("TED universe is incomplete")

    notice_hits_by_domain: Counter[str] = Counter()
    notice_hits_by_rule: Counter[str] = Counter()
    exact_reference_notices_by_domain: Counter[str] = Counter()
    exact_reference_candidate_cups: dict[str, set[str]] = {
        name: set() for name in CANDIDATE_RULES
    }
    exact_reference_candidate_projects: dict[str, set[str]] = {
        name: set() for name in CANDIDATE_RULES
    }

    for record in ted.records:
        cpv_codes = tuple(_normalized_cpv(code) for code in record.get("cpv_codes", ()))
        cpv_codes = tuple(code for code in cpv_codes if code)
        reference = _normalize_cup(record.get("project_reference"))

        for domain in CANDIDATE_RULES:
            if not any(candidate_cpv_match(domain, code) for code in cpv_codes):
                continue
            notice_hits_by_domain[domain] += 1
            for rule in CANDIDATE_COMPONENT_RULES:
                if rule.candidate_domain != domain:
                    continue
                if any(code.startswith(rule.cpv_prefixes) for code in cpv_codes):
                    notice_hits_by_rule[f"{domain}:{rule.category}"] += 1
            if reference is not None and reference in candidate_cups[domain]:
                exact_reference_notices_by_domain[domain] += 1
                exact_reference_candidate_cups[domain].add(reference)
                exact_reference_candidate_projects[domain].update(
                    candidate_projects_by_cup[domain][reference]
                )

    report = {
        "schema_version": "phase-r-candidate-cpv-ted-validation-v2",
        "ted_cutoff": FROZEN_TED_CUTOFF.isoformat(),
        "ted_complete": ted.complete,
        "ted_stop_reason": ted.stop_reason,
        "ted_notice_count": len(ted.records),
        "ted_pages_fetched": ted.pages_fetched,
        "candidate_project_count_by_domain": {
            name: len(ids) for name, ids in sorted(candidate_project_ids.items())
        },
        "candidate_unique_cup_count_by_domain": {
            name: len(cups) for name, cups in sorted(candidate_cups.items())
        },
        "candidate_duplicate_project_cup_count_by_domain": {
            name: len(candidate_project_ids[name]) - len(candidate_cups[name])
            for name in sorted(candidate_project_ids)
        },
        "ted_notice_hits_by_domain": dict(sorted(notice_hits_by_domain.items())),
        "ted_notice_hits_by_rule": dict(sorted(notice_hits_by_rule.items())),
        "exact_cup_reference_notices_by_domain": dict(
            sorted(exact_reference_notices_by_domain.items())
        ),
        "candidate_unique_cups_with_exact_reference_hit_by_domain": {
            name: len(cups) for name, cups in sorted(exact_reference_candidate_cups.items())
        },
        "candidate_projects_with_exact_cup_reference_hit_by_domain": {
            name: len(ids)
            for name, ids in sorted(exact_reference_candidate_projects.items())
        },
        "candidate_project_exact_reference_hit_pct_by_domain": {
            name: round(
                len(exact_reference_candidate_projects[name])
                / len(candidate_project_ids[name])
                * 100,
                4,
            )
            for name in sorted(candidate_project_ids)
        },
        "interpretation": {
            "universe_cpv_hits_are_not_project_matches": True,
            "exact_cup_reference_hits_are_a_strict_lower_bound": True,
            "shared_cup_can_represent_multiple_frozen_projects": True,
            "production_open_closed_changed": False,
        },
        "boundary": {
            "uses_existing_ted_safe_projection": True,
            "uses_existing_socrata_safe_projection": True,
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
