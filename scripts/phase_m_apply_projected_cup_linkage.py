from __future__ import annotations

import argparse
import re
from datetime import datetime, timezone
from uuid import UUID

import psycopg

from procrun.classification import aggregate_project_state
from procrun.domain import ComponentAssessment, ComponentState
from procrun.ledger import append_assessment_version, append_project_assessment_version
from procrun.matching import MATCH_RULE_VERSION
from procrun.production_delivery import collect_complete_ted_italy
from procrun.runway import PROJECT_CLASSIFIER_VERSION

BOUNDARY_RATIONALE = "Component boundary is ambiguous; false-OPEN protection requires withholding."
CLOSED_RATIONALE = "At least one high-confidence pre-cutoff procurement record covers the component."
TIER_A_REASON = "complete deterministic Tier A evidence covers the component"


def _norm(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", value.casefold())


def _references(value: object) -> frozenset[str]:
    if not isinstance(value, str):
        return frozenset()
    return frozenset(normalized for part in value.split("|") if (normalized := _norm(part.strip())))


def _latest_components(conn: psycopg.Connection[object]) -> list[tuple[object, ...]]:
    return conn.execute(
        """
        WITH latest AS (
            SELECT DISTINCT ON (component_id)
                version_id, assessment_id, component_id, operation_code, state, cutoff_date,
                matching_candidates, accepted_evidence_ids, rationale, coverage_note
            FROM procrun.assessment_versions
            ORDER BY component_id, cutoff_date DESC, as_of DESC, inserted_at DESC, version_id DESC
        )
        SELECT version_id, assessment_id, component_id, operation_code, state, cutoff_date,
               matching_candidates, accepted_evidence_ids, rationale, coverage_note
        FROM latest
        ORDER BY operation_code, component_id
        """
    ).fetchall()


def _latest_evidence_map(
    conn: psycopg.Connection[object],
) -> dict[str, tuple[UUID, str]]:
    rows = conn.execute(
        """
        SELECT DISTINCT ON (evidence_id) evidence_id, version_id, notice_id
        FROM procrun.procurement_evidence_versions
        ORDER BY evidence_id, as_of DESC, inserted_at DESC, version_id DESC
        """
    ).fetchall()
    return {
        str(evidence_id): (UUID(str(version_id)), str(notice_id))
        for evidence_id, version_id, notice_id in rows
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--database-url", required=True)
    parser.add_argument("--cutoff", required=True)
    args = parser.parse_args()

    cutoff = datetime.fromisoformat(args.cutoff).date()
    now = datetime.now(timezone.utc)

    # This is the same approved TED Search API route, but the production projection now includes
    # the already-qualified eForms field eu-funds-financing-id-lot. No buyer, winner, contact,
    # municipality or other identity field is requested or received.
    ted = collect_complete_ted_italy(cutoff)
    notice_refs: dict[str, frozenset[str]] = {
        str(record["notice_id"]): refs
        for record in ted.records
        if (refs := _references(record.get("project_reference")))
    }

    changed = 0
    matched_notices: set[str] = set()
    matched_components: set[str] = set()

    with psycopg.connect(args.database_url) as conn:
        rows = _latest_components(conn)
        if not rows:
            raise RuntimeError("no current component assessments found")
        evidence_map = _latest_evidence_map(conn)
        by_operation: dict[str, list[tuple[UUID, ComponentAssessment]]] = {}

        with conn.transaction():
            for (
                current_version_id,
                assessment_id,
                component_id,
                operation_code,
                state,
                row_cutoff,
                matching_candidates,
                accepted_evidence_ids,
                rationale,
                coverage_note,
            ) in rows:
                if row_cutoff != cutoff:
                    raise RuntimeError(
                        f"current component cutoff drift for {component_id}: {row_cutoff} != {cutoff}"
                    )

                current_assessment = ComponentAssessment(
                    component_id=component_id,
                    state=ComponentState(state),
                    cutoff_date=row_cutoff,
                    rationale=rationale,
                    evidence_ids=tuple(accepted_evidence_ids or ()),
                    coverage_note=coverage_note,
                )
                new_assessment = current_assessment
                new_version_id = UUID(str(current_version_id))

                # Boundary ambiguity remains an independent fail-closed veto even if a CUP link exists.
                if rationale != BOUNDARY_RATIONALE:
                    op_norm = _norm(str(operation_code))
                    candidates = [dict(item) for item in (matching_candidates or [])]
                    qualifying: list[str] = []
                    accepted_versions: list[UUID] = []

                    for candidate in candidates:
                        evidence_id = str(candidate.get("evidence_id") or "")
                        evidence_entry = evidence_map.get(evidence_id)
                        if evidence_entry is None:
                            continue
                        evidence_version_id, notice_id = evidence_entry
                        refs = notice_refs.get(notice_id, frozenset())
                        features = dict(candidate.get("features") or {})
                        if (
                            op_norm
                            and op_norm in refs
                            and bool(candidate.get("pre_cutoff"))
                            and bool(features.get("high_scope_overlap"))
                            and bool(features.get("compatible_date_window"))
                        ):
                            features["exact_project_identifier"] = True
                            candidate["features"] = features
                            candidate["tier"] = "A"
                            candidate["disposition"] = "HIGH_CONFIDENCE"
                            candidate["reason"] = TIER_A_REASON
                            candidate["project_reference_source"] = (
                                "TED:eu-funds-financing-id-lot/eu-funds-identifier"
                            )
                            qualifying.append(evidence_id)
                            accepted_versions.append(evidence_version_id)
                            matched_notices.add(notice_id)

                    if qualifying:
                        new_assessment = ComponentAssessment(
                            component_id=component_id,
                            state=ComponentState.CLOSED,
                            cutoff_date=row_cutoff,
                            rationale=CLOSED_RATIONALE,
                            evidence_ids=tuple(qualifying),
                            coverage_note=coverage_note,
                        )
                        rejected = [
                            candidate
                            for candidate in candidates
                            if candidate.get("disposition") == "REJECTED"
                        ]
                        write = append_assessment_version(
                            conn,
                            assessment_id=assessment_id,
                            operation_code=operation_code,
                            assessment=new_assessment,
                            as_of=now,
                            rule_version=MATCH_RULE_VERSION,
                            model_version=None,
                            matching_candidates=candidates,
                            accepted_evidence_version_ids=tuple(accepted_versions),
                            rejected_evidence=rejected,
                        )
                        new_version_id = write.version_id
                        changed += 1
                        matched_components.add(str(component_id))

                by_operation.setdefault(str(operation_code), []).append((new_version_id, new_assessment))

            for operation_code, items in by_operation.items():
                assessments = tuple(item[1] for item in items)
                cutoffs = {assessment.cutoff_date for assessment in assessments}
                if cutoffs != {cutoff}:
                    raise RuntimeError(f"mixed current cutoff dates for {operation_code}")
                project_assessment = aggregate_project_state(
                    operation_code,
                    cutoff,
                    assessments,
                )
                append_project_assessment_version(
                    conn,
                    assessment=project_assessment,
                    component_assessment_version_ids=tuple(item[0] for item in items),
                    as_of=now,
                    classifier_version=PROJECT_CLASSIFIER_VERSION,
                )

    print(f"ted_records={len(ted.records)}")
    print(f"ted_records_with_project_reference={len(notice_refs)}")
    print(f"distinct_ted_notices_exactly_linked={len(matched_notices)}")
    print(f"components_reclassified_to_closed={changed}")
    print(f"distinct_components_exactly_linked={len(matched_components)}")
    print(f"match_rule_version={MATCH_RULE_VERSION}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
