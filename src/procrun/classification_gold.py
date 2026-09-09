"""Blind, hash-anchored gold-standard tooling for the A21 classification release gate."""

from __future__ import annotations

import hashlib
import json
import math
from datetime import date
from pathlib import Path
from typing import Any, Final

from pydantic import BaseModel, ConfigDict, Field, model_validator

from procrun.domain import ComponentState, FundingProject, ProjectState

GOLD_SCHEMA_VERSION: Final = "a21-gold-v1"
DEFAULT_BENCHMARK_SIZE: Final = 200
DEFAULT_HOLDOUT_FRACTION: Final = 0.25


class GoldStandardError(ValueError):
    """Raised when an A21 benchmark or gold package is not defensible."""


class FrozenModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


def _canonical_json(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        default=str,
    ).encode("utf-8")


def sha256_json(value: Any) -> str:
    return hashlib.sha256(_canonical_json(value)).hexdigest()


class BenchmarkManifest(FrozenModel):
    schema_version: str = GOLD_SCHEMA_VERSION
    cutoff_date: date
    selection_seed: str
    qualifying_universe_count: int = Field(ge=1)
    target_benchmark_size: int = Field(ge=1)
    holdout_fraction: float = Field(gt=0.0, lt=1.0)
    projects: tuple[FundingProject, ...]
    holdout_operation_codes: tuple[str, ...]

    @model_validator(mode="after")
    def validate_manifest(self) -> "BenchmarkManifest":
        operation_codes = tuple(project.operation_code for project in self.projects)
        if len(set(operation_codes)) != len(operation_codes):
            raise GoldStandardError("benchmark contains duplicate operation_code values")
        if not self.projects:
            raise GoldStandardError("benchmark contains no projects")
        if len(self.projects) > self.qualifying_universe_count:
            raise GoldStandardError("benchmark exceeds qualifying universe")
        required = min(self.target_benchmark_size, self.qualifying_universe_count)
        if len(self.projects) != required:
            raise GoldStandardError(
                f"benchmark must contain {required} projects, got {len(self.projects)}"
            )
        holdout = set(self.holdout_operation_codes)
        if not holdout.issubset(set(operation_codes)):
            raise GoldStandardError("holdout contains operation codes outside benchmark")
        required_holdout = math.ceil(len(self.projects) * self.holdout_fraction)
        if len(holdout) < required_holdout:
            raise GoldStandardError(
                f"holdout must contain at least {required_holdout} projects, got {len(holdout)}"
            )
        return self

    @property
    def manifest_sha256(self) -> str:
        return sha256_json(self.model_dump(mode="json"))


class GoldEvidence(FrozenModel):
    notice_id: str
    publication_date: date
    source_url: str
    title: str
    scope_description: str | None = None
    accepted_for_component: bool
    rationale: str

    @model_validator(mode="after")
    def validate_evidence(self) -> "GoldEvidence":
        if not self.notice_id.strip():
            raise GoldStandardError("gold evidence notice_id must not be blank")
        if not self.source_url.startswith(("https://", "http://")):
            raise GoldStandardError("gold evidence requires an inspectable public source URL")
        if not self.rationale.strip():
            raise GoldStandardError("gold evidence requires written rationale")
        return self


class GoldComponent(FrozenModel):
    gold_component_id: str
    category: str
    description: str
    scope_evidence: str
    scope_evidence_start: int = Field(ge=0)
    scope_evidence_end: int = Field(gt=0)
    expected_state: ComponentState
    rationale: str
    evidence: tuple[GoldEvidence, ...] = ()

    @model_validator(mode="after")
    def validate_component(self) -> "GoldComponent":
        if self.scope_evidence_end <= self.scope_evidence_start:
            raise GoldStandardError("gold component scope span is invalid")
        if not self.gold_component_id.strip() or not self.category.strip():
            raise GoldStandardError("gold component identifiers must not be blank")
        if not self.description.strip() or not self.scope_evidence.strip():
            raise GoldStandardError("gold component description/evidence must not be blank")
        if not self.rationale.strip():
            raise GoldStandardError("gold component requires written rationale")
        if self.expected_state is ComponentState.CLOSED and not any(
            item.accepted_for_component for item in self.evidence
        ):
            raise GoldStandardError("CLOSED gold component requires accepted procurement evidence")
        if self.expected_state is ComponentState.OPEN and any(
            item.accepted_for_component for item in self.evidence
        ):
            raise GoldStandardError("OPEN gold component cannot contain accepted procurement evidence")
        return self


class GoldCase(FrozenModel):
    operation_code: str
    cutoff_date: date
    components: tuple[GoldComponent, ...]
    expected_project_state: ProjectState
    rationale: str

    @model_validator(mode="after")
    def validate_case(self) -> "GoldCase":
        if not self.operation_code.strip() or not self.rationale.strip():
            raise GoldStandardError("gold case identity and rationale must not be blank")
        ids = tuple(component.gold_component_id for component in self.components)
        if len(set(ids)) != len(ids):
            raise GoldStandardError("gold case contains duplicate component IDs")
        expected = aggregate_gold_project_state(self.components)
        if self.expected_project_state is not expected:
            raise GoldStandardError(
                f"project state {self.expected_project_state} conflicts with component aggregate {expected}"
            )
        return self


class GoldTemplate(FrozenModel):
    schema_version: str = GOLD_SCHEMA_VERSION
    manifest_sha256: str
    cases: tuple[GoldCase, ...]


class FrozenGoldPackage(FrozenModel):
    schema_version: str = GOLD_SCHEMA_VERSION
    manifest: BenchmarkManifest
    cases: tuple[GoldCase, ...]
    package_sha256: str


def aggregate_gold_project_state(components: tuple[GoldComponent, ...]) -> ProjectState:
    if not components:
        return ProjectState.UNRESOLVED
    states = {component.expected_state for component in components}
    if ComponentState.UNRESOLVED in states:
        return ProjectState.UNRESOLVED
    if states == {ComponentState.CLOSED}:
        return ProjectState.CLOSED
    if states == {ComponentState.OPEN}:
        return ProjectState.OPEN
    if states == {ComponentState.OPEN, ComponentState.CLOSED}:
        return ProjectState.PARTIAL
    return ProjectState.UNRESOLVED


def load_funding_projects_jsonl(path: Path) -> tuple[FundingProject, ...]:
    projects: list[FundingProject] = []
    for line_number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not raw.strip():
            continue
        try:
            projects.append(FundingProject.model_validate_json(raw))
        except ValueError as exc:
            raise GoldStandardError(f"invalid FundingProject JSONL line {line_number}: {exc}") from exc
    if not projects:
        raise GoldStandardError("FundingProject JSONL contains no projects")
    return tuple(projects)


def _rank(seed: str, operation_code: str) -> str:
    return hashlib.sha256(f"{seed}\0{operation_code}".encode()).hexdigest()


def build_benchmark_manifest(
    projects: tuple[FundingProject, ...],
    *,
    cutoff_date: date,
    selection_seed: str,
    target_benchmark_size: int = DEFAULT_BENCHMARK_SIZE,
    holdout_fraction: float = DEFAULT_HOLDOUT_FRACTION,
) -> BenchmarkManifest:
    if not selection_seed.strip():
        raise GoldStandardError("selection seed must not be blank")
    by_code: dict[str, FundingProject] = {}
    for project in projects:
        if project.operation_code in by_code:
            raise GoldStandardError(f"duplicate operation_code in source universe: {project.operation_code}")
        by_code[project.operation_code] = project
    ranked = sorted(projects, key=lambda item: (_rank(selection_seed, item.operation_code), item.operation_code))
    selected = tuple(ranked[: min(target_benchmark_size, len(ranked))])
    holdout_count = math.ceil(len(selected) * holdout_fraction)
    holdout_ranked = sorted(
        selected,
        key=lambda item: (_rank(f"{selection_seed}:holdout", item.operation_code), item.operation_code),
    )
    holdout_codes = tuple(item.operation_code for item in holdout_ranked[:holdout_count])
    return BenchmarkManifest(
        cutoff_date=cutoff_date,
        selection_seed=selection_seed,
        qualifying_universe_count=len(projects),
        target_benchmark_size=target_benchmark_size,
        holdout_fraction=holdout_fraction,
        projects=selected,
        holdout_operation_codes=holdout_codes,
    )


def empty_gold_template(manifest: BenchmarkManifest) -> dict[str, Any]:
    """Create a deliberately non-validatable template without exposing engine answers."""

    return {
        "schema_version": GOLD_SCHEMA_VERSION,
        "manifest_sha256": manifest.manifest_sha256,
        "cases": [
            {
                "operation_code": project.operation_code,
                "cutoff_date": manifest.cutoff_date.isoformat(),
                "project_title": project.project_title,
                "project_scope_text": project.project_scope_text,
                "region": project.region,
                "municipality": project.municipality,
                "source_url": project.source_url,
                "components": [],
                "expected_project_state": None,
                "rationale": "",
            }
            for project in manifest.projects
        ],
        "instructions": (
            "Adjudicate from public source material only. Do not inspect ProcRun engine output. "
            "Before freezing, remove helper project_* / region / municipality / source_url fields "
            "from each case so the completed file conforms to GoldTemplate."
        ),
    }


def validate_gold_against_manifest(
    manifest: BenchmarkManifest, template: GoldTemplate
) -> tuple[GoldCase, ...]:
    if template.manifest_sha256 != manifest.manifest_sha256:
        raise GoldStandardError("gold template points to a different benchmark manifest")
    by_code = {case.operation_code: case for case in template.cases}
    expected_codes = {project.operation_code for project in manifest.projects}
    if set(by_code) != expected_codes or len(by_code) != len(template.cases):
        raise GoldStandardError("gold cases must match the benchmark operation codes exactly once")
    project_by_code = {project.operation_code: project for project in manifest.projects}
    for case in template.cases:
        if case.cutoff_date != manifest.cutoff_date:
            raise GoldStandardError(f"cutoff mismatch for {case.operation_code}")
        source = project_by_code[case.operation_code].project_scope_text
        for component in case.components:
            if component.scope_evidence_end > len(source):
                raise GoldStandardError(
                    f"scope span exceeds source text for {case.operation_code}/{component.gold_component_id}"
                )
            observed = source[component.scope_evidence_start : component.scope_evidence_end]
            if observed != component.scope_evidence:
                raise GoldStandardError(
                    f"scope evidence is not verbatim for {case.operation_code}/{component.gold_component_id}"
                )
            for evidence in component.evidence:
                if evidence.accepted_for_component and evidence.publication_date > manifest.cutoff_date:
                    raise GoldStandardError(
                        f"post-cutoff evidence cannot close {case.operation_code}/{component.gold_component_id}"
                    )
    return tuple(by_code[project.operation_code] for project in manifest.projects)


def freeze_gold_package(manifest: BenchmarkManifest, template: GoldTemplate) -> FrozenGoldPackage:
    cases = validate_gold_against_manifest(manifest, template)
    payload = {
        "schema_version": GOLD_SCHEMA_VERSION,
        "manifest": manifest.model_dump(mode="json"),
        "cases": [case.model_dump(mode="json") for case in cases],
    }
    return FrozenGoldPackage(
        manifest=manifest,
        cases=cases,
        package_sha256=sha256_json(payload),
    )
