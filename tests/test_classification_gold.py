from datetime import date

import pytest

from procrun.classification_gold import (
    BenchmarkManifest,
    GoldCase,
    GoldComponent,
    GoldEvidence,
    GoldStandardError,
    GoldTemplate,
    build_benchmark_manifest,
    empty_gold_template,
    freeze_gold_package,
)
from procrun.domain import ComponentState, FundingProject, ProjectState


def _project(index: int) -> FundingProject:
    scope = f"Project {index} includes installation of monitoring sensors and civil works."
    return FundingProject(
        operation_code=f"P{index:03d}",
        project_title=f"Project {index}",
        project_scope_text=scope,
        region="Lombardia",
        source_url=f"https://example.test/projects/{index}",
    )


def test_manifest_is_deterministic_and_has_25_percent_holdout() -> None:
    projects = tuple(_project(index) for index in range(250))
    first = build_benchmark_manifest(
        projects,
        cutoff_date=date(2026, 9, 9),
        selection_seed="a21-round-1",
    )
    second = build_benchmark_manifest(
        tuple(reversed(projects)),
        cutoff_date=date(2026, 9, 9),
        selection_seed="a21-round-1",
    )
    assert first == second
    assert len(first.projects) == 200
    assert len(first.holdout_operation_codes) == 50
    assert first.manifest_sha256 == second.manifest_sha256


def test_manifest_uses_entire_universe_when_smaller_than_200() -> None:
    manifest = build_benchmark_manifest(
        tuple(_project(index) for index in range(81)),
        cutoff_date=date(2026, 9, 9),
        selection_seed="small-universe",
    )
    assert len(manifest.projects) == 81
    assert len(manifest.holdout_operation_codes) == 21


def test_empty_template_contains_no_engine_answer() -> None:
    manifest = build_benchmark_manifest(
        tuple(_project(index) for index in range(4)),
        cutoff_date=date(2026, 9, 9),
        selection_seed="blind",
    )
    template = empty_gold_template(manifest)
    assert all(case["components"] == [] for case in template["cases"])
    assert all(case["expected_project_state"] is None for case in template["cases"])


def test_freeze_requires_verbatim_scope_and_pre_cutoff_closed_evidence() -> None:
    project = _project(1)
    manifest = build_benchmark_manifest(
        (project,),
        cutoff_date=date(2026, 9, 9),
        selection_seed="freeze",
    )
    phrase = "monitoring sensors"
    start = project.project_scope_text.index(phrase)
    component = GoldComponent(
        gold_component_id="P001:c1",
        category="water_wastewater:monitoring",
        description="monitoring sensors",
        scope_evidence=phrase,
        scope_evidence_start=start,
        scope_evidence_end=start + len(phrase),
        expected_state=ComponentState.CLOSED,
        rationale="The project explicitly requires this purchasable component.",
        evidence=(
            GoldEvidence(
                notice_id="TED-1",
                publication_date=date(2026, 1, 10),
                source_url="https://ted.europa.eu/example",
                title="Monitoring sensors procurement",
                accepted_for_component=True,
                rationale="Exact component and project context are supported.",
            ),
        ),
    )
    case = GoldCase(
        operation_code=project.operation_code,
        cutoff_date=manifest.cutoff_date,
        components=(component,),
        expected_project_state=ProjectState.CLOSED,
        rationale="All adjudicated components are closed.",
    )
    template = GoldTemplate(manifest_sha256=manifest.manifest_sha256, cases=(case,))
    frozen = freeze_gold_package(manifest, template)
    assert frozen.package_sha256

    bad_component = component.model_copy(update={"scope_evidence": "not verbatim"})
    bad_case = case.model_copy(update={"components": (bad_component,)})
    bad_template = template.model_copy(update={"cases": (bad_case,)})
    with pytest.raises(GoldStandardError, match="not verbatim"):
        freeze_gold_package(manifest, bad_template)


def test_gold_project_state_must_match_component_aggregate() -> None:
    with pytest.raises(GoldStandardError, match="conflicts"):
        GoldCase(
            operation_code="P001",
            cutoff_date=date(2026, 9, 9),
            components=(),
            expected_project_state=ProjectState.OPEN,
            rationale="Incorrect on purpose.",
        )


def test_manifest_rejects_duplicate_source_projects() -> None:
    project = _project(1)
    with pytest.raises(GoldStandardError, match="duplicate operation_code"):
        build_benchmark_manifest(
            (project, project),
            cutoff_date=date(2026, 9, 9),
            selection_seed="dupe",
        )


def test_manifest_round_trip_keeps_hash() -> None:
    manifest = build_benchmark_manifest(
        tuple(_project(index) for index in range(3)),
        cutoff_date=date(2026, 9, 9),
        selection_seed="roundtrip",
    )
    loaded = BenchmarkManifest.model_validate_json(manifest.model_dump_json())
    assert loaded.manifest_sha256 == manifest.manifest_sha256
