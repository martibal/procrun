#!/usr/bin/env python3
"""Measure Regione Lombardia AZIONE coverage on the exact frozen 4,305-project corpus."""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Final

import httpx

from procrun.a21_identity import a21_projects_by_local_operation_id
from procrun.collectors.opencoesione import to_funding_projects
from procrun.collectors.opencoesione_live import collect_open_coesione_live

FROZEN_PROJECT_COUNT: Final = 4305
FROZEN_SOURCE_SHA256: Final = "35dc073ec9e5e06201080bc949a9da19dfd3366deee3524417491e2b2fd21c6a"
DATASET_ID: Final = "q78n-g3m9"
ENDPOINT: Final = f"https://www.dati.lombardia.it/resource/{DATASET_ID}.json"
SAFE_FIELDS: Final = ("cup", "priorita", "obiettivo_specifico", "azione", "codice_bando")
PAGE_SIZE: Final = 10000
REPORT_PATH = Path("artifacts/lombardia-frozen-action-distribution.json")


def _norm(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    normalized = " ".join(value.split()).strip().upper()
    return normalized or None


def _fetch_rows() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    offset = 0
    allowed = set(SAFE_FIELDS)
    with httpx.Client(timeout=60.0, follow_redirects=True) as client:
        while True:
            response = client.get(
                ENDPOINT,
                params={
                    "$select": ",".join(SAFE_FIELDS),
                    "$where": "cup is not null",
                    "$limit": str(PAGE_SIZE),
                    "$offset": str(offset),
                    "$order": "cup",
                },
                headers={"User-Agent": "ProcRun-frozen-action-diagnostic/2.0"},
            )
            response.raise_for_status()
            payload = response.json()
            if not isinstance(payload, list):
                raise RuntimeError("unexpected Socrata response shape")
            for row in payload:
                if not isinstance(row, dict):
                    raise RuntimeError("non-object Socrata row")
                unexpected = set(row) - allowed
                if unexpected:
                    raise RuntimeError(f"projection escape: {sorted(unexpected)!r}")
                rows.append(row)
            if len(payload) < PAGE_SIZE:
                break
            offset += PAGE_SIZE
    return rows


def main() -> int:
    batch = collect_open_coesione_live()
    if batch.source_sha256 != FROZEN_SOURCE_SHA256:
        raise RuntimeError("frozen OpenCoesione source hash drift")
    projects = a21_projects_by_local_operation_id(batch.operations, to_funding_projects(batch))
    if len(projects) != FROZEN_PROJECT_COUNT:
        raise RuntimeError("frozen project count drift")

    selected_ids = {project.operation_code for project in projects}
    cup_by_project_id: dict[str, str] = {}
    for operation in batch.operations:
        if operation.operation_id not in selected_ids or not operation.cup:
            continue
        cup = _norm(operation.cup)
        if cup is not None:
            cup_by_project_id[operation.operation_id] = cup
    if len(cup_by_project_id) != FROZEN_PROJECT_COUNT:
        raise RuntimeError(
            "expected a CUP on every frozen project: "
            f"projects={FROZEN_PROJECT_COUNT}, mapped={len(cup_by_project_id)}"
        )

    project_ids_by_cup: dict[str, set[str]] = defaultdict(set)
    for project_id, cup in cup_by_project_id.items():
        project_ids_by_cup[cup].add(project_id)
    frozen_cups = set(project_ids_by_cup)

    rows = _fetch_rows()
    actions_by_cup: dict[str, set[str]] = defaultdict(set)
    bandi_by_cup: dict[str, set[str]] = defaultdict(set)
    objectives_by_cup: dict[str, set[str]] = defaultdict(set)
    priorities_by_cup: dict[str, set[str]] = defaultdict(set)
    joined_cups: set[str] = set()

    for row in rows:
        cup = _norm(row.get("cup"))
        if cup is None or cup not in frozen_cups:
            continue
        joined_cups.add(cup)
        action = _norm(row.get("azione"))
        if action:
            actions_by_cup[cup].add(action)
        bando = _norm(row.get("codice_bando"))
        if bando:
            bandi_by_cup[cup].add(bando)
        objective = _norm(row.get("obiettivo_specifico"))
        if objective:
            objectives_by_cup[cup].add(objective)
        priority = _norm(row.get("priorita"))
        if priority:
            priorities_by_cup[cup].add(priority)

    action_project_counts: Counter[str] = Counter()
    bando_project_counts: Counter[str] = Counter()
    action_bando_project_counts: Counter[str] = Counter()
    joined_project_ids: set[str] = set()
    action_project_ids: set[str] = set()
    bando_project_ids: set[str] = set()
    objective_project_ids: set[str] = set()
    priority_project_ids: set[str] = set()
    multiple_action_project_ids: set[str] = set()

    for cup, project_ids in project_ids_by_cup.items():
        if cup in joined_cups:
            joined_project_ids.update(project_ids)
        actions = actions_by_cup.get(cup, set())
        bandi = bandi_by_cup.get(cup, set())
        objectives = objectives_by_cup.get(cup, set())
        priorities = priorities_by_cup.get(cup, set())
        if actions:
            action_project_ids.update(project_ids)
        if bandi:
            bando_project_ids.update(project_ids)
        if objectives:
            objective_project_ids.update(project_ids)
        if priorities:
            priority_project_ids.update(project_ids)
        if len(actions) > 1:
            multiple_action_project_ids.update(project_ids)
        for action in actions:
            action_project_counts[action] += len(project_ids)
        for bando in bandi:
            bando_project_counts[bando] += len(project_ids)
        for action in actions:
            for bando in bandi:
                action_bando_project_counts[f"{action}|{bando}"] += len(project_ids)

    report = {
        "schema_version": "lombardia-frozen-action-distribution-v2",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "frozen_projects": FROZEN_PROJECT_COUNT,
        "distinct_frozen_cups": len(frozen_cups),
        "shared_cup_projects": FROZEN_PROJECT_COUNT - len(frozen_cups),
        "joined_projects": len(joined_project_ids),
        "joined_pct": round(len(joined_project_ids) / FROZEN_PROJECT_COUNT * 100, 4),
        "projects_with_action": len(action_project_ids),
        "projects_with_action_pct": round(len(action_project_ids) / FROZEN_PROJECT_COUNT * 100, 4),
        "projects_with_bando": len(bando_project_ids),
        "projects_with_objective": len(objective_project_ids),
        "projects_with_priority": len(priority_project_ids),
        "projects_with_multiple_actions": len(multiple_action_project_ids),
        "distinct_actions": len(action_project_counts),
        "action_project_counts": dict(
            sorted(action_project_counts.items(), key=lambda item: (-item[1], item[0]))
        ),
        "distinct_bandi": len(bando_project_counts),
        "top_bando_project_counts": dict(bando_project_counts.most_common(100)),
        "top_action_bando_project_counts": dict(action_bando_project_counts.most_common(100)),
    }
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
