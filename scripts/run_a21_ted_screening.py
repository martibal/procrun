"""Build an engine-blind TED candidate pack for A21 stratification adjudication.

The runner consumes only independently adjudicated non-ZERO screening cases. It retrieves only the
already-qualified server-side TED projection, never classifier output, and never assigns a gold or
customer state. Its output is an evidence-review queue for independent procurement adjudication.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import defaultdict
from datetime import date
from pathlib import Path
from typing import Any

from procrun.collectors.ted import TedCollectionResult, TedError, collect_ted_notices
from procrun.component_engine import RULES

REGION_NUTS = {
    "Lombardia": "ITC4",
    "Sardegna": "ITG2",
}
REGION_QUERY_TEMPLATES = (
    "place-of-performance = {nuts}",
    "place-of-performance-subdiv-proc = {nuts}",
    "RC = {nuts}",
)
DATE_QUERY_TEMPLATES = (
    "publication-date >= {start} AND publication-date <= {end}",
    "PD >= {start} AND PD <= {end}",
)
STOPWORDS = frozenset(
    {
        "della",
        "delle",
        "dello",
        "degli",
        "dell",
        "dalla",
        "dalle",
        "dallo",
        "alla",
        "alle",
        "allo",
        "nella",
        "nelle",
        "nello",
        "con",
        "per",
        "del",
        "dei",
        "una",
        "uno",
        "the",
        "and",
        "for",
        "with",
        "from",
        "project",
        "progetto",
        "intervento",
        "interventi",
        "realizzazione",
    }
)
MAX_CANDIDATES_PER_CASE = 80
START_YEAR = 2022


def _canonical_sha(value: Any) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _date_text(value: date) -> str:
    return value.strftime("%Y%m%d")


def _year_windows(cutoff: date) -> tuple[tuple[date, date], ...]:
    windows: list[tuple[date, date]] = []
    for year in range(START_YEAR, cutoff.year + 1):
        start = date(year, 1, 1)
        end = min(date(year, 12, 31), cutoff)
        windows.append((start, end))
    return tuple(windows)


def _tokens(text: str | None) -> frozenset[str]:
    if not text:
        return frozenset()
    return frozenset(
        token
        for token in re.findall(r"[a-zà-ÿ0-9]+", text.casefold())
        if len(token) >= 5 and token not in STOPWORDS
    )


def _cup(operation_code: str) -> str | None:
    first = operation_code.split("---", 1)[0].strip()
    if re.fullmatch(r"[A-Z0-9]{15}", first):
        return first
    return None


def _domain_cpv_prefixes(domains: list[str]) -> tuple[str, ...]:
    selected = set(domains)
    return tuple(
        sorted(
            {
                prefix
                for rule in RULES
                if rule.domain.value in selected
                for prefix in rule.cpv_prefixes
            },
            key=lambda item: (len(item), item),
        )
    )


def _candidate_score(case: dict[str, Any], notice: dict[str, Any]) -> tuple[int, dict[str, Any]]:
    source_text = " ".join(
        value
        for value in (case.get("project_title"), case.get("project_scope_text"))
        if isinstance(value, str)
    )
    notice_text = " ".join(
        value
        for value in (notice.get("title"), notice.get("scope_description"))
        if isinstance(value, str)
    )
    source_tokens = _tokens(source_text)
    notice_tokens = _tokens(notice_text)
    overlap = sorted(source_tokens & notice_tokens)

    cup = _cup(case["operation_code"])
    reference = (notice.get("project_reference") or "").strip().casefold()
    exact_reference = bool(cup and reference == cup.casefold())

    cpv_prefixes = _domain_cpv_prefixes(case.get("domains") or [])
    cpv_codes = tuple(str(value) for value in notice.get("cpv_codes") or ())
    cpv_match = any(code.startswith(prefix) for code in cpv_codes for prefix in cpv_prefixes)

    title = (case.get("project_title") or "").strip().casefold()
    notice_title = (notice.get("title") or "").strip().casefold()
    exact_title_fragment = bool(title and len(title) >= 20 and title in notice_title)

    score = 0
    if exact_reference:
        score += 100
    if exact_title_fragment:
        score += 25
    score += min(len(overlap), 10) * 3
    if cpv_match:
        score += 5

    reasons = {
        "exact_cup_reference": exact_reference,
        "exact_project_title_fragment": exact_title_fragment,
        "token_overlap": overlap,
        "domain_cpv_match": cpv_match,
        "domain_cpv_prefixes": cpv_prefixes,
    }
    return score, reasons


def _is_candidate(case: dict[str, Any], score: int, reasons: dict[str, Any]) -> bool:
    if reasons["exact_cup_reference"] or reasons["exact_project_title_fragment"]:
        return True
    overlap_count = len(reasons["token_overlap"])
    if overlap_count >= 2:
        return True
    return bool(reasons["domain_cpv_match"] and overlap_count >= 1 and score >= 8)


def _resolve_region_query(region: str, nuts: str, cutoff: date) -> str:
    probe_start = date(max(START_YEAR, cutoff.year - 1), 1, 1)
    date_fragment = f"publication-date >= {_date_text(probe_start)}"
    errors: list[str] = []
    for template in REGION_QUERY_TEMPLATES:
        fragment = template.format(nuts=nuts)
        query = f"{fragment} AND {date_fragment}"
        try:
            collect_ted_notices(query, page_size=1, max_pages=1)
            return fragment
        except (TedError, ValueError) as exc:
            errors.append(f"{fragment}: {type(exc).__name__}")
    raise RuntimeError(
        f"could not resolve TED region query for {region}/{nuts}: " + "; ".join(errors)
    )


def _resolve_date_template(region_fragment: str, cutoff: date) -> str:
    start = date(max(START_YEAR, cutoff.year - 1), 1, 1)
    for template in DATE_QUERY_TEMPLATES:
        query = f"{region_fragment} AND " + template.format(
            start=_date_text(start), end=_date_text(cutoff)
        )
        try:
            collect_ted_notices(query, page_size=1, max_pages=1)
            return template
        except (TedError, ValueError):
            continue
    raise RuntimeError("could not resolve TED publication-date query syntax")


def _collect_region(region: str, cutoff: date) -> tuple[tuple[dict[str, Any], ...], dict[str, Any]]:
    nuts = REGION_NUTS[region]
    region_fragment = _resolve_region_query(region, nuts, cutoff)
    date_template = _resolve_date_template(region_fragment, cutoff)

    records: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    window_audit: list[dict[str, Any]] = []
    for start, end in _year_windows(cutoff):
        query = f"{region_fragment} AND " + date_template.format(
            start=_date_text(start), end=_date_text(end)
        )
        result: TedCollectionResult = collect_ted_notices(
            query,
            page_size=250,
            max_pages=500,
            scope="ALL",
        )
        if not result.complete:
            raise RuntimeError(
                f"TED coverage incomplete for {region} {start}/{end}: {result.stop_reason}"
            )
        for notice in result.records:
            key = (str(notice["notice_id"]), str(notice["publication_date"]))
            if key in seen:
                continue
            seen.add(key)
            records.append(notice)
        window_audit.append(
            {
                "start": start.isoformat(),
                "end": end.isoformat(),
                "query": query,
                "records": len(result.records),
                "pages_fetched": result.pages_fetched,
                "total_notice_count": result.total_notice_count,
                "complete": result.complete,
            }
        )

    records.sort(key=lambda item: (str(item["publication_date"]), str(item["notice_id"])))
    audit = {
        "region": region,
        "nuts": nuts,
        "region_query": region_fragment,
        "date_query_template": date_template,
        "notice_count": len(records),
        "notice_set_sha256": _canonical_sha(records),
        "windows": window_audit,
    }
    return tuple(records), audit


def build_review_queue(input_document: dict[str, Any], cutoff: date) -> dict[str, Any]:
    cases = input_document.get("cases")
    if not isinstance(cases, list) or not cases:
        raise ValueError("input requires non-empty cases")
    if any(case.get("component_count_band") == "ZERO" for case in cases):
        raise ValueError("TED screening input must contain non-ZERO cases only")

    by_region: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for case in cases:
        region = case.get("region")
        if region not in REGION_NUTS:
            raise ValueError(f"unsupported A21 TED screening region: {region!r}")
        by_region[region].append(case)

    notices_by_region: dict[str, tuple[dict[str, Any], ...]] = {}
    region_audit: list[dict[str, Any]] = []
    for region in sorted(by_region):
        notices, audit = _collect_region(region, cutoff)
        notices_by_region[region] = notices
        region_audit.append(audit)

    queue: list[dict[str, Any]] = []
    for case in sorted(cases, key=lambda item: int(item["case_number"])):
        project_start = case.get("project_start")
        start_date = date.fromisoformat(project_start) if project_start else date(START_YEAR, 1, 1)
        candidates: list[dict[str, Any]] = []
        total_eligible = 0
        for notice in notices_by_region[case["region"]]:
            publication_date = date.fromisoformat(str(notice["publication_date"]))
            if publication_date < start_date or publication_date > cutoff:
                continue
            total_eligible += 1
            score, reasons = _candidate_score(case, notice)
            if not _is_candidate(case, score, reasons):
                continue
            candidates.append(
                {
                    "score": score,
                    "reasons": reasons,
                    "notice": notice,
                }
            )

        candidates.sort(
            key=lambda item: (
                -int(item["score"]),
                str(item["notice"]["publication_date"]),
                str(item["notice"]["notice_id"]),
            )
        )
        truncated = len(candidates) > MAX_CANDIDATES_PER_CASE
        retained = candidates[:MAX_CANDIDATES_PER_CASE]
        queue.append(
            {
                "case_number": case["case_number"],
                "operation_code": case["operation_code"],
                "region": case["region"],
                "domains": case.get("domains") or [],
                "components": case.get("components") or [],
                "project_title": case.get("project_title"),
                "project_scope_text": case.get("project_scope_text"),
                "project_start": case.get("project_start"),
                "regional_notices_date_eligible": total_eligible,
                "candidate_count": len(candidates),
                "candidate_truncated": truncated,
                "candidates": retained,
                "independent_adjudication": {
                    "procurement_band": None,
                    "expected_project_state": None,
                    "rationale": None,
                },
            }
        )

    return {
        "schema_version": "a21-ted-review-queue-v1",
        "cutoff_date": cutoff.isoformat(),
        "source_input_sha256": _canonical_sha(input_document),
        "engine_output_used": False,
        "automatic_procurement_labels_assigned": False,
        "region_retrieval": region_audit,
        "cases": queue,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    input_document = json.loads(args.input.read_text(encoding="utf-8"))
    cutoff = date.fromisoformat(str(input_document.get("cutoff_date")))
    result = build_review_queue(input_document, cutoff)
    text = json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(text, encoding="utf-8", newline="")

    print(f"A21_TED_SCREEN_CASES={len(result['cases'])}")
    print("ENGINE_OUTPUT_USED=NO")
    print("AUTOMATIC_PROCUREMENT_LABELS_ASSIGNED=NO")
    for audit in result["region_retrieval"]:
        print(
            "A21_TED_REGION "
            f"region={audit['region']} notices={audit['notice_count']} "
            f"sha256={audit['notice_set_sha256']}"
        )
    print("A21_TED_REVIEW_QUEUE_SHA256=" + hashlib.sha256(text.encode("utf-8")).hexdigest())
    print("A21_TED_SCREENING=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
