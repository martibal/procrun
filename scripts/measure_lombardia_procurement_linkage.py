#!/usr/bin/env python3
"""Measure direct CUP linkage from funded projects to Lombardia procurement records.

This diagnostic requests only non-personal structured fields from Regione Lombardia Socrata
procurement datasets. It never requests contracting-officer names, fiscal identifiers,
awardee/participant identity, or procurement free text. The goal is to test whether direct CUP
linkage provides materially more customer-useful procurement facts than text classification alone.
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
OUTCOMES_DATASET_ID: Final = "ktkp-f6ec"
TENDERS_DATASET_ID: Final = "k6cb-4hbm"
SOCRATA_RESOURCE_TEMPLATE: Final = "https://www.dati.lombardia.it/resource/{dataset_id}.json"
SOCRATA_METADATA_TEMPLATE: Final = "https://www.dati.lombardia.it/api/views/{dataset_id}"
OUTCOMES_SAFE_FIELDS: Final = (
    "numero_esito",
    "numero_bando",
    "provincia",
    "comune",
    "tipologia_appalto",
    "stato_bando",
    "settore",
    "codice_cpv",
    "numero_lotti",
    "n_lotto",
    "cup",
)
TENDERS_SAFE_CANDIDATES: Final = (
    "codice_bando",
    "provincia",
    "comune",
    "codice_tipologia_appalto",
    "stato_bando",
    "settore",
    "procedura_gara",
    "importo_complessivo_base",
    "data_pubblicazione",
    "data_presentazioni_offerte",
    "codice_cpv",
    "cup",
    "cig",
)
PAGE_SIZE: Final = 10000
REPORT_PATH = Path("artifacts/lombardia-procurement-linkage.json")


def _normalize_cup(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    normalized = value.strip().upper()
    return normalized or None


def _metadata_fields(client: httpx.Client, dataset_id: str) -> set[str]:
    response = client.get(
        SOCRATA_METADATA_TEMPLATE.format(dataset_id=dataset_id),
        headers={"User-Agent": "ProcRun-structured-linkage-diagnostic/2.0"},
    )
    response.raise_for_status()
    payload = response.json()
    if not isinstance(payload, dict) or not isinstance(payload.get("columns"), list):
        raise RuntimeError(f"unexpected Socrata metadata shape for {dataset_id}")
    result: set[str] = set()
    for column in payload["columns"]:
        if not isinstance(column, dict):
            continue
        field_name = column.get("fieldName")
        if isinstance(field_name, str) and field_name:
            result.add(field_name)
    return result


def _fetch_projection(
    client: httpx.Client,
    *,
    dataset_id: str,
    safe_fields: tuple[str, ...],
) -> list[dict[str, object]]:
    if "cup" not in safe_fields:
        return []
    rows: list[dict[str, object]] = []
    offset = 0
    endpoint = SOCRATA_RESOURCE_TEMPLATE.format(dataset_id=dataset_id)
    select = ",".join(safe_fields)
    allowed = set(safe_fields)
    while True:
        response = client.get(
            endpoint,
            params={
                "$select": select,
                "$where": "cup is not null",
                "$limit": str(PAGE_SIZE),
                "$offset": str(offset),
                "$order": "cup",
            },
            headers={"User-Agent": "ProcRun-structured-linkage-diagnostic/2.0"},
        )
        response.raise_for_status()
        payload = response.json()
        if not isinstance(payload, list):
            raise RuntimeError(f"Socrata projected response is not a JSON list: {dataset_id}")
        for row in payload:
            if not isinstance(row, dict):
                raise RuntimeError(f"Socrata projected response has non-object row: {dataset_id}")
            unexpected = set(row) - allowed
            if unexpected:
                raise RuntimeError(
                    "Socrata response escaped the frozen safe projection: "
                    f"dataset={dataset_id}, unexpected={sorted(unexpected)!r}"
                )
            rows.append(row)
        if len(payload) < PAGE_SIZE:
            break
        offset += PAGE_SIZE
    return rows


def _summarize_rows(rows: list[dict[str, object]]) -> tuple[Counter[str], Counter[str], set[str]]:
    rows_by_cup: Counter[str] = Counter()
    rows_with_cpv_by_cup: Counter[str] = Counter()
    statuses: set[str] = set()
    for row in rows:
        cup = _normalize_cup(row.get("cup"))
        if not cup:
            continue
        rows_by_cup[cup] += 1
        cpv = row.get("codice_cpv")
        if isinstance(cpv, str) and cpv.strip():
            rows_with_cpv_by_cup[cup] += 1
        status = row.get("stato_bando")
        if isinstance(status, str) and status.strip():
            statuses.add(status.strip())
    return rows_by_cup, rows_with_cpv_by_cup, statuses


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

    print("[L2] Inspecting schema metadata and fetching safe CUP projections...", flush=True)
    with httpx.Client(timeout=60.0, follow_redirects=True) as client:
        tender_metadata = _metadata_fields(client, TENDERS_DATASET_ID)
        tender_fields = tuple(
            field for field in TENDERS_SAFE_CANDIDATES if field in tender_metadata
        )
        outcome_rows = _fetch_projection(
            client,
            dataset_id=OUTCOMES_DATASET_ID,
            safe_fields=OUTCOMES_SAFE_FIELDS,
        )
        tender_rows = _fetch_projection(
            client,
            dataset_id=TENDERS_DATASET_ID,
            safe_fields=tender_fields,
        )

    outcome_by_cup, outcome_cpv_by_cup, outcome_statuses = _summarize_rows(outcome_rows)
    tender_by_cup, tender_cpv_by_cup, tender_statuses = _summarize_rows(tender_rows)
    combined_by_cup = outcome_by_cup + tender_by_cup
    combined_cpv_by_cup = outcome_cpv_by_cup + tender_cpv_by_cup

    funded_cups = set(cups_by_local_id.values())
    linked_cups = funded_cups & set(combined_by_cup)
    linked_local_ids = {
        local_id for local_id, cup in cups_by_local_id.items() if cup in linked_cups
    }
    unresolved_linked = unresolved_local_ids & linked_local_ids
    structured_linked = structured_local_ids & linked_local_ids
    linked_with_cpv = {cup for cup in linked_cups if combined_cpv_by_cup[cup] > 0}
    outcome_linked = funded_cups & set(outcome_by_cup)
    tender_linked = funded_cups & set(tender_by_cup)

    report = {
        "schema_version": "lombardia-procurement-linkage-v2",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_resource_sha256": batch.source_sha256,
        "frozen_projects": len(projects),
        "funded_projects_with_cup": len(cups_by_local_id),
        "funded_projects_with_cup_pct": round(len(cups_by_local_id) / len(projects) * 100, 4),
        "baseline_structured_projects": len(structured_local_ids),
        "baseline_unresolved_projects": len(unresolved_local_ids),
        "outcomes": {
            "dataset_id": OUTCOMES_DATASET_ID,
            "safe_projection": list(OUTCOMES_SAFE_FIELDS),
            "projected_rows_with_cup": len(outcome_rows),
            "distinct_cups": len(outcome_by_cup),
            "funded_projects_linked": len(outcome_linked),
            "status_values": sorted(outcome_statuses),
        },
        "active_tenders": {
            "dataset_id": TENDERS_DATASET_ID,
            "metadata_has_cup": "cup" in tender_metadata,
            "safe_projection": list(tender_fields),
            "projected_rows_with_cup": len(tender_rows),
            "distinct_cups": len(tender_by_cup),
            "funded_projects_linked": len(tender_linked),
            "status_values": sorted(tender_statuses),
        },
        "combined": {
            "funded_projects_linked": len(linked_local_ids),
            "funded_projects_linked_pct": round(len(linked_local_ids) / len(projects) * 100, 4),
            "unresolved_projects_linked": len(unresolved_linked),
            "unresolved_linked_pct_of_unresolved": round(
                len(unresolved_linked) / len(unresolved_local_ids) * 100, 4
            ),
            "structured_projects_linked": len(structured_linked),
            "linked_projects_with_cpv": len(linked_with_cpv),
            "linked_projects_with_cpv_pct": round(
                len(linked_with_cpv) / len(linked_cups) * 100, 4
            )
            if linked_cups
            else 0.0,
            "procurement_rows_for_linked_projects": sum(
                combined_by_cup[cup] for cup in linked_cups
            ),
            "max_rows_for_one_linked_project": max(
                (combined_by_cup[cup] for cup in linked_cups), default=0
            ),
        },
    }

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True), flush=True)
    print(f"[L3] Wrote {REPORT_PATH}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
