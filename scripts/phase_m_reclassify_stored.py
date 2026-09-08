from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from uuid import UUID

import psycopg

from procrun.classification import aggregate_project_state
from procrun.domain import ComponentAssessment, ComponentState
from procrun.ledger import append_assessment_version, append_project_assessment_version
from procrun.matching import MATCH_RULE_VERSION
from procrun.runway import PROJECT_CLASSIFIER_VERSION

REVIEW_RATIONALE = "A pre-cutoff procurement candidate is in the review band; OPEN is prohibited."
OPEN_RATIONALE_PREFIX = "No relevant procurement found in TED as of "


def _actual_title_match(project_title: str | None, normalized: dict[str, object]) -> bool:
    if not project_title:
        return False
    needle = project_title.strip().casefold()
    if not needle:
        return False
    title = str(normalized.get("title") or "")
    scope = str(normalized.get("scope_description") or "")
    return needle in title.casefold() or needle in scope.casefold()


def _review_candidates(candidates: list[dict[str, object]]) -> list[dict[str, object]]:
    return [candidate for candidate in candidates if candidate.get("disposition") == "REVIEW"]


def _latest_component_rows(conn: psycopg.Connection[object]) -> list[tuple[object, ...]]:
    return conn.execute(
        """
        WITH latest AS (
            SELECT DISTINCT ON (component_id)
                version_id, assessment_id, component_id, operation_code, state, cutoff_date,
                as_of, rule_version, matching_candidates, accepted_evidence_ids,
                accepted_evidence_version_ids, rationale, coverage_note, inserted_at
            FROM procrun.assessment_versions
            ORDER BY component_id, cutoff_date DESC, as_of DESC, inserted_at DESC, version_id DESC
        )
        SELECT version_id, assessment_id, component_id, operation_code, state, cutoff_date,
               matching_candidates, accepted_evidence_ids, accepted_evidence_version_ids,
               rationale, coverage_note
        FROM latest
        ORDER BY operation_code, component_id
        """
    ).fetchall()


def _latest_project_title(conn: psycopg.Connection[object], operation_code: str) -> str | None:
    row = conn.execute(
        """
        SELECT project_title
        FROM procrun.funding_project_versions
        WHERE operation_code = %s
        ORDER BY as_of DESC, inserted_at DESC, version_id DESC
        LIMIT 1
        """,
        (operation_code,),
    ).fetchone()
    return None if row is None else row[0]


def _normalized_evidence(conn: psycopg.Connection[object], evidence_id: str) -> dict[str, object]:
    row = conn.execute(
        """
        SELECT s.normalized_fields
        FROM procrun.procurement_evidence_versions p
        JOIN procrun.source_record_versions s ON s.version_id = p.source_record_version_id
        WHERE p.evidence_id = %s
        ORDER BY p.as_of DESC, p.inserted_at DESC, p.version_id DESC
        LIMIT 1
        """,
        (evidence_id,),
    ).fetchone()
    if row is None:
        raise RuntimeError(f"missing normalized evidence for {evidence_id}")
    value = row[0]
    return value if isinstance(value, dict) else json.loads(value)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--database-url", required=True)
    args = parser.parse_args()

    now = datetime.now(timezone.utc)
    changed = 0
    retained_review = 0

    with psycopg.connect(args.database_url) as conn:
        rows = _latest_component_rows(conn)
        if not rows:
            raise RuntimeError("no current component assessments found")

        by_operation: dict[str, list[tuple[UUID, ComponentAssessment]]] = {}

        with conn.transaction():
            for (
                current_version_id,
                assessment_id,
                component_id,
                operation_code,
                state,
                cutoff_date,
                matching_candidates,
                accepted_evidence_ids,
                accepted_evidence_version_ids,
                rationale,
                coverage_note,
            ) in rows:
                new_version_id = UUID(str(current_version_id))
                assessment = ComponentAssessment(
                    component_id=component_id,
                    state=ComponentState(state),
                    cutoff_date=cutoff_date,
                    rationale=rationale,
                    evidence_ids=tuple(accepted_evidence_ids or ()),
                    coverage_note=coverage_note,
                )

                if state == "UNRESOLVED" and rationale == REVIEW_RATIONALE:
                    candidates = [dict(item) for item in list(matching_candidates or [])]
                    reviews = _review_candidates(candidates)
                    if len(reviews) != 1:
                        raise RuntimeError(
                            f"expected exactly one REVIEW candidate for {component_id}; got {len(reviews)}"
                        )
                    review = reviews[0]
                    if review.get("tier") != "C":
                        raise RuntimeError(f"unexpected stored review tier for {component_id}")
                    features = dict(review.get("features") or {})
                    evidence_id = str(review.get("evidence_id") or "")
                    if not evidence_id:
                        raise RuntimeError(f"missing evidence_id for {component_id}")

                    project_title = _latest_project_title(conn, operation_code)
                    normalized = _normalized_evidence(conn, evidence_id)
                    actual_title_match = _actual_title_match(project_title, normalized)

                    if actual_title_match:
                        retained_review += 1
                    else:
                        corrected_candidates: list[dict[str, object]] = []
                        for candidate in candidates:
                            current = dict(candidate)
                            if current.get("evidence_id") == evidence_id and current.get("disposition") == "REVIEW":
                                corrected_features = dict(current.get("features") or {})
                                corrected_features["project_title_or_location_match"] = False
                                current["features"] = corrected_features
                                current["tier"] = "NONE"
                                current["disposition"] = "REJECTED"
                                current["reason"] = "candidate does not satisfy a frozen Tier A-C structural rule"
                            corrected_candidates.append(current)

                        rejected = [
                            candidate
                            for candidate in corrected_candidates
                            if candidate.get("disposition") == "REJECTED"
                        ]
                        assessment = ComponentAssessment(
                            component_id=component_id,
                            state=ComponentState.OPEN,
                            cutoff_date=cutoff_date,
                            rationale=f"{OPEN_RATIONALE_PREFIX}{cutoff_date.isoformat()}.",
                            evidence_ids=(),
                            coverage_note=coverage_note,
                        )
                        write = append_assessment_version(
                            conn,
                            assessment_id=assessment_id,
                            operation_code=operation_code,
                            assessment=assessment,
                            as_of=now,
                            rule_version=MATCH_RULE_VERSION,
                            model_version=None,
                            matching_candidates=corrected_candidates,
                            accepted_evidence_version_ids=(),
                            rejected_evidence=rejected,
                        )
                        new_version_id = write.version_id
                        changed += 1

                by_operation.setdefault(operation_code, []).append((new_version_id, assessment))

            for operation_code, items in by_operation.items():
                component_assessments = tuple(item[1] for item in items)
                cutoff_dates = {item.cutoff_date for item in component_assessments}
                if len(cutoff_dates) != 1:
                    raise RuntimeError(f"mixed current cutoff dates for {operation_code}")
                project_assessment = aggregate_project_state(
                    operation_code,
                    next(iter(cutoff_dates)),
                    component_assessments,
                )
                append_project_assessment_version(
                    conn,
                    assessment=project_assessment,
                    component_assessment_version_ids=tuple(item[0] for item in items),
                    as_of=now,
                    classifier_version=PROJECT_CLASSIFIER_VERSION,
                )

    print(f"reclassified_to_open={changed}")
    print(f"retained_true_title_review={retained_review}")
    print(f"match_rule_version={MATCH_RULE_VERSION}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
