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
                headers={"User-Agent": "ProcRun-frozen-action-diagnostic/1.0"},
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

    frozen_cups = {
        _norm(operation.cup)
        for operation in batch.operations
        if operation.cup and operation.operation_id in {project.operation_code for project in projects}
    }
    frozen_cups.discard(None)
    if len(frozen_cups) != FROZEN_PROJECT_COUNT:
        raise RuntimeError(
            f"expected one CUP per frozen project: projects={FROZEN_PROJECT_COUNT}, cups={len(frozen_cups)}"
        )

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
    action_bando_counts: Counter[str] = Counter()
    for cup in frozen_cups:
        for action in actions_by_cup.get(cup, set()):
            action_project_counts[action] += 1
        for bando in bandi_by_cup.get(cup, set()):
            bando_project_counts[bando] += 1
        for action in actions_by_cup.get(cup, set()):
            for bando in bandi_by_cup.get(cup, set()):
                action_bando_counts[f"{action}|{bando}"] += 1

    ambiguous_action_cups = sum(1 for cup in frozen_cups if len(actions_by_cup.get(cup, set())) > 1)
    report = {
        "schema_version": "lombardia-frozen-action-distribution-v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "frozen_projects": FROZEN_PROJECT_COUNT,
        "frozen_cups": len(frozen_cups),
        "joined_projects": len(joined_cups),
        "joined_pct": round(len(joined_cups) / FROZEN_PROJECT_COUNT * 100, 4),
        "projects_with_action": len(actions_by_cup),
        "projects_with_action_pct": round(len(actions_by_cup) / FROZEN_PROJECT_COUNT * 100, 4),
        "projects_with_bando": len(bandi_by_cup),
        "projects_with_objective": len(objectives_by_cup),
        "projects_with_priority": len(priorities_by_cup),
        "projects_with_multiple_actions": ambiguous_action_cups,
        "distinct_actions": len(action_project_counts),
        "action_project_counts": dict(sorted(action_project_counts.items(), key=lambda x: (-x[1], x[0]))),
        "distinct_bandi": len(bando_project_counts),
        "top_bando_project_counts": dict(bando_project_counts.most_common(100)),
        "top_action_bando_counts": dict(action_bando_counts.most_common(100)),
    }
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
