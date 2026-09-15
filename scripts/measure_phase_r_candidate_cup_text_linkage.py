#!/usr/bin/env python3
"""Aggregate-only exact CUP text linkage diagnostic for Phase R candidate domains."""

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

REPORT_PATH = Path("artifacts/phase-r-candidate-cup-text-linkage.json")
FROZEN_TED_CUTOFF = date(2026, 9, 12)


def _action(value: object) -> str:
    return str(value or "").strip()


def _contains_exact_cup(text: object, cup: str) -> bool:
    if not isinstance(text, str) or not text:
        return False
    # CUP is treated as one alphanumeric token. No fuzzy, punctuation-stripping,
    # stemming, translation or semantic inference is allowed.
    pattern = rf"(?<![A-Z0-9]){re.escape(cup.upper())}(?![A-Z0-9])"
    return re.search(pattern, text.upper()) is not None


def main() -> int:
    batch = collect_open_coesione_live()
    if batch.source_sha256 != FROZEN_SOURCE_SHA256:
        raise RuntimeError("exact-CUP diagnostic requires exact frozen OpenCoesione source")

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

    notices_with_exact_cup_by_domain: Counter[str] = Counter()
    notices_with_title_cup_by_domain: Counter[str] = Counter()
    notices_with_scope_cup_by_domain: Counter[str] = Counter()
    matched_project_ids: dict[str, set[str]] = {name: set() for name in CANDIDATE_RULES}
    matched_cups: dict[str, set[str]] = {name: set() for name in CANDIDATE_RULES}

    for record in ted.records:
        cpv_codes = tuple(str(code) for code in record.get("cpv_codes", ()))
        title = record.get("title")
        scope = record.get("scope_description")

        for domain in CANDIDATE_RULES:
            if not any(candidate_cpv_match(domain, code) for code in cpv_codes):
                continue

            title_hit = False
            scope_hit = False
            hit_cups: set[str] = set()
            for cup in candidate_projects_by_cup[domain]:
                in_title = _contains_exact_cup(title, cup)
                in_scope = _contains_exact_cup(scope, cup)
                if in_title or in_scope:
                    hit_cups.add(cup)
                    title_hit = title_hit or in_title
                    scope_hit = scope_hit or in_scope

            if not hit_cups:
                continue

            notices_with_exact_cup_by_domain[domain] += 1
            if title_hit:
                notices_with_title_cup_by_domain[domain] += 1
            if scope_hit:
                notices_with_scope_cup_by_domain[domain] += 1
            for cup in hit_cups:
                matched_cups[domain].add(cup)
                matched_project_ids[domain].update(candidate_projects_by_cup[domain][cup])

    report = {
        "schema_version": "phase-r-candidate-cup-text-linkage-v1",
        "ted_cutoff": FROZEN_TED_CUTOFF.isoformat(),
        "ted_complete": ted.complete,
        "ted_notice_count": len(ted.records),
        "ted_pages_fetched": ted.pages_fetched,
        "candidate_projects_by_domain": {
            name: len(ids) for name, ids in sorted(candidate_project_ids.items())
        },
        "candidate_unique_cups_by_domain": {
            name: len(cups) for name, cups in sorted(candidate_projects_by_cup.items())
        },
        "exact_cup_text_notices_by_domain": dict(sorted(notices_with_exact_cup_by_domain.items())),
        "exact_cup_in_title_notices_by_domain": dict(sorted(notices_with_title_cup_by_domain.items())),
        "exact_cup_in_scope_notices_by_domain": dict(sorted(notices_with_scope_cup_by_domain.items())),
        "candidate_unique_cups_with_exact_text_hit_by_domain": {
            name: len(cups) for name, cups in sorted(matched_cups.items())
        },
        "candidate_projects_with_exact_text_hit_by_domain": {
            name: len(ids) for name, ids in sorted(matched_project_ids.items())
        },
        "candidate_project_exact_text_hit_pct_by_domain": {
            name: round(len(matched_project_ids[name]) / len(candidate_project_ids[name]) * 100, 4)
            for name in sorted(candidate_project_ids)
        },
        "interpretation": {
            "requires_candidate_cpv_and_exact_cup_token": True,
            "fuzzy_matching_used": False,
            "semantic_inference_used": False,
            "absence_is_not_evidence_of_no_procurement": True,
            "production_open_closed_changed": False,
        },
        "boundary": {
            "uses_existing_ted_safe_projection": True,
            "uses_existing_socrata_safe_projection": True,
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
