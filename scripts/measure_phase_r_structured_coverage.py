#!/usr/bin/env python3
"""Profile safe structured-signal coverage on the frozen Phase R OpenCoesione corpus.

This is a diagnostic only. It reads only fields already admitted by the frozen OpenCoesione
collector, emits aggregate counts only, and does not alter classification semantics. The purpose is
to locate the structural reason 4,172 projects remain unresolved after Phase R A-D.
"""

from __future__ import annotations

import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from procrun.a21_identity import a21_projects_by_local_operation_id
from procrun.collectors.opencoesione import to_funding_projects
from procrun.collectors.opencoesione_live import collect_open_coesione_live
from procrun.component_engine import structured_component_suggestions
from procrun.eu_objective_mapping import INTERVENTION_FIELD_MAP, MAPPING_VERSION
from procrun.production_delivery import ALL_COMPONENT_DOMAINS

FROZEN_PROJECT_COUNT = 4305
FROZEN_SOURCE_SHA256 = "35dc073ec9e5e06201080bc949a9da19dfd3366deee3524417491e2b2fd21c6a"
FROZEN_STRUCTURED_SIGNAL_PROJECTS = 133
REPORT_PATH = Path("artifacts/phase-r-structured-coverage-profile.json")

_OBJECTIVE_CODE_RE = re.compile(r"\b((?:RSO|ISO)\d+(?:\.\d+)+)\b", re.IGNORECASE)
_ANY_THREE_DIGIT_RE = re.compile(r"(?<!\d)(\d{3})(?!\d)")
_LEADING_CODE_RE = re.compile(r"^\s*(\d{1,3})(?:\s|[-:.;])")


def _top(counter: Counter[str], limit: int = 100) -> list[dict[str, object]]:
    return [
        {"value": value, "projects": count}
        for value, count in counter.most_common(limit)
    ]


def main() -> int:
    print("[S1] Collecting frozen approved OpenCoesione corpus...", flush=True)
    batch = collect_open_coesione_live()
    if batch.source_sha256 != FROZEN_SOURCE_SHA256:
        raise RuntimeError(
            "Structured coverage profiling requires the exact frozen Phase R source: "
            f"expected={FROZEN_SOURCE_SHA256}, actual={batch.source_sha256}"
        )

    projects = a21_projects_by_local_operation_id(batch.operations, to_funding_projects(batch))
    if len(projects) != FROZEN_PROJECT_COUNT:
        raise RuntimeError(
            f"frozen project count drift: expected={FROZEN_PROJECT_COUNT}, actual={len(projects)}"
        )

    objective_exact: Counter[str] = Counter()
    objective_codes: Counter[str] = Counter()
    objective_without_code: Counter[str] = Counter()
    theme_exact: Counter[str] = Counter()
    theme_three_digit_codes: Counter[str] = Counter()
    theme_leading_codes: Counter[str] = Counter()
    theme_without_numeric_code: Counter[str] = Counter()
    current_mapped_by_source: Counter[str] = Counter()
    current_mapped_by_domain: Counter[str] = Counter()
    mapped_ids: set[str] = set()
    mapped_from_theme_ids: set[str] = set()
    intervention_known_code_occurrences: Counter[str] = Counter()

    objective_nonempty = 0
    theme_nonempty = 0

    for project in projects:
        if project.objective:
            objective_nonempty += 1
            objective_exact[project.objective] += 1
            matches = [
                match.group(1).upper()
                for match in _OBJECTIVE_CODE_RE.finditer(project.objective)
            ]
            if matches:
                objective_codes.update(set(matches))
            else:
                objective_without_code[project.objective] += 1

        if project.theme:
            theme_nonempty += 1
            theme_exact[project.theme] += 1
            codes = {match.group(1) for match in _ANY_THREE_DIGIT_RE.finditer(project.theme)}
            if codes:
                theme_three_digit_codes.update(codes)
                for code in codes:
                    if code in INTERVENTION_FIELD_MAP:
                        intervention_known_code_occurrences[code] += 1
            else:
                theme_without_numeric_code[project.theme] += 1
            leading = _LEADING_CODE_RE.search(project.theme)
            if leading:
                theme_leading_codes[leading.group(1).zfill(3)] += 1

        structured = structured_component_suggestions(project, list(ALL_COMPONENT_DOMAINS))
        if structured:
            mapped_ids.add(project.operation_code)
        for item in structured:
            current_mapped_by_source[item.source.value] += 1
            current_mapped_by_domain[item.domain.value] += 1
            if item.source.value == "intervention_category":
                mapped_from_theme_ids.add(project.operation_code)

    if len(mapped_ids) != FROZEN_STRUCTURED_SIGNAL_PROJECTS:
        raise RuntimeError(
            "current structured-signal pool no longer reproduces: "
            f"expected={FROZEN_STRUCTURED_SIGNAL_PROJECTS}, actual={len(mapped_ids)}"
        )

    report = {
        "schema_version": "phase-r-structured-coverage-profile-v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_resource_sha256": batch.source_sha256,
        "mapping_version": MAPPING_VERSION,
        "frozen_project_count": FROZEN_PROJECT_COUNT,
        "current_structured_signal_projects": len(mapped_ids),
        "current_structured_signal_pct": round(len(mapped_ids) / FROZEN_PROJECT_COUNT * 100, 4),
        "current_mapped_projects_from_intervention_category": len(mapped_from_theme_ids),
        "current_mapping_hits_by_source": dict(sorted(current_mapped_by_source.items())),
        "current_mapping_hits_by_domain": dict(sorted(current_mapped_by_domain.items())),
        "specific_objective": {
            "nonempty_projects": objective_nonempty,
            "nonempty_pct": round(objective_nonempty / FROZEN_PROJECT_COUNT * 100, 4),
            "distinct_exact_values": len(objective_exact),
            "distinct_detected_codes": len(objective_codes),
            "projects_by_detected_code": dict(sorted(objective_codes.items())),
            "top_exact_values": _top(objective_exact),
            "top_values_without_detected_code": _top(objective_without_code),
        },
        "intervention_category": {
            "nonempty_projects": theme_nonempty,
            "nonempty_pct": round(theme_nonempty / FROZEN_PROJECT_COUNT * 100, 4),
            "distinct_exact_values": len(theme_exact),
            "distinct_three_digit_codes": len(theme_three_digit_codes),
            "projects_by_three_digit_code": dict(sorted(theme_three_digit_codes.items())),
            "projects_by_leading_code": dict(sorted(theme_leading_codes.items())),
            "known_mapped_code_occurrences": dict(sorted(intervention_known_code_occurrences.items())),
            "top_exact_values": _top(theme_exact),
            "top_values_without_numeric_code": _top(theme_without_numeric_code),
        },
    }

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True), flush=True)
    print(f"[S2] Wrote {REPORT_PATH}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
