#!/usr/bin/env python3
"""Measure safe Lombardia Socrata structured coverage on the frozen Phase R corpus.

This diagnostic receives only the eight-field Stage 2 Socrata projection, joins by exact CUP in
memory, and emits aggregate counts only. It does not change production classification semantics.
"""

from __future__ import annotations

import json
import urllib.parse
import urllib.request
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

from procrun.a21_identity import a21_projects_by_local_operation_id
from procrun.collectors.opencoesione import to_funding_projects
from procrun.collectors.opencoesione_live import collect_open_coesione_live
from procrun.component_engine import structured_component_suggestions
from procrun.eu_objective_mapping import INTERVENTION_FIELD_MAP
from procrun.production_delivery import ALL_COMPONENT_DOMAINS

DATASET_ID = "q78n-g3m9"
RESOURCE_URL = f"https://www.dati.lombardia.it/resource/{DATASET_ID}.json"
SAFE_FIELDS = (
    "cup",
    "priorita",
    "obiettivo_specifico",
    "azione",
    "codice_bando",
    "codice_operazione",
    "codice_tipologia_intervento",
    "descrizione_tipologia",
)
SAFE_FIELD_SET = set(SAFE_FIELDS)
FROZEN_PROJECT_COUNT = 4305
FROZEN_SOURCE_SHA256 = "35dc073ec9e5e06201080bc949a9da19dfd3366deee3524417491e2b2fd21c6a"
FROZEN_STRUCTURED_SIGNAL_PROJECTS = 133
MAX_SOURCE_ROWS = 50_000
REPORT_PATH = Path("artifacts/lombardia-socrata-structured-coverage.json")
HEADERS = {
    "User-Agent": "ProcRun/phase-r-lombardia-socrata-coverage-v1",
    "Accept": "application/json",
}


def _normalize_cup(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    normalized = value.strip().upper()
    return normalized or None


def _normalize_intervention_code(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    stripped = value.strip()
    if not stripped or not stripped.isdigit() or len(stripped) > 3:
        return None
    return stripped.zfill(3)


def _classification_signature(row: dict[str, object]) -> tuple[str, ...]:
    fields = (
        "priorita",
        "obiettivo_specifico",
        "azione",
        "codice_tipologia_intervento",
        "descrizione_tipologia",
    )
    return tuple(str(row.get(field, "")).strip() for field in fields)


def _fetch_safe_rows() -> list[dict[str, object]]:
    params = {
        "$select": ",".join(SAFE_FIELDS),
        "$limit": str(MAX_SOURCE_ROWS),
    }
    url = RESOURCE_URL + "?" + urllib.parse.urlencode(params)
    request = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(request, timeout=60) as response:
        if response.status != 200:
            raise RuntimeError(f"unexpected Socrata HTTP status: {response.status}")
        payload = json.load(response)

    if not isinstance(payload, list):
        raise RuntimeError("unexpected non-list Socrata coverage response")
    if len(payload) >= MAX_SOURCE_ROWS:
        raise RuntimeError("Socrata safe projection may be truncated at configured row bound")

    rows: list[dict[str, object]] = []
    for item in payload:
        if not isinstance(item, dict):
            raise RuntimeError("unexpected non-object Socrata row")
        unexpected = set(item) - SAFE_FIELD_SET
        if unexpected:
            raise RuntimeError(f"unexpected fields received from Socrata: {sorted(unexpected)}")
        rows.append(item)
    return rows


def main() -> int:
    batch = collect_open_coesione_live()
    if batch.source_sha256 != FROZEN_SOURCE_SHA256:
        raise RuntimeError(
            "Lombardia coverage measurement requires exact frozen OpenCoesione source: "
            f"expected={FROZEN_SOURCE_SHA256}, actual={batch.source_sha256}"
        )

    projects = a21_projects_by_local_operation_id(batch.operations, to_funding_projects(batch))
    if len(projects) != FROZEN_PROJECT_COUNT:
        raise RuntimeError(
            f"frozen project count drift: expected={FROZEN_PROJECT_COUNT}, actual={len(projects)}"
        )

    current_structured_ids = {
        project.operation_code
        for project in projects
        if structured_component_suggestions(project, list(ALL_COMPONENT_DOMAINS))
    }
    if len(current_structured_ids) != FROZEN_STRUCTURED_SIGNAL_PROJECTS:
        raise RuntimeError(
            "current structured baseline drift: "
            f"expected={FROZEN_STRUCTURED_SIGNAL_PROJECTS}, actual={len(current_structured_ids)}"
        )

    cup_by_operation_id: dict[str, str | None] = {}
    for operation in batch.operations:
        normalized_cup = _normalize_cup(operation.cup)
        existing = cup_by_operation_id.get(operation.operation_id)
        if operation.operation_id in cup_by_operation_id and existing != normalized_cup:
            raise RuntimeError(
                "conflicting CUP values for frozen OpenCoesione operation: "
                f"{operation.operation_id}"
            )
        cup_by_operation_id[operation.operation_id] = normalized_cup

    source_rows = _fetch_safe_rows()
    source_by_cup: dict[str, list[dict[str, object]]] = defaultdict(list)
    rows_without_cup = 0
    for row in source_rows:
        cup = _normalize_cup(row.get("cup"))
        if cup is None:
            rows_without_cup += 1
            continue
        source_by_cup[cup].append(row)

    source_conflicting_cups: set[str] = set()
    source_consistent_by_cup: dict[str, dict[str, object]] = {}
    duplicate_consistent_cups = 0
    for cup, rows in source_by_cup.items():
        signatures = {_classification_signature(row) for row in rows}
        if len(signatures) != 1:
            source_conflicting_cups.add(cup)
            continue
        if len(rows) > 1:
            duplicate_consistent_cups += 1
        source_consistent_by_cup[cup] = rows[0]

    frozen_projects_with_cup = 0
    overlap_projects = 0
    safe_classified_overlap_projects = 0
    incremental_projects = 0
    already_structured_overlap_projects = 0
    ambiguous_overlap_projects = 0
    missing_intervention_code_projects = 0
    existing_map_projects = 0
    existing_map_incremental_projects = 0
    existing_map_by_domain: Counter[str] = Counter()
    existing_map_by_code: Counter[str] = Counter()
    intervention_codes: Counter[str] = Counter()
    intervention_descriptions: Counter[str] = Counter()
    objectives: Counter[str] = Counter()
    actions: Counter[str] = Counter()

    for project in projects:
        cup = cup_by_operation_id.get(project.operation_code)
        if cup is None:
            continue
        frozen_projects_with_cup += 1
        if cup in source_conflicting_cups:
            ambiguous_overlap_projects += 1
            continue
        source_row = source_consistent_by_cup.get(cup)
        if source_row is None:
            continue

        overlap_projects += 1
        raw_intervention_code = source_row.get("codice_tipologia_intervento")
        intervention_code = _normalize_intervention_code(raw_intervention_code)
        if intervention_code is None:
            missing_intervention_code_projects += 1
            continue

        safe_classified_overlap_projects += 1
        intervention_codes[intervention_code] += 1
        description = str(source_row.get("descrizione_tipologia", "")).strip()
        if description:
            intervention_descriptions[description] += 1
        objective = str(source_row.get("obiettivo_specifico", "")).strip()
        if objective:
            objectives[objective] += 1
        action = str(source_row.get("azione", "")).strip()
        if action:
            actions[action] += 1

        existing_mapping = INTERVENTION_FIELD_MAP.get(intervention_code)
        if existing_mapping is not None:
            existing_map_projects += 1
            existing_map_by_code[intervention_code] += 1
            existing_map_by_domain[existing_mapping.domain] += 1
            if project.operation_code not in current_structured_ids:
                existing_map_incremental_projects += 1

        if project.operation_code in current_structured_ids:
            already_structured_overlap_projects += 1
        else:
            incremental_projects += 1

    combined_ceiling = FROZEN_STRUCTURED_SIGNAL_PROJECTS + incremental_projects
    existing_map_combined = FROZEN_STRUCTURED_SIGNAL_PROJECTS + existing_map_incremental_projects
    report = {
        "schema_version": "lombardia-socrata-structured-coverage-v2",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "frozen_source_sha256": batch.source_sha256,
        "frozen_project_count": FROZEN_PROJECT_COUNT,
        "current_structured_signal_projects": FROZEN_STRUCTURED_SIGNAL_PROJECTS,
        "current_structured_signal_pct": round(
            FROZEN_STRUCTURED_SIGNAL_PROJECTS / FROZEN_PROJECT_COUNT * 100, 4
        ),
        "socrata_dataset_id": DATASET_ID,
        "socrata_projection_fields": list(SAFE_FIELDS),
        "socrata_rows_received": len(source_rows),
        "socrata_rows_without_cup": rows_without_cup,
        "socrata_unique_cups": len(source_by_cup),
        "socrata_conflicting_cups": len(source_conflicting_cups),
        "socrata_duplicate_consistent_cups": duplicate_consistent_cups,
        "frozen_projects_with_cup": frozen_projects_with_cup,
        "overlap_projects": overlap_projects,
        "overlap_pct": round(overlap_projects / FROZEN_PROJECT_COUNT * 100, 4),
        "ambiguous_overlap_projects": ambiguous_overlap_projects,
        "missing_intervention_code_projects": missing_intervention_code_projects,
        "safe_classified_overlap_projects": safe_classified_overlap_projects,
        "already_structured_overlap_projects": already_structured_overlap_projects,
        "incremental_structured_projects": incremental_projects,
        "incremental_structured_pct_points": round(
            incremental_projects / FROZEN_PROJECT_COUNT * 100, 4
        ),
        "combined_structured_ceiling_projects": combined_ceiling,
        "combined_structured_ceiling_pct": round(combined_ceiling / FROZEN_PROJECT_COUNT * 100, 4),
        "existing_frozen_intervention_map": {
            "mapped_overlap_projects": existing_map_projects,
            "incremental_projects": existing_map_incremental_projects,
            "combined_projects": existing_map_combined,
            "combined_pct": round(existing_map_combined / FROZEN_PROJECT_COUNT * 100, 4),
            "projects_by_code": dict(sorted(existing_map_by_code.items())),
            "projects_by_domain": dict(sorted(existing_map_by_domain.items())),
        },
        "intervention_code_distribution": dict(sorted(intervention_codes.items())),
        "intervention_description_distribution": dict(intervention_descriptions.most_common()),
        "specific_objective_distribution": dict(sorted(objectives.items())),
        "action_distribution": dict(sorted(actions.items())),
        "boundary": {
            "server_side_select_used": True,
            "select_star_used": False,
            "beneficiary_fields_requested": False,
            "project_narrative_requested": False,
            "row_level_artifact_emitted": False,
            "join_key": "exact_normalized_cup",
            "production_mapping_changed": False,
        },
    }

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
