#!/usr/bin/env python3
"""Measure candidate-domain structural-feature impact without changing production semantics.

The diagnostic joins the frozen 715 candidate projects to bounded candidate-CPV TED result sets
using only non-PII structured fields. It emits aggregate counts only and never persists TED rows,
project CUP values, or notice identifiers.
"""

from __future__ import annotations

import json
from collections import defaultdict
from collections.abc import Mapping, Sequence
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Final

import httpx

from procrun.a21_identity import a21_projects_by_local_operation_id
from procrun.collectors.opencoesione import to_funding_projects
from procrun.collectors.opencoesione_live import collect_open_coesione_live
from procrun.collectors.ted import TED_SOURCE_ID, _post_with_throttle_retry
from procrun.domain import FundingProject
from procrun.source_contracts import require_live_source
from scripts.measure_lombardia_socrata_structured_coverage import (
    FROZEN_PROJECT_COUNT,
    FROZEN_SOURCE_SHA256,
    _classification_signature,
    _fetch_safe_rows,
    _normalize_cup,
    _normalize_intervention_code,
)

START_DATE: Final = date(2021, 1, 1)
CUTOFF_DATE: Final = date(2026, 9, 12)
REPORT_PATH: Final = Path("artifacts/phase-r-candidate-feature-impact.json")
TED_FIELDS: Final = (
    "publication-number",
    "publication-date",
    "classification-cpv",
    "eu-funds-identifier",
    "place-of-performance-subdiv-proc",
)
ALLOWED_TED_NOTICE_FIELDS: Final = frozenset((*TED_FIELDS, "links"))
PAGE_SIZE: Final = 250
MAX_PAGES_PER_DOMAIN: Final = 100

CANDIDATE_SPECS: Final = {
    "digital_transformation": {
        "intervention_code": "013",
        "action": "1.2.3",
        "expected_projects": 573,
        "cpv_query": (
            "classification-cpv = 302* OR classification-cpv = 48* "
            "OR classification-cpv = 72*"
        ),
    },
    "waste_circular_economy": {
        "intervention_code": "067",
        "action": "2.6.2",
        "expected_projects": 142,
        "cpv_query": (
            "classification-cpv = 42914* OR classification-cpv = 452221* "
            "OR classification-cpv = 9051*"
        ),
    },
}


def _ted_date(value: date) -> str:
    return value.strftime("%Y%m%d")


def _string_tuple(value: Any) -> tuple[str, ...]:
    if isinstance(value, str):
        stripped = value.strip()
        return (stripped,) if stripped else ()
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        return tuple(str(item).strip() for item in value if str(item).strip())
    return ()


def _first_scalar(value: Any) -> str | None:
    if isinstance(value, str):
        stripped = value.strip()
        return stripped or None
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        for item in value:
            if isinstance(item, str) and item.strip():
                return item.strip()
    return None


def _nuts_match(project_code: str | None, notice_codes: tuple[str, ...]) -> bool:
    if project_code is None:
        return False
    normalized_project = project_code.strip().casefold()
    if not normalized_project:
        return False
    return any(
        notice.casefold() == normalized_project
        or notice.casefold().startswith(normalized_project)
        or normalized_project.startswith(notice.casefold())
        for notice in notice_codes
        if notice
    )


def _date_compatible(project: FundingProject, publication_date: date) -> bool:
    if project.project_start is None and project.project_end is None:
        return False
    if project.project_start is not None and publication_date < project.project_start:
        return False
    return project.project_end is None or publication_date <= project.project_end


def _candidate_projects() -> dict[str, tuple[tuple[FundingProject, str], ...]]:
    batch = collect_open_coesione_live()
    if batch.source_sha256 != FROZEN_SOURCE_SHA256:
        raise RuntimeError(
            "candidate impact requires exact frozen OpenCoesione source: "
            f"expected={FROZEN_SOURCE_SHA256}, actual={batch.source_sha256}"
        )
    projects = a21_projects_by_local_operation_id(batch.operations, to_funding_projects(batch))
    if len(projects) != FROZEN_PROJECT_COUNT:
        raise RuntimeError(
            f"frozen project count drift: expected={FROZEN_PROJECT_COUNT}, actual={len(projects)}"
        )

    cup_by_operation_id: dict[str, str | None] = {}
    for operation in batch.operations:
        cup = _normalize_cup(operation.cup)
        existing = cup_by_operation_id.get(operation.operation_id)
        if operation.operation_id in cup_by_operation_id and existing != cup:
            raise RuntimeError("conflicting CUP values in frozen OpenCoesione operations")
        cup_by_operation_id[operation.operation_id] = cup

    source_by_cup: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in _fetch_safe_rows():
        cup = _normalize_cup(row.get("cup"))
        if cup is not None:
            source_by_cup[cup].append(row)

    source_consistent_by_cup: dict[str, dict[str, object]] = {}
    for cup, rows in source_by_cup.items():
        signatures = {_classification_signature(row) for row in rows}
        if len(signatures) == 1:
            source_consistent_by_cup[cup] = rows[0]

    result: dict[str, list[tuple[FundingProject, str]]] = {
        key: [] for key in CANDIDATE_SPECS
    }
    for project in projects:
        cup = cup_by_operation_id.get(project.operation_code)
        if cup is None:
            continue
        row = source_consistent_by_cup.get(cup)
        if row is None:
            continue
        intervention_code = _normalize_intervention_code(
            row.get("codice_tipologia_intervento")
        )
        action = str(row.get("azione", "")).strip()
        for key, spec in CANDIDATE_SPECS.items():
            if intervention_code == spec["intervention_code"] and action == spec["action"]:
                result[key].append((project, cup))

    frozen: dict[str, tuple[tuple[FundingProject, str], ...]] = {}
    for key, rows in result.items():
        expected = int(CANDIDATE_SPECS[key]["expected_projects"])
        if len(rows) != expected:
            raise RuntimeError(
                f"candidate cohort drift for {key}: expected={expected}, actual={len(rows)}"
            )
        frozen[key] = tuple(rows)
    return frozen


def _collect_ted_structured_rows(
    http: httpx.Client,
    *,
    cpv_query: str,
) -> tuple[dict[str, object], ...]:
    date_clause = (
        f"buyer-country = ITA AND publication-date >= {_ted_date(START_DATE)} "
        f"AND publication-date <= {_ted_date(CUTOFF_DATE)}"
    )
    query = f"{date_clause} AND ({cpv_query})"
    token: str | None = None
    first_total: int | None = None
    rows: list[dict[str, object]] = []
    seen: set[str] = set()

    for _page in range(1, MAX_PAGES_PER_DOMAIN + 1):
        payload: dict[str, object] = {
            "query": query,
            "fields": list(TED_FIELDS),
            "limit": PAGE_SIZE,
            "scope": "ALL",
            "checkQuerySyntax": False,
            "paginationMode": "ITERATION",
        }
        if token is not None:
            payload["iterationNextToken"] = token
        response = _post_with_throttle_retry(http, payload)
        body = response.json()
        if not isinstance(body, dict) or body.get("timedOut") is not False:
            raise RuntimeError("TED candidate-feature query returned invalid/timed-out envelope")
        total = body.get("totalNoticeCount")
        if first_total is None:
            if not isinstance(total, int) or isinstance(total, bool) or total < 0:
                raise RuntimeError("TED candidate-feature totalNoticeCount is invalid")
            first_total = total
        notices = body.get("notices")
        if not isinstance(notices, list):
            raise RuntimeError("TED candidate-feature notices is not a list")
        if not notices:
            break

        for notice in notices:
            if not isinstance(notice, Mapping):
                raise RuntimeError("TED candidate-feature notice is not an object")
            unexpected = set(notice) - ALLOWED_TED_NOTICE_FIELDS
            if unexpected:
                raise RuntimeError(
                    f"TED candidate-feature returned non-admitted fields: {sorted(unexpected)}"
                )
            notice_id = _first_scalar(notice.get("publication-number"))
            publication_date_text = _first_scalar(notice.get("publication-date"))
            if notice_id is None or publication_date_text is None:
                raise RuntimeError("TED candidate-feature notice lacks identity/date")
            identity = f"{notice_id}|{publication_date_text}"
            if identity in seen:
                continue
            seen.add(identity)
            rows.append(
                {
                    "publication_date": date.fromisoformat(publication_date_text[:10]),
                    "cpv_codes": _string_tuple(notice.get("classification-cpv")),
                    "project_references": _string_tuple(notice.get("eu-funds-identifier")),
                    "nuts_codes": _string_tuple(
                        notice.get("place-of-performance-subdiv-proc")
                    ),
                }
            )

        next_token = body.get("iterationNextToken")
        if not isinstance(next_token, str) or not next_token:
            break
        token = next_token
    else:
        raise RuntimeError("TED candidate-feature query exceeded bounded page limit")

    if first_total is None or len(rows) != first_total:
        raise RuntimeError(
            "TED candidate-feature complete-count invariant failed: "
            f"received={len(rows)}, expected={first_total}"
        )
    return tuple(rows)


def _measure_domain(
    projects: tuple[tuple[FundingProject, str], ...],
    notices: tuple[dict[str, object], ...],
) -> dict[str, int | float]:
    projects_with_exact_reference = 0
    projects_with_geography_cpv = 0
    projects_with_structural_candidate = 0
    projects_with_compatible_structural_candidate = 0
    exact_reference_notice_matches = 0

    for project, cup in projects:
        normalized_cup = cup.casefold()
        exact = False
        geography = False
        structural = False
        compatible_structural = False
        for notice in notices:
            references = tuple(
                str(value).strip().casefold()
                for value in notice["project_references"]
                if str(value).strip()
            )
            exact_here = normalized_cup in references
            geography_here = _nuts_match(
                project.nuts_code,
                tuple(str(value) for value in notice["nuts_codes"]),
            )
            if exact_here:
                exact = True
                exact_reference_notice_matches += 1
            if geography_here:
                geography = True
            if exact_here or geography_here:
                structural = True
                publication_date = notice["publication_date"]
                if isinstance(publication_date, date) and _date_compatible(
                    project, publication_date
                ):
                    compatible_structural = True
        projects_with_exact_reference += int(exact)
        projects_with_geography_cpv += int(geography)
        projects_with_structural_candidate += int(structural)
        projects_with_compatible_structural_candidate += int(compatible_structural)

    total = len(projects)
    return {
        "projects": total,
        "ted_notices_in_candidate_cpv_universe": len(notices),
        "projects_with_exact_reference": projects_with_exact_reference,
        "projects_with_exact_reference_pct": round(
            projects_with_exact_reference / total * 100, 4
        ),
        "exact_reference_notice_matches": exact_reference_notice_matches,
        "projects_with_geography_cpv": projects_with_geography_cpv,
        "projects_with_geography_cpv_pct": round(
            projects_with_geography_cpv / total * 100, 4
        ),
        "projects_with_any_structural_candidate": projects_with_structural_candidate,
        "projects_with_any_structural_candidate_pct": round(
            projects_with_structural_candidate / total * 100, 4
        ),
        "projects_with_date_compatible_structural_candidate": (
            projects_with_compatible_structural_candidate
        ),
        "projects_with_date_compatible_structural_candidate_pct": round(
            projects_with_compatible_structural_candidate / total * 100, 4
        ),
    }


def main() -> int:
    contract = require_live_source(TED_SOURCE_ID)
    if not contract.server_side_projection:
        raise RuntimeError("TED source contract no longer guarantees server-side projection")

    cohorts = _candidate_projects()
    measurements: dict[str, dict[str, int | float]] = {}
    with httpx.Client(
        timeout=30.0,
        headers={"Accept": "application/json", "User-Agent": "ProcRun/phase-r-feature-impact-v1"},
    ) as http:
        for key, projects in cohorts.items():
            notices = _collect_ted_structured_rows(
                http,
                cpv_query=str(CANDIDATE_SPECS[key]["cpv_query"]),
            )
            measurements[key] = _measure_domain(projects, notices)

    report = {
        "schema_version": "phase-r-candidate-feature-impact-v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "frozen_project_count": FROZEN_PROJECT_COUNT,
        "frozen_source_sha256": FROZEN_SOURCE_SHA256,
        "window": {
            "buyer_country": "ITA",
            "start_date": START_DATE.isoformat(),
            "cutoff_date": CUTOFF_DATE.isoformat(),
        },
        "measurements": measurements,
        "boundary": {
            "requested_ted_fields": list(TED_FIELDS),
            "title_requested": False,
            "description_requested": False,
            "buyer_requested": False,
            "contact_requested": False,
            "ted_rows_persisted": False,
            "cup_values_persisted": False,
            "notice_ids_persisted": False,
            "row_level_artifact_emitted": False,
            "production_mapping_changed": False,
            "production_taxonomy_changed": False,
            "open_closed_semantics_changed": False,
        },
    }
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
