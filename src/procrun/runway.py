"""Canonical pure orchestration for one funded-project runway assessment.

The web layer must never recreate this logic. It consumes only the customer-safe read model built
from this result.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, replace
from datetime import date

from procrun.candidates import build_match_candidates
from procrun.classification import aggregate_project_state
from procrun.component_engine import (
    COMPONENT_RULE_VERSION,
    ComponentDomain,
    ExtractedComponent,
    ExtractionResult,
    extract_components,
)
from procrun.domain import FundingProject, ProcurementEvidence, ProjectAssessment
from procrun.matching import MATCH_RULE_VERSION, ComponentMatchResult, MatchCandidate, classify_component

RUNWAY_ORCHESTRATION_VERSION = "runway-v1"
PROJECT_CLASSIFIER_VERSION = "project-state-v1"


class RunwayInvariantError(ValueError):
    """Raised when orchestration inputs cannot support a safe state."""


@dataclass(frozen=True)
class ComponentCoverage:
    complete: bool
    boundary_resolved: bool
    note: str


@dataclass(frozen=True)
class RunwayComponentResult:
    extracted: ExtractedComponent
    candidates: tuple[MatchCandidate, ...]
    match: ComponentMatchResult


@dataclass(frozen=True)
class RunwayResult:
    project: FundingProject
    cutoff_date: date
    extraction: ExtractionResult
    components: tuple[RunwayComponentResult, ...]
    assessment: ProjectAssessment
    orchestration_version: str = RUNWAY_ORCHESTRATION_VERSION
    component_rule_version: str = COMPONENT_RULE_VERSION
    match_rule_version: str = MATCH_RULE_VERSION
    project_classifier_version: str = PROJECT_CLASSIFIER_VERSION


def _with_primary_component_span(extracted: ExtractedComponent) -> ExtractedComponent:
    if not extracted.evidence_spans:
        raise RunwayInvariantError("extracted component lacks source evidence span")
    primary = extracted.evidence_spans[0]
    component = extracted.component.model_copy(
        update={
            "scope_evidence": primary.text,
            "scope_evidence_start": primary.start,
            "scope_evidence_end": primary.end,
            "scope_source_field": "project_scope_text",
        }
    )
    return replace(extracted, component=component)


def assess_project_runway(
    project: FundingProject,
    *,
    domains: Sequence[ComponentDomain],
    cutoff_date: date,
    evidence_by_component: Mapping[str, Sequence[ProcurementEvidence]],
    coverage_by_component: Mapping[str, ComponentCoverage],
) -> RunwayResult:
    """Run extraction, candidate construction, matching and project aggregation fail-closed."""

    raw_extraction = extract_components(project, domains)
    extraction = replace(
        raw_extraction,
        components=tuple(_with_primary_component_span(item) for item in raw_extraction.components),
    )
    if extraction.operation_code != project.operation_code:
        raise RunwayInvariantError("extraction/project operation code mismatch")
    if not extraction.components:
        raise RunwayInvariantError(
            "no deterministic components were extracted; fallback must resolve scope before runway"
        )

    known_component_ids = {item.component.component_id for item in extraction.components}
    unknown_evidence_keys = set(evidence_by_component) - known_component_ids
    unknown_coverage_keys = set(coverage_by_component) - known_component_ids
    if unknown_evidence_keys:
        raise RunwayInvariantError(
            "evidence supplied for unknown components: " + ", ".join(sorted(unknown_evidence_keys))
        )
    if unknown_coverage_keys:
        raise RunwayInvariantError(
            "coverage supplied for unknown components: " + ", ".join(sorted(unknown_coverage_keys))
        )

    results: list[RunwayComponentResult] = []
    for extracted in extraction.components:
        component = extracted.component
        try:
            coverage = coverage_by_component[component.component_id]
        except KeyError as exc:
            raise RunwayInvariantError(
                f"explicit procurement coverage is required for {component.component_id}"
            ) from exc
        if not coverage.note.strip():
            raise RunwayInvariantError("coverage note must not be empty")

        raw_evidence = tuple(evidence_by_component.get(component.component_id, ()))
        candidates = build_match_candidates(project, component, raw_evidence)
        match = classify_component(
            component,
            cutoff_date,
            candidates,
            coverage_complete=coverage.complete,
            component_boundary_resolved=coverage.boundary_resolved,
            coverage_note=coverage.note,
        )
        results.append(
            RunwayComponentResult(
                extracted=extracted,
                candidates=candidates,
                match=match,
            )
        )

    assessment = aggregate_project_state(
        project.operation_code,
        cutoff_date,
        tuple(item.match.assessment for item in results),
    )
    return RunwayResult(
        project=project,
        cutoff_date=cutoff_date,
        extraction=extraction,
        components=tuple(results),
        assessment=assessment,
    )
