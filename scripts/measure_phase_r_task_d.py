#!/usr/bin/env python3
"""Measure Phase R Task D after the recorded Task C result.

Task D changes only morphology-aware comparison of the already-frozen Task C phrases. Under the
Phase R confidence contract, full evidence still requires a compatible structured signal. The
measurement therefore reproduces the 4,305-project source snapshot, the 133-project structured
signal pool, and the 104-project Task C exact-phrase result before attributing any evidence upgrade
to morphology.
"""

from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from procrun.a21_identity import a21_projects_by_local_operation_id
from procrun.collectors.opencoesione import to_funding_projects
from procrun.collectors.opencoesione_live import collect_open_coesione_live
from procrun.component_engine import ComponentDomain, structured_component_suggestions
from procrun.italian_normalization import ITALIAN_NORMALIZATION_VERSION
from procrun.phase_r_morphology import TASK_D_RULE_VERSION, task_d_morphology_evidence
from procrun.phase_r_phrase_expansion import TASK_C_RULE_VERSION, task_c_phrase_evidence

FROZEN_PROJECT_COUNT = 4305
FROZEN_SOURCE_SHA256 = "35dc073ec9e5e06201080bc949a9da19dfd3366deee3524417491e2b2fd21c6a"
TASK_C_CLASSIFIED = 133
TASK_C_FULL_EVIDENCE = 106
TASK_C_STRUCTURED_ONLY = 27
TASK_C_PHRASE_EVIDENCE_PROJECTS = 104
TASK_C_UNRESOLVED = 4172
ALL_DOMAINS = tuple(ComponentDomain)
REPORT_PATH = Path("artifacts/phase-r-task-d-report.json")


def main() -> int:
    print("[D1] Collecting and verifying the frozen OpenCoesione corpus...", flush=True)
    batch = collect_open_coesione_live()
    if batch.source_sha256 != FROZEN_SOURCE_SHA256:
        raise RuntimeError(
            "Task D source snapshot differs from the recorded Task C source; measurement is "
            f"prohibited: expected={FROZEN_SOURCE_SHA256}, actual={batch.source_sha256}"
        )

    projects = a21_projects_by_local_operation_id(batch.operations, to_funding_projects(batch))
    if len(projects) != FROZEN_PROJECT_COUNT:
        raise RuntimeError(
            f"Phase R frozen corpus mismatch: expected={FROZEN_PROJECT_COUNT}, actual={len(projects)}"
        )

    structured_ids: set[str] = set()
    task_c_ids: set[str] = set()
    task_d_ids: set[str] = set()
    morphology_forms: Counter[str] = Counter()

    for project in projects:
        structured = structured_component_suggestions(project, list(ALL_DOMAINS))
        if structured:
            structured_ids.add(project.operation_code)

        c_evidence = task_c_phrase_evidence(project, structured)
        if c_evidence:
            task_c_ids.add(project.operation_code)

        d_evidence = task_d_morphology_evidence(project, structured)
        if d_evidence:
            task_d_ids.add(project.operation_code)
            for item in d_evidence:
                morphology_forms[item.text.casefold()] += 1

    if len(structured_ids) != TASK_C_CLASSIFIED:
        raise RuntimeError(
            "Structured-signal pool drifted from the recorded Task C classified population: "
            f"expected={TASK_C_CLASSIFIED}, actual={len(structured_ids)}"
        )
    if len(task_c_ids) != TASK_C_PHRASE_EVIDENCE_PROJECTS:
        raise RuntimeError(
            "Task C exact-phrase population did not reproduce: "
            f"expected={TASK_C_PHRASE_EVIDENCE_PROJECTS}, actual={len(task_c_ids)}"
        )

    task_d_new_full_ids = task_d_ids - task_c_ids
    full_phrase_evidence_ids = task_c_ids | task_d_ids

    # Task C recorded 106 full-evidence projects: 104 C-phrase projects plus two pre-existing
    # Task A full-evidence projects. Those two are outside this isolated C/D phrase module.
    full_evidence_after_d = TASK_C_FULL_EVIDENCE + len(task_d_new_full_ids)
    structured_only_after_d = TASK_C_CLASSIFIED - full_evidence_after_d
    if structured_only_after_d < 0:
        raise RuntimeError("Task D full-evidence count exceeds the frozen structured-signal pool")

    # Under the binding confidence model, morphology cannot create a classified project without a
    # structured signal. Task C already classified every project in that 133-project pool, so D can
    # improve evidence quality but cannot increase classified coverage by construction.
    classified_after_d = len(structured_ids)
    unresolved_after_d = FROZEN_PROJECT_COUNT - classified_after_d

    report = {
        "schema_version": "phase-r-task-d-measurement-v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_resource_sha256": batch.source_sha256,
        "frozen_project_count": FROZEN_PROJECT_COUNT,
        "task_c_rule_version": TASK_C_RULE_VERSION,
        "task_d_rule_version": TASK_D_RULE_VERSION,
        "normalization_version": ITALIAN_NORMALIZATION_VERSION,
        "task_c_classified": TASK_C_CLASSIFIED,
        "task_c_full_evidence": TASK_C_FULL_EVIDENCE,
        "task_c_structured_only": TASK_C_STRUCTURED_ONLY,
        "task_c_unresolved": TASK_C_UNRESOLVED,
        "task_c_phrase_evidence_projects": len(task_c_ids),
        "task_d_morphology_evidence_projects": len(task_d_ids),
        "task_d_new_full_evidence_vs_task_c": len(task_d_new_full_ids),
        "phrase_evidence_projects_after_task_d": len(full_phrase_evidence_ids),
        "full_evidence_after_task_d": full_evidence_after_d,
        "structured_only_after_task_d": structured_only_after_d,
        "newly_classified_attributable_to_task_d": 0,
        "classified_after_task_d": classified_after_d,
        "classified_pct_after_task_d": round(
            classified_after_d / FROZEN_PROJECT_COUNT * 100, 4
        ),
        "unresolved_after_task_d": unresolved_after_d,
        "morphology_forms": dict(sorted(morphology_forms.items())),
        "structured_signal_ceiling": len(structured_ids),
        "structured_signal_ceiling_pct": round(
            len(structured_ids) / FROZEN_PROJECT_COUNT * 100, 4
        ),
        "target_pct": 40.0,
        "target_met": classified_after_d / FROZEN_PROJECT_COUNT >= 0.40,
    }

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True), flush=True)
    print(f"[D2] Wrote {REPORT_PATH}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
