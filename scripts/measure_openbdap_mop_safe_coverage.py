#!/usr/bin/env python3
"""Measure safe OpenBDAP MOP national counts, lifecycle runway and Lombardia overlap.

The diagnostic uses only server-side projected OData requests. National scale and
lifecycle cohorts are counted by probing existence at $skip offsets with $top=1 and
CUP-only projection; this needs O(log n) requests and never receives unrestricted
rows. Lifecycle fields are referenced only inside server-side filters, so their row
values are not returned or persisted by the count probes. The Lombardia overlap
requests only CUP, project status, intervention sector and effective works cost for CUPs already in the frozen corpus. Raw MOP rows are never persisted.
"""
from __future__ import annotations

import json
import time
from collections import Counter
from collections.abc import Iterable
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Final
from urllib.parse import urlparse

import httpx

from procrun.a21_identity import a21_projects_by_local_operation_id
from procrun.collectors.opencoesione import to_funding_projects
from procrun.collectors.opencoesione_live import collect_open_coesione_live
from procrun.component_engine import structured_component_suggestions
from procrun.production_delivery import ALL_COMPONENT_DOMAINS

FROZEN_PROJECT_COUNT: Final = 4305
FROZEN_SOURCE_SHA256: Final = "35dc073ec9e5e06201080bc949a9da19dfd3366deee3524417491e2b2fd21c6a"
FROZEN_STRUCTURED_PROJECTS: Final = 133
RESOURCE_ID: Final = "bda1676b-62ab-44b7-8f9a-ca93b8534488@rgs"
BASE_URL: Final = (
    "https://bdap-opendata.rgs.mef.gov.it/"
    f"ODataProxy/MdData('{RESOURCE_ID}')/DataRows"
)
ALLOWED_HOST: Final = "bdap-opendata.rgs.mef.gov.it"
CUP: Final = "Cccodice_cup_1267962549"
STATUS_CODE: Final = "Cccodice_stato_1426672593"
STATUS_DESC: Final = "Ccdescrizione_s1176782119"
SECTOR: Final = "Ccsettore_inter1475973826"
COST_EFFECTIVE: Final = "Cccosto_lavori_e582037416"
PLANNED_EXECUTION_START: Final = "Ccinizio_esecuz2103627579"
ACTUAL_EXECUTION_START: Final = "Ccinizio_esecuzi167207395"
SAFE_FIELDS: Final = (CUP, STATUS_CODE, STATUS_DESC, SECTOR, COST_EFFECTIVE)
ALLOWED_RETURNED_KEYS: Final = set(SAFE_FIELDS) | {"row_id"}
COUNT_ALLOWED_RETURNED_KEYS: Final = {CUP, "row_id"}
BATCH_SIZE: Final = 60
MAX_ROWS_PER_BATCH: Final = 300
MAX_RESPONSE_BYTES: Final = 2_000_000
MAX_ATTEMPTS: Final = 3
MAX_COUNT_PROBE_OFFSET: Final = 2_000_000
REPORT_PATH = Path("artifacts/openbdap-mop-safe-coverage.json")

# The current official MOP release was published 2026-09-04 and describes data
# observed at 2026-08-31. These bounds are deliberately frozen for this diagnostic
# so a later source refresh cannot silently move the commercial measurement window.
LIFECYCLE_OBSERVED_DATE: Final = "2026-08-31"
LIFECYCLE_12M_END: Final = "2027-08-31"
LIFECYCLE_24M_END: Final = "2028-08-31"
VALID_DATE_FLOOR: Final = "2000-01-01"
VALID_DATE_CEILING: Final = "2100-12-31"
SENTINEL_DATE: Final = "9999-12-31"


def _extract_rows(payload: Any) -> list[dict[str, Any]]:
    if not isinstance(payload, dict):
        raise RuntimeError("OpenBDAP OData JSON root is not an object")
    data = payload.get("d")
    if not isinstance(data, dict) or not isinstance(data.get("results"), list):
        raise RuntimeError("OpenBDAP OData response has no d.results list")
    rows = data["results"]
    if not all(isinstance(row, dict) for row in rows):
        raise RuntimeError("OpenBDAP OData returned a non-object row")
    return rows


def _data_keys(row: dict[str, Any]) -> set[str]:
    return {key for key in row if key not in {"__metadata", "@odata.id", "@odata.etag"}}


def _norm(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    text = " ".join(value.split()).strip().upper()
    return text or None


def _amount(value: object) -> Decimal | None:
    if value is None:
        return None
    text = str(value).strip().replace(" ", "")
    if not text:
        return None
    if "," in text and "." in text:
        text = text.replace(".", "").replace(",", ".")
    elif "," in text:
        text = text.replace(",", ".")
    try:
        return Decimal(text)
    except InvalidOperation:
        return None


def _batches(values: list[str], size: int) -> Iterable[list[str]]:
    for start in range(0, len(values), size):
        yield values[start : start + size]


def _row_exists_at_skip(
    client: httpx.Client,
    skip: int,
    filter_expr: str | None = None,
) -> bool:
    """Probe one CUP-only row at an offset and persist no returned value."""
    params = {
        "$select": CUP,
        "$skip": str(skip),
        "$top": "1",
        "$format": "json",
    }
    if filter_expr:
        params["$filter"] = filter_expr
    response = client.get(BASE_URL, params=params)
    if response.is_redirect:
        raise RuntimeError("OpenBDAP national count request redirected")
    response.raise_for_status()
    if len(response.content) > MAX_RESPONSE_BYTES:
        raise RuntimeError("OpenBDAP national count response exceeded safety bound")
    rows = _extract_rows(response.json())
    if len(rows) > 1:
        raise RuntimeError("OpenBDAP top=1 count probe returned more than one row")
    if not rows:
        return False
    unexpected = _data_keys(rows[0]) - COUNT_ALLOWED_RETURNED_KEYS
    if unexpected:
        raise RuntimeError(
            "OpenBDAP CUP-only count projection escaped allowlist: "
            + ", ".join(sorted(unexpected))
        )
    if not _norm(rows[0].get(CUP)):
        raise RuntimeError("OpenBDAP CUP-only count probe returned no CUP")
    return True


def _count_rows(
    client: httpx.Client,
    filter_expr: str | None = None,
    *,
    known_upper_bound: int | None = None,
) -> tuple[int, int]:
    """Count rows exactly with binary search, reusing a known upper bound when available.

    Passing a known upper bound avoids a second exponential-bracketing phase for every
    lifecycle cohort. Because every lifecycle cohort is a subset of active MOP rows,
    the already measured active-row count is a safe upper bound.
    """
    requests = 1
    if not _row_exists_at_skip(client, 0, filter_expr):
        return 0, requests

    if known_upper_bound is not None:
        if known_upper_bound <= 0:
            raise ValueError("known_upper_bound must be positive")
        low = 0
        high = known_upper_bound
        if _row_exists_at_skip(client, high - 1, filter_expr):
            return high, requests + 1
        requests += 1
    else:
        low = 0
        high = 1
        while high < MAX_COUNT_PROBE_OFFSET:
            requests += 1
            if not _row_exists_at_skip(client, high, filter_expr):
                break
            low = high
            high *= 2
        else:
            raise RuntimeError("OpenBDAP count exceeded frozen probe offset ceiling")

    while low + 1 < high:
        middle = (low + high) // 2
        requests += 1
        if _row_exists_at_skip(client, middle, filter_expr):
            low = middle
        else:
            high = middle
    return high, requests


def _active_filter(extra: str | None = None) -> str:
    base = f"{STATUS_CODE} eq 'A'"
    return f"{base} and ({extra})" if extra else base


def _missing_or_sentinel(field: str) -> str:
    return f"({field} eq '' or {field} eq '{SENTINEL_DATE}')"


def _valid_date(field: str) -> str:
    return (
        f"({field} ge '{VALID_DATE_FLOOR}' and "
        f"{field} le '{VALID_DATE_CEILING}')"
    )


def _between(field: str, start: str, end: str) -> str:
    return f"({field} ge '{start}' and {field} le '{end}')"


def _lifecycle_counts(
    client: httpx.Client,
    active_rows: int,
) -> tuple[dict[str, int], dict[str, int]]:
    """Count safe lifecycle cohorts without receiving lifecycle values."""
    filters = {
        "actual_execution_start_blank": _active_filter(f"{ACTUAL_EXECUTION_START} eq ''"),
        "actual_execution_start_sentinel": _active_filter(
            f"{ACTUAL_EXECUTION_START} eq '{SENTINEL_DATE}'"
        ),
        "actual_execution_start_valid": _active_filter(_valid_date(ACTUAL_EXECUTION_START)),
        "no_actual_start_with_valid_planned_start": _active_filter(
            f"{_missing_or_sentinel(ACTUAL_EXECUTION_START)} and "
            f"{_valid_date(PLANNED_EXECUTION_START)}"
        ),
        "no_actual_start_planned_next_12m": _active_filter(
            f"{_missing_or_sentinel(ACTUAL_EXECUTION_START)} and "
            f"{_between(PLANNED_EXECUTION_START, LIFECYCLE_OBSERVED_DATE, LIFECYCLE_12M_END)}"
        ),
        "no_actual_start_planned_next_24m": _active_filter(
            f"{_missing_or_sentinel(ACTUAL_EXECUTION_START)} and "
            f"{_between(PLANNED_EXECUTION_START, LIFECYCLE_OBSERVED_DATE, LIFECYCLE_24M_END)}"
        ),
    }
    counts: dict[str, int] = {}
    requests: dict[str, int] = {}
    for name, filter_expr in filters.items():
        count, request_count = _count_rows(
            client,
            filter_expr,
            known_upper_bound=active_rows,
        )
        counts[name] = count
        requests[name] = request_count
    return counts, requests


def _fetch_batch(client: httpx.Client, cups: list[str]) -> list[dict[str, Any]]:
    requested = set(cups)
    filter_expr = " or ".join(f"{CUP} eq '{cup}'" for cup in cups)
    params = {
        "$select": ",".join(SAFE_FIELDS),
        "$filter": filter_expr,
        "$top": str(MAX_ROWS_PER_BATCH),
        "$format": "json",
    }
    last_error: Exception | None = None
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            response = client.get(BASE_URL, params=params)
            if response.is_redirect:
                raise RuntimeError("OpenBDAP overlap request redirected")
            response.raise_for_status()
            if len(response.content) > MAX_RESPONSE_BYTES:
                raise RuntimeError("OpenBDAP overlap response exceeded safety bound")
            rows = _extract_rows(response.json())
            if len(rows) >= MAX_ROWS_PER_BATCH:
                raise RuntimeError("OpenBDAP batch hit row ceiling; result may be truncated")
            for row in rows:
                keys = _data_keys(row)
                unexpected = keys - ALLOWED_RETURNED_KEYS
                if unexpected:
                    raise RuntimeError(
                        "safe projection escaped allowlist: " + ", ".join(sorted(unexpected))
                    )
                returned_cup = _norm(row.get(CUP))
                if not returned_cup or returned_cup not in requested:
                    raise RuntimeError("OpenBDAP returned a CUP outside the requested batch")
            return rows
        except (httpx.TimeoutException, httpx.TransportError) as exc:
            last_error = exc
            if attempt == MAX_ATTEMPTS:
                break
            time.sleep(2**attempt)
    raise RuntimeError("OpenBDAP CUP batch failed after retries") from last_error


def main() -> int:
    parsed = urlparse(BASE_URL)
    if parsed.scheme != "https" or parsed.hostname != ALLOWED_HOST:
        raise RuntimeError("OpenBDAP endpoint left the frozen origin")

    headers = {
        "User-Agent": "ProcRun-OpenBDAP-MOP-Safe-Coverage/5.0",
        "Accept": "application/json",
    }
    timeout = httpx.Timeout(30.0, connect=15.0)
    with httpx.Client(timeout=timeout, follow_redirects=False, headers=headers) as client:
        national_total_rows, total_count_requests = _count_rows(client)
        national_active_rows, active_count_requests = _count_rows(
            client, _active_filter()
        )
        lifecycle_counts, lifecycle_request_counts = _lifecycle_counts(
            client,
            national_active_rows,
        )

    if national_total_rows <= 0:
        raise RuntimeError("OpenBDAP national MOP count is unexpectedly empty")
    if not 0 <= national_active_rows <= national_total_rows:
        raise RuntimeError("OpenBDAP national active count is inconsistent")
    if any(not 0 <= count <= national_active_rows for count in lifecycle_counts.values()):
        raise RuntimeError("OpenBDAP lifecycle count exceeds active national population")
    if (
        lifecycle_counts["no_actual_start_planned_next_12m"]
        > lifecycle_counts["no_actual_start_planned_next_24m"]
    ):
        raise RuntimeError("OpenBDAP 12m lifecycle cohort exceeds 24m cohort")
    if (
        lifecycle_counts["no_actual_start_planned_next_24m"]
        > lifecycle_counts["no_actual_start_with_valid_planned_start"]
    ):
        raise RuntimeError("OpenBDAP future cohort exceeds valid-planned-start cohort")

    batch = collect_open_coesione_live()
    if batch.source_sha256 != FROZEN_SOURCE_SHA256:
        raise RuntimeError("frozen OpenCoesione source hash drift")
    projects = a21_projects_by_local_operation_id(batch.operations, to_funding_projects(batch))
    if len(projects) != FROZEN_PROJECT_COUNT:
        raise RuntimeError("frozen OpenCoesione project count drift")

    selected_local_ids = {project.operation_code for project in projects}
    cups_by_local_id: dict[str, str] = {}
    for operation in batch.operations:
        if operation.operation_id not in selected_local_ids or not operation.cup:
            continue
        cup = _norm(operation.cup)
        if cup:
            cups_by_local_id[operation.operation_id] = cup

    structured_local_ids = {
        project.operation_code
        for project in projects
        if structured_component_suggestions(project, list(ALL_COMPONENT_DOMAINS))
    }
    if len(structured_local_ids) != FROZEN_STRUCTURED_PROJECTS:
        raise RuntimeError("structured baseline drift")
    unresolved_local_ids = selected_local_ids - structured_local_ids

    unique_funded_cups = sorted(set(cups_by_local_id.values()))
    matched_cups: set[str] = set()
    status_codes: Counter[str] = Counter()
    status_labels: Counter[str] = Counter()
    sectors: Counter[str] = Counter()
    cups_with_sector: set[str] = set()
    cups_with_cost: set[str] = set()
    total_effective_cost = Decimal("0")
    returned_rows = 0
    batch_count = 0

    with httpx.Client(timeout=timeout, follow_redirects=False, headers=headers) as client:
        for cup_batch in _batches(unique_funded_cups, BATCH_SIZE):
            rows = _fetch_batch(client, cup_batch)
            batch_count += 1
            returned_rows += len(rows)
            for row in rows:
                cup = _norm(row.get(CUP))
                assert cup is not None
                matched_cups.add(cup)
                status_code = _norm(row.get(STATUS_CODE))
                if status_code:
                    status_codes[status_code] += 1
                status_label = _norm(row.get(STATUS_DESC))
                if status_label:
                    status_labels[status_label] += 1
                sector = _norm(row.get(SECTOR))
                if sector:
                    sectors[sector] += 1
                    cups_with_sector.add(cup)
                amount = _amount(row.get(COST_EFFECTIVE))
                if amount is not None:
                    cups_with_cost.add(cup)
                    total_effective_cost += amount

    matched_local_ids = {
        local_id for local_id, cup in cups_by_local_id.items() if cup in matched_cups
    }
    unresolved_matched = matched_local_ids & unresolved_local_ids
    structured_matched = matched_local_ids & structured_local_ids

    lifecycle_report = dict(lifecycle_counts)
    lifecycle_report["no_actual_start_with_valid_planned_start_pct_of_active"] = round(
        lifecycle_counts["no_actual_start_with_valid_planned_start"]
        * 100
        / national_active_rows,
        4,
    )
    lifecycle_report["no_actual_start_planned_next_12m_pct_of_active"] = round(
        lifecycle_counts["no_actual_start_planned_next_12m"] * 100 / national_active_rows,
        4,
    )
    lifecycle_report["no_actual_start_planned_next_24m_pct_of_active"] = round(
        lifecycle_counts["no_actual_start_planned_next_24m"] * 100 / national_active_rows,
        4,
    )
    lifecycle_report["active_unclassified_actual_start_residual"] = (
        national_active_rows
        - lifecycle_counts["actual_execution_start_blank"]
        - lifecycle_counts["actual_execution_start_sentinel"]
        - lifecycle_counts["actual_execution_start_valid"]
    )

    report = {
        "measurement_contract": "openbdap-mop-safe-coverage-v5",
        "resource_id": RESOURCE_ID,
        "national_count_method": (
            "OData $skip binary search with $top=1 and CUP-only projection; lifecycle cohorts reuse active-row upper bound"
        ),
        "national_count_probe_values_persisted": False,
        "national_total_count_probe_requests": total_count_requests,
        "national_active_count_probe_requests": active_count_requests,
        "national_lifecycle_count_probe_requests": lifecycle_request_counts,
        "national_lifecycle_count_probe_requests_total": sum(lifecycle_request_counts.values()),
        "national_total_mop_rows": national_total_rows,
        "national_active_mop_rows": national_active_rows,
        "national_active_pct": round(national_active_rows * 100 / national_total_rows, 4),
        "lifecycle_observed_date": LIFECYCLE_OBSERVED_DATE,
        "lifecycle_12m_end": LIFECYCLE_12M_END,
        "lifecycle_24m_end": LIFECYCLE_24M_END,
        "lifecycle_date_values_received": False,
        "lifecycle": lifecycle_report,
        "frozen_source_sha256": batch.source_sha256,
        "frozen_projects": len(projects),
        "frozen_projects_with_cup": len(cups_by_local_id),
        "unique_funded_cups": len(unique_funded_cups),
        "baseline_structured_projects": len(structured_local_ids),
        "baseline_unresolved_projects": len(unresolved_local_ids),
        "projection_fields": list(SAFE_FIELDS),
        "identity_fields_received": False,
        "raw_mop_rows_persisted": False,
        "request_batches": batch_count,
        "returned_mop_rows": returned_rows,
        "matched_unique_cups": len(matched_cups),
        "matched_cup_pct": round(len(matched_cups) * 100 / len(unique_funded_cups), 4),
        "matched_frozen_projects": len(matched_local_ids),
        "matched_frozen_project_pct": round(len(matched_local_ids) * 100 / len(projects), 4),
        "matched_baseline_unresolved_projects": len(unresolved_matched),
        "matched_unresolved_pct": round(
            len(unresolved_matched) * 100 / len(unresolved_local_ids), 4
        ),
        "matched_baseline_structured_projects": len(structured_matched),
        "matched_cups_with_sector": len(cups_with_sector),
        "sector_coverage_pct_of_matched": round(
            len(cups_with_sector) * 100 / len(matched_cups), 4
        )
        if matched_cups
        else 0.0,
        "matched_cups_with_effective_cost": len(cups_with_cost),
        "cost_coverage_pct_of_matched": round(
            len(cups_with_cost) * 100 / len(matched_cups), 4
        )
        if matched_cups
        else 0.0,
        "effective_cost_total_eur": str(total_effective_cost),
        "status_codes": dict(status_codes.most_common()),
        "status_labels": dict(status_labels.most_common()),
        "top_sectors": dict(sectors.most_common(25)),
    }
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
