#!/usr/bin/env python3
"""Measure two preregistered Phase R candidate domains without changing production taxonomy."""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path

from procrun.a21_identity import a21_projects_by_local_operation_id
from procrun.collectors.opencoesione import to_funding_projects
from procrun.collectors.opencoesione_live import collect_open_coesione_live
from procrun.component_engine import structured_component_suggestions
from procrun.eu_objective_mapping import INTERVENTION_FIELD_MAP
from procrun.production_delivery import ALL_COMPONENT_DOMAINS
from scripts.measure_lombardia_socrata_structured_coverage import (
    FROZEN_PROJECT_COUNT,
    FROZEN_SOURCE_SHA256,
    FROZEN_STRUCTURED_SIGNAL_PROJECTS,
    _classification_signature,
    _fetch_safe_rows,
    _normalize_cup,
    _normalize_intervention_code,
)

REPORT_PATH = Path("artifacts/phase-r-candidate-domain-design.json")

CANDIDATE_RULES = {
    "digital_transformation": {
        "intervention_code": "013",
        "azione": "1.2.3",
        "expected_projects": 573,
    },
    "waste_circular_economy": {
        "intervention_code": "067",
        "azione": "2.6.2",
        "expected_projects": 142,
    },
}


def _action(value: object) -> str:
    return str(value or "").strip()


def main() -> int:
    batch = collect_open_coesione_live()
    if batch.source_sha256 != FROZEN_SOURCE_SHA256:
        raise RuntimeError("candidate-domain diagnostic requires exact frozen OpenCoesione source")

    projects = a21_projects_by_local_operation_id(batch.operations, to_funding_projects(batch))
    if len(projects) != FROZEN_PROJECT_COUNT:
        raise RuntimeError("frozen Phase R project count drift")

    current_structured_ids = {
        project.operation_code
        for project in projects
        if structured_component_suggestions(project, list(ALL_COMPONENT_DOMAINS))
    }
    if len(current_structured_ids) != FROZEN_STRUCTURED_SIGNAL_PROJECTS:
        raise RuntimeError("current structured-signal baseline drift")

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

    existing_mapped_ids = set(current_structured_ids)
    candidate_ids: dict[str, set[str]] = {name: set() for name in CANDIDATE_RULES}
    candidate_actions: dict[str, Counter[str]] = {
        name: Counter() for name in CANDIDATE_RULES
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

        if code in INTERVENTION_FIELD_MAP:
            existing_mapped_ids.add(project.operation_code)

        for name, rule in CANDIDATE_RULES.items():
            if code == rule["intervention_code"] and action == rule["azione"]:
                candidate_ids[name].add(project.operation_code)
                candidate_actions[name][action] += 1

    for name, rule in CANDIDATE_RULES.items():
        actual = len(candidate_ids[name])
        expected = int(rule["expected_projects"])
        if actual != expected:
            raise RuntimeError(
                f"candidate cohort drift for {name}: expected={expected}, actual={actual}"
            )

    candidate_union = set().union(*candidate_ids.values())
    candidate_overlap_existing = candidate_union.intersection(existing_mapped_ids)
    combined = existing_mapped_ids.union(candidate_union)

    report = {
        "schema_version": "phase-r-candidate-domain-design-v1",
        "frozen_project_count": FROZEN_PROJECT_COUNT,
        "production_taxonomy_changed": False,
        "customer_output_changed": False,
        "candidate_rules": CANDIDATE_RULES,
        "existing_safe_mapped_projects": len(existing_mapped_ids),
        "existing_safe_mapped_pct": round(
            len(existing_mapped_ids) / FROZEN_PROJECT_COUNT * 100, 4
        ),
        "candidate_projects_by_domain": {
            name: len(ids) for name, ids in sorted(candidate_ids.items())
        },
        "candidate_action_distribution": {
            name: dict(sorted(counter.items()))
            for name, counter in sorted(candidate_actions.items())
        },
        "candidate_union_projects": len(candidate_union),
        "candidate_overlap_existing_projects": len(candidate_overlap_existing),
        "candidate_incremental_projects": len(candidate_union - existing_mapped_ids),
        "combined_candidate_ceiling_projects": len(combined),
        "combined_candidate_ceiling_pct": round(len(combined) / FROZEN_PROJECT_COUNT * 100, 4),
        "phase_r_target_pct": 40.0,
        "phase_r_target_met": len(combined) / FROZEN_PROJECT_COUNT >= 0.40,
        "boundary": {
            "uses_existing_safe_socrata_projection": True,
            "beneficiary_fields_requested": False,
            "project_narrative_requested": False,
            "row_level_artifact_emitted": False,
            "component_domain_enum_changed": False,
            "production_mapping_changed": False,
        },
    }

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
