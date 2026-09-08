from __future__ import annotations

import argparse
import re
from datetime import datetime, timezone
from uuid import UUID

import psycopg

from procrun.classification import aggregate_project_state
from procrun.domain import ComponentAssessment, ComponentState
from procrun.ledger import append_assessment_version, append_project_assessment_version
from procrun.runway import PROJECT_CLASSIFIER_VERSION

RULE_VERSION = "phase-m-strict-title-v1"
RATIONALE = (
    "Strict project-title linkage plus frozen structural procurement evidence covers the component."
)
STOPWORDS = {
    "a",
    "ad",
    "ai",
    "al",
    "alla",
    "alle",
    "allo",
    "con",
    "da",
    "dal",
    "dalla",
    "delle",
    "dei",
    "del",
    "di",
    "e",
    "ed",
    "il",
    "in",
    "la",
    "le",
    "lo",
    "nel",
    "nella",
    "per",
    "su",
    "un",
    "una",
    "lavori",
    "opera",
    "opere",
    "progetto",
    "intervento",
    "realizzazione",
    "riqualificazione",
    "manutenzione",
    "adeguamento",
    "fornitura",
    "servizio",
    "servizi",
    "sistemazione",
    "messa",
    "sicurezza",
}
TOKEN_RE = re.compile(r"[a-z0-9]{3,}", re.IGNORECASE)


def tokens(value: str | None) -> set[str]:
    if not value:
        return set()
    return {
        t.casefold()
        for t in TOKEN_RE.findall(value)
        if t.casefold() not in STOPWORDS and not t.isdigit()
    }


def strict_title_match(
    project_title: str | None, title: str | None, scope: str | None
) -> tuple[bool, int, int]:
    project = tokens(project_title)
    evidence = tokens((title or "") + " " + (scope or ""))
    if len(project) < 4:
        return False, 0, len(project)
    matched = len(project & evidence)
    required = max(4, (3 * len(project) + 3) // 4)
    return matched >= required, matched, len(project)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--database-url", required=True)
    args = ap.parse_args()
    now = datetime.now(timezone.utc)
    promoted = 0
    qualifying_candidates = 0
    max_match_tokens = 0

    with psycopg.connect(args.database_url) as conn:
        rows = conn.execute("""
            WITH latest AS (
              SELECT DISTINCT ON (component_id)
                     version_id, assessment_id, component_id, operation_code,
                     state, cutoff_date,
                     matching_candidates,accepted_evidence_ids,rationale,coverage_note
              FROM procrun.assessment_versions
              ORDER BY component_id,cutoff_date DESC,as_of DESC,inserted_at DESC,version_id DESC
            ) SELECT * FROM latest ORDER BY operation_code,component_id
        """).fetchall()
        by_operation: dict[str, list[tuple[UUID, ComponentAssessment]]] = {}
        with conn.transaction():
            for row in rows:
                (
                    current_version_id,
                    assessment_id,
                    component_id,
                    operation_code,
                    state,
                    cutoff_date,
                    matching_candidates,
                    accepted_evidence_ids,
                    rationale,
                    coverage_note,
                ) = row
                assessment = ComponentAssessment(
                    component_id=component_id,
                    state=ComponentState(state),
                    cutoff_date=cutoff_date,
                    rationale=rationale,
                    evidence_ids=tuple(accepted_evidence_ids or ()),
                    coverage_note=coverage_note,
                )
                version_id = UUID(str(current_version_id))

                if state == "OPEN":
                    p = conn.execute(
                        """
                      SELECT project_title FROM procrun.funding_project_versions WHERE operation_code=%s
                      ORDER BY as_of DESC,inserted_at DESC,version_id DESC LIMIT 1
                    """,
                        (operation_code,),
                    ).fetchone()
                    project_title = None if p is None else p[0]
                    candidate_map = {str(c.get("evidence_id")): c for c in (matching_candidates or [])}
                    evidences = conn.execute(
                        """
                      SELECT DISTINCT ON (evidence_id) version_id,evidence_id,title,scope_description
                      FROM procrun.procurement_evidence_versions WHERE component_id=%s
                      ORDER BY evidence_id,as_of DESC,inserted_at DESC,version_id DESC
                    """,
                        (component_id,),
                    ).fetchall()
                    qualified: list[tuple[UUID, str, dict]] = []
                    for ev_version, ev_id, ev_title, ev_scope in evidences:
                        c = candidate_map.get(str(ev_id))
                        if not c:
                            continue
                        f = dict(c.get("features") or {})
                        structural = all(
                            bool(f.get(k))
                            for k in (
                                "geography_match",
                                "high_scope_overlap",
                                "cpv_or_category_match",
                                "compatible_date_window",
                            )
                        )
                        if not structural:
                            continue
                        ok, matched, total = strict_title_match(project_title, ev_title, ev_scope)
                        max_match_tokens = max(max_match_tokens, matched)
                        if ok:
                            qualifying_candidates += 1
                            audit = dict(c)
                            audit["tier"] = "STRICT_TITLE"
                            audit["disposition"] = "HIGH_CONFIDENCE"
                            audit["reason"] = (
                                f"strict title linkage matched {matched}/{total} "
                                "significant project-title tokens"
                            )
                            qualified.append((UUID(str(ev_version)), str(ev_id), audit))
                    if qualified:
                        qualified.sort(key=lambda x: x[1])
                        ev_version, ev_id, audit = qualified[0]
                        assessment = ComponentAssessment(
                            component_id=component_id,
                            state=ComponentState.CLOSED,
                            cutoff_date=cutoff_date,
                            rationale=RATIONALE,
                            evidence_ids=(ev_id,),
                            coverage_note=coverage_note,
                        )
                        corrected = list(matching_candidates or []) + [audit]
                        write = append_assessment_version(
                            conn,
                            assessment_id=assessment_id,
                            operation_code=operation_code,
                            assessment=assessment,
                            as_of=now,
                            rule_version=RULE_VERSION,
                            model_version=None,
                            matching_candidates=corrected,
                            accepted_evidence_version_ids=(ev_version,),
                            rejected_evidence=(),
                        )
                        version_id = write.version_id
                        promoted += 1

                by_operation.setdefault(operation_code, []).append((version_id, assessment))

            for operation_code, items in by_operation.items():
                assessments = tuple(a for _, a in items)
                cutoffs = {a.cutoff_date for a in assessments}
                if len(cutoffs) != 1:
                    raise RuntimeError(f"mixed cutoff dates for {operation_code}")
                pa = aggregate_project_state(operation_code, next(iter(cutoffs)), assessments)
                append_project_assessment_version(
                    conn,
                    assessment=pa,
                    component_assessment_version_ids=tuple(v for v, _ in items),
                    as_of=now,
                    classifier_version=PROJECT_CLASSIFIER_VERSION,
                )

    print(f"strict_title_components_reclassified_to_closed={promoted}")
    print(f"strict_title_qualifying_candidates={qualifying_candidates}")
    print(f"strict_title_max_matched_tokens={max_match_tokens}")
    print(f"rule_version={RULE_VERSION}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
