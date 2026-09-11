#!/usr/bin/env python3
"""Measure direct CUP linkage from funded projects to Lombardia procurement outcomes.

This diagnostic deliberately requests only non-personal structured fields from the Regione Lombardia
Socrata dataset. It does not request contracting-officer names, fiscal identifiers, awardee identity,
or procurement free text. The goal is to test whether direct CUP linkage can provide materially more
customer-useful procurement facts than text classification alone.
"""

from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Final

import httpx

from procrun.a21_identity import a21_projects_by_local_operation_id
from procrun.collectors.opencoesione import to_funding_projects
from procrun.collectors.opencoesione_live import collect_open_coesione_live
from procrun.component_engine import structured_component_suggestions
from procrun.production_delivery import ALL_COMPONENT_DOMAINS

FROZEN_PROJECT_COUNT: Final = 4305
FROZEN_SOURCE_SHA256: Final = "35dc073ec9e5e06201080bc949a9da19dfd3366deee3524417491e2b2fd21c6a"
FROZEN_STRUCTURED_SIGNAL_PROJECTS: Final = 133
SOCRATA_DATASET_ID: Final = "ktkp-f6ec"
SOCRATA_ENDPOINT: Final = f"https://www.dati.lombardia.it/resource/{SOCRATA_DATASET_ID}.json"
SAFE_SELECT: Final = (
    "numero_esito,numero_bando,provincia,comune,tipologia_appalto,stato_bando,"
    "settore,codice_cpv,numero_lotti,n_lotto,cup"
)
PAGE_SIZE: Final = 10000
REPORT_PATH = Path("artifacts/lombardia-procurement-linkage.json")


def _normalize_cup(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    normalized = value.strip().upper()
    return normalized or None


def _fetch_projected_outcomes() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    offset = 0
    with httpx.Client(timeout=60.0, follow_redirects=True) as client:
        while True:
            response = client.get(
                SOCRATA_ENDPOINT,
                params={
                    "$select": SAFE_SELECT,
                    "$where": "cup is not null",
                    "$limit": str(PAGE_SIZE),
                    "$offset": str(offset),
                    "$order": "cup,numero_esito,numero_bando",
                },
                headers={"User-Agent": "ProcRun-structured-linkage-diagnostic/1.0"},
            )
            response.raise_for_status()
            payload = response.json()
            if not isinstance(payload, list):
                raise RuntimeError("Socrata projected response is not a JSON list")
            for row in payload:
                if not isinstance(row, dict):
                    raise RuntimeError("Socrata projected response contains a non-object row")
                unexpected = set(row) - set(SAFE_SELECT.split(","))
                if unexpected:
                    raise RuntimeError(
                        "Socrata response escaped the frozen safe projection: "
                        f"unexpected={sorted(unexpected)!r}"
                    )
                rows.append(row)
            if len(payload) < PAGE_SIZE:
                break
            offset += PAGE_SIZE
    return rows


def main() -> int:
    print("[L1] Reproducing frozen OpenCoesione project universe...", flush=True)
    batch = collect_open_coesione_live()
    if batch.source_sha256 != FROZEN_SOURCE_SHA256:
        raise RuntimeError(
            "linkage diagnostic requires the exact frozen Phase R source: "
            f"expected={FROZEN_SOURCE_SHA256}, actual={batch.source_sha256}"
        )

    projects = a21_projects_by_local_operation_id(batch.operations, to_funding_projects(batch))
    if len(projects) != FROZEN_PROJECT_COUNT:
        raise RuntimeError(
            f"frozen project count drift: expected={FROZEN_PROJECT_COUNT}, actual={len(projects)}"
        )

    selected_local_ids = {project.operation_code for project in projects}
    cups_by_local_id: dict[str, str] = {}
    for operation in batch.operations:
        if operation.operation_id not in selected_local_ids or not operation.cup:
            continue
        cup = _normalize_cup(operation.cup)
        if cup:
            cups_by_local_id[operation.operation_id] = cup

    structured_local_ids = {
        project.operation_code
        for project in projects
        if structured_component_suggestions(project, list(ALL_COMPONENT_DOMAINS))
    }
    if len(structured_local_ids) != FROZEN_STRUCTURED_SIGNAL_PROJECTS:
        raise RuntimeError(
            "current structured-signal baseline drift: "
            f"expected={FROZEN_STRUCTURED_SIGNAL_PROJECTS}, actual={len(structured_local_ids)}"
        )
    unresolved_local_ids = selected_local_ids - structured_local_ids

    print("[L2] Fetching CUP-bounded structured procurement projection...", flush=True)
    outcomes = _fetch_projected_outcomes()
    rows_by_cup: Counter[str] = Counter()
    rows_with_cpv_by_cup: Counter[str] = Counter()
    status_by_cup: dict[str, set[str]] = {}
    for row in outcomes:
        cup = _normalize_cup(row.get("cup"))
        if not cup:
            continue
        rows_by_cup[cup] += 1
        if isinstance(row.get("codice_cpv"), str) and row["codice_cpv"].strip():
            rows_with_cpv_by_cup[cup] += 1
        status = row.get("stato_bando")
        if isinstance(status, str) and status.strip():
            status_by_cup.setdefault(cup, set()).add(status.strip())

    funded_cups = set(cups_by_local_id.values())
    linked_cups = funded_cups & set(rows_by_cup)
    linked_local_ids = {
        local_id for local_id, cup in cups_by_local_id.items() if cup in linked_cups
    }
    unresolved_linked = unresolved_local_ids & linked_local_ids
    structured_linked = structured_local_ids & linked_local_ids
    linked_with_cpv = {cup for cup in linked_cups if rows_with_cpv_by_cup[cup] > 0}

    report = {
        "schema_version": "lombardia-procurement-linkage-v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_resource_sha256": batch.source_sha256,
        "socrata_dataset_id": SOCRATA_DATASET_ID,
        "safe_projection": SAFE_SELECT.split(","),
        "frozen_projects": len(projects),
        "funded_projects_with_cup": len(cups_by_local_id),
        "funded_projects_with_cup_pct": round(len(cups_by_local_id) / len(projects) * 100, 4),
        "baseline_structured_projects": len(structured_local_ids),
        "baseline_unresolved_projects": len(unresolved_local_ids),
        "projected_procurement_rows_with_cup": len(outcomes),
        "distinct_procurement_cups": len(rows_by_cup),
        "funded_projects_linked_to_procurement": len(linked_local_ids),
        "funded_projects_linked_pct": round(len(linked_local_ids) / len(projects) * 100, 4),
        "unresolved_projects_linked_to_procurement": len(unresolved_linked),
        "unresolved_projects_linked_pct_of_unresolved": round(
            len(unresolved_linked) / len(unresolved_local_ids) * 100, 4
        ),
        "structured_projects_linked_to_procurement": len(structured_linked),
        "linked_projects_with_cpv": len(linked_with_cpv),
        "linked_projects_with_cpv_pct": round(
            len(linked_with_cpv) / len(linked_cups) * 100, 4
        )
        if linked_cups
        else 0.0,
        "procurement_rows_for_linked_projects": sum(rows_by_cup[cup] for cup in linked_cups),
        "max_procurement_rows_for_one_linked_project": max(
            (rows_by_cup[cup] for cup in linked_cups), default=0
        ),
        "distinct_status_values_on_linked_projects": sorted(
            {status for cup in linked_cups for status in status_by_cup.get(cup, set())}
        ),
    }

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True), flush=True)
    print(f"[L3] Wrote {REPORT_PATH}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
