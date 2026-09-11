#!/usr/bin/env python3
"""Measure Phase R Task A on the frozen 4,305-project corpus.

The script deliberately measures Task A before any Task C phrase expansion or Task D
normalisation. It reproduces the current full production classification against complete TED
coverage, then overlays only the approved structured objective/intervention mappings.
"""

from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

from procrun.a21_identity import a21_projects_by_local_operation_id
from procrun.collectors.opencoesione import to_funding_projects
from procrun.collectors.opencoesione_live import collect_open_coesione_live
from procrun.component_engine import (
    STRUCTURED_RULE_VERSION,
    extract_components,
    structured_component_suggestions,
)
from procrun.domain import ProjectState
from procrun.eu_objective_mapping import MAPPING_VERSION
from procrun.production_delivery import (
    ALL_COMPONENT_DOMAINS,
    build_live_runway_results,
    collect_complete_ted_italy,
)

FROZEN_PROJECT_COUNT = 4305
FROZEN_BASELINE_CLASSIFIED = 116
REPORT_PATH = Path("artifacts/phase-r-task-a-report.json")

_STOPWORDS = {
    "a", "ad", "al", "alla", "alle", "con", "da", "dal", "dalla", "delle", "dei", "del",
    "di", "e", "ed", "il", "in", "la", "le", "lo", "nel", "nella", "per", "un", "una",
    "uno", "su", "sul", "sulla", "tra", "fra", "the", "and", "of", "for", "to",
}
_TOKEN_RE = re.compile(r"[A-Za-zÀ-ÖØ-öø-ÿ][A-Za-zÀ-ÖØ-öø-ÿ'-]{2,}")


def _ngrams(text: str) -> tuple[str, ...]:
    tokens = [token.casefold() for token in _TOKEN_RE.findall(text)]
    tokens = [token for token in tokens if token not in _STOPWORDS]
    grams: list[str] = []
    grams.extend(tokens)
    grams.extend(" ".join(tokens[i : i + 2]) for i in range(max(0, len(tokens) - 1)))
    grams.extend(" ".join(tokens[i : i + 3]) for i in range(max(0, len(tokens) - 2)))
    return tuple(grams)


def main() -> int:
    started = datetime.now(timezone.utc)
    cutoff = started.date()

    print("[A1] Collecting approved OpenCoesione corpus...", flush=True)
    batch = collect_open_coesione_live()
    projects = a21_projects_by_local_operation_id(batch.operations, to_funding_projects(batch))
    if len(projects) != FROZEN_PROJECT_COUNT:
        raise RuntimeError(
            f"Phase R frozen corpus mismatch: expected={FROZEN_PROJECT_COUNT}, actual={len(projects)}"
        )

    print("[A2] Reproducing current classification against complete TED coverage...", flush=True)
    ted = collect_complete_ted_italy(cutoff)
    if not ted.complete:
        raise RuntimeError("TED collection incomplete; Task A measurement prohibited")
    baseline_results = build_live_runway_results(batch, ted, cutoff_date=cutoff)
    if len(baseline_results) != FROZEN_PROJECT_COUNT:
        raise RuntimeError("baseline result count differs from frozen project count")

    baseline_classified_ids = {
        result.project.operation_code
        for result in baseline_results
        if result.assessment.state is not ProjectState.UNRESOLVED
    }
    if len(baseline_classified_ids) != FROZEN_BASELINE_CLASSIFIED:
        raise RuntimeError(
            "Phase R preregistered baseline no longer reproduces on the current source snapshot: "
            f"expected={FROZEN_BASELINE_CLASSIFIED}, actual={len(baseline_classified_ids)}. "
            "Do not retune the baseline; freeze the source snapshot before continuing."
        )

    print("[A3] Applying structured mapping only (no phrase/normalisation changes)...", flush=True)
    full_evidence_ids: set[str] = set()
    structured_only_ids: set[str] = set()
    phrase_only_legacy_ids: set[str] = set()
    any_structured_ids: set[str] = set()
    by_domain: Counter[str] = Counter()
    by_source: Counter[str] = Counter()
    ngram_counts: dict[str, Counter[str]] = defaultdict(Counter)

    for project in projects:
        phrase = extract_components(project, ALL_COMPONENT_DOMAINS)
        phrase_domains = {item.domain for item in phrase.components}
        structured = structured_component_suggestions(project, list(ALL_COMPONENT_DOMAINS))
        structured_domains = {item.domain for item in structured}
        if structured:
            any_structured_ids.add(project.operation_code)
        for item in structured:
            by_domain[item.domain.value] += 1
            by_source[item.source.value] += 1

        compatible = bool(phrase_domains & structured_domains)
        if project.operation_code in baseline_classified_ids:
            if compatible:
                full_evidence_ids.add(project.operation_code)
            else:
                phrase_only_legacy_ids.add(project.operation_code)

        if structured and not phrase.components:
            structured_only_ids.add(project.operation_code)
            for item in structured:
                ngram_counts[item.domain.value].update(_ngrams(project.project_scope_text))

    phase_r_classified_ids = full_evidence_ids | structured_only_ids
    unresolved_after_a = FROZEN_PROJECT_COUNT - len(phase_r_classified_ids)
    net_change_vs_legacy = len(phase_r_classified_ids) - FROZEN_BASELINE_CLASSIFIED

    top_ngrams = {
        domain: [
            {"phrase": phrase, "count": count}
            for phrase, count in counts.most_common(40)
            if count >= 2
        ]
        for domain, counts in sorted(ngram_counts.items())
    }

    report = {
        "schema_version": "phase-r-task-a-measurement-v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "cutoff_date": cutoff.isoformat(),
        "source_resource_sha256": batch.source_sha256,
        "ted_records": len(ted.records),
        "ted_pages": ted.pages_fetched,
        "frozen_project_count": FROZEN_PROJECT_COUNT,
        "legacy_baseline_classified": FROZEN_BASELINE_CLASSIFIED,
        "legacy_baseline_pct": round(FROZEN_BASELINE_CLASSIFIED / FROZEN_PROJECT_COUNT * 100, 4),
        "structured_rule_version": STRUCTURED_RULE_VERSION,
        "mapping_version": MAPPING_VERSION,
        "projects_with_any_structured_signal": len(any_structured_ids),
        "full_evidence_phrase_plus_compatible_structured": len(full_evidence_ids),
        "structured_only_no_phrase": len(structured_only_ids),
        "legacy_phrase_classified_without_compatible_structured": len(phrase_only_legacy_ids),
        "phase_r_classified_after_task_a": len(phase_r_classified_ids),
        "phase_r_classified_pct_after_task_a": round(
            len(phase_r_classified_ids) / FROZEN_PROJECT_COUNT * 100, 4
        ),
        "net_change_vs_legacy_baseline": net_change_vs_legacy,
        "unresolved_after_task_a": unresolved_after_a,
        "structured_signal_hits_by_domain": dict(sorted(by_domain.items())),
        "structured_signal_hits_by_source": dict(sorted(by_source.items())),
        "corpus_ngrams_for_task_c": top_ngrams,
    }

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(json.dumps(report, indent=2, sort_keys=True), flush=True)
    print(f"[A4] Wrote {REPORT_PATH}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
