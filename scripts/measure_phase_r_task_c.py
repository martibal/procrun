#!/usr/bin/env python3
"""Measure Phase R Task C after the recorded isolated Task A result.

This measurement intentionally avoids another full TED download. Task A already froze and
reproduced the legacy 116-project baseline against complete TED coverage. Task C changes only the
project-side evidence vocabulary, so its incremental effect can be measured on the same approved
4,305-project OpenCoesione corpus without changing procurement evidence.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from procrun.a21_identity import a21_projects_by_local_operation_id
from procrun.collectors.opencoesione import to_funding_projects
from procrun.collectors.opencoesione_live import collect_open_coesione_live
from procrun.component_engine import (
    STRUCTURED_RULE_VERSION,
    ComponentDomain,
    extract_components,
    structured_component_suggestions,
)
from procrun.eu_objective_mapping import MAPPING_VERSION
from procrun.phase_r_phrase_expansion import TASK_C_RULE_VERSION, task_c_phrase_evidence

FROZEN_PROJECT_COUNT = 4305
FROZEN_BASELINE_CLASSIFIED = 116
TASK_A_FULL_EVIDENCE = 2
TASK_A_STRUCTURED_ONLY = 127
TASK_A_CLASSIFIED = 129
TASK_A_UNRESOLVED = 4176
REPORT_PATH = Path("artifacts/phase-r-task-c-report.json")
ALL_DOMAINS = tuple(ComponentDomain)


def main() -> int:
    started = datetime.now(timezone.utc)
    print("[C1] Collecting approved OpenCoesione corpus...", flush=True)
    batch = collect_open_coesione_live()
    projects = a21_projects_by_local_operation_id(batch.operations, to_funding_projects(batch))
    if len(projects) != FROZEN_PROJECT_COUNT:
        raise RuntimeError(
            f"Phase R frozen corpus mismatch: expected={FROZEN_PROJECT_COUNT}, actual={len(projects)}"
        )

    task_a_full_ids: set[str] = set()
    task_a_structured_only_ids: set[str] = set()
    task_a_conflict_ids: set[str] = set()
    task_c_full_ids: set[str] = set()
    task_c_phrase_hits: dict[str, int] = {}

    for project in projects:
        phrase = extract_components(project, ALL_DOMAINS)
        phrase_domains = {item.domain for item in phrase.components}
        structured = structured_component_suggestions(project, list(ALL_DOMAINS))
        structured_domains = {item.domain for item in structured}
        compatible = bool(phrase_domains & structured_domains)

        if compatible:
            task_a_full_ids.add(project.operation_code)
        elif structured and not phrase.components:
            task_a_structured_only_ids.add(project.operation_code)
        elif structured:
            task_a_conflict_ids.add(project.operation_code)

        c_evidence = task_c_phrase_evidence(project, structured)
        if c_evidence:
            task_c_full_ids.add(project.operation_code)
            for item in c_evidence:
                task_c_phrase_hits[item.phrase] = task_c_phrase_hits.get(item.phrase, 0) + 1

    # Reproduce the recorded Task A project-side partition before measuring C. The isolated A
    # workflow also reproduced the 116-project TED baseline; that expensive check is not repeated.
    if len(task_a_full_ids) != TASK_A_FULL_EVIDENCE:
        raise RuntimeError(
            f"Task A full-evidence partition drifted: expected={TASK_A_FULL_EVIDENCE}, "
            f"actual={len(task_a_full_ids)}"
        )
    if len(task_a_structured_only_ids) != TASK_A_STRUCTURED_ONLY:
        raise RuntimeError(
            f"Task A structured-only partition drifted: expected={TASK_A_STRUCTURED_ONLY}, "
            f"actual={len(task_a_structured_only_ids)}"
        )

    task_c_new_full_ids = task_c_full_ids - task_a_full_ids
    # A Task C phrase can convert a previously structured-only/conflict project to full evidence.
    # It only increases total classified coverage when it resolves one of the four structured
    # conflict cases that Task A did not count at all. Structured-only -> full is a quality upgrade,
    # not an additional classified project.
    task_c_newly_classified_ids = task_c_full_ids & task_a_conflict_ids
    full_after_c = task_a_full_ids | task_c_full_ids
    structured_only_after_c = task_a_structured_only_ids - task_c_full_ids
    classified_after_c = full_after_c | structured_only_after_c
    unresolved_after_c = FROZEN_PROJECT_COUNT - len(classified_after_c)

    if len(task_a_full_ids | task_a_structured_only_ids) != TASK_A_CLASSIFIED:
        raise RuntimeError("Task A classified partition no longer reproduces the recorded 129")
    if FROZEN_PROJECT_COUNT - TASK_A_CLASSIFIED != TASK_A_UNRESOLVED:
        raise RuntimeError("recorded Task A unresolved invariant is inconsistent")

    report = {
        "schema_version": "phase-r-task-c-measurement-v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_resource_sha256": batch.source_sha256,
        "frozen_project_count": FROZEN_PROJECT_COUNT,
        "legacy_baseline_classified": FROZEN_BASELINE_CLASSIFIED,
        "task_a_classified": TASK_A_CLASSIFIED,
        "task_a_full_evidence": TASK_A_FULL_EVIDENCE,
        "task_a_structured_only": TASK_A_STRUCTURED_ONLY,
        "task_c_rule_version": TASK_C_RULE_VERSION,
        "structured_rule_version": STRUCTURED_RULE_VERSION,
        "mapping_version": MAPPING_VERSION,
        "task_c_projects_with_phrase_evidence": len(task_c_full_ids),
        "task_c_new_full_evidence_vs_task_a": len(task_c_new_full_ids),
        "newly_classified_attributable_to_task_c": len(task_c_newly_classified_ids),
        "full_evidence_after_task_c": len(full_after_c),
        "structured_only_after_task_c": len(structured_only_after_c),
        "classified_after_task_c": len(classified_after_c),
        "classified_pct_after_task_c": round(
            len(classified_after_c) / FROZEN_PROJECT_COUNT * 100, 4
        ),
        "unresolved_after_task_c": unresolved_after_c,
        "task_a_structured_conflict_cases": len(task_a_conflict_ids),
        "phrase_hits": dict(sorted(task_c_phrase_hits.items())),
        "target_pct": 40.0,
        "target_met": len(classified_after_c) / FROZEN_PROJECT_COUNT >= 0.40,
    }

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True), flush=True)
    print(f"[C2] Wrote {REPORT_PATH}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
