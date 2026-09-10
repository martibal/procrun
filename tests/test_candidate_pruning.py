from datetime import date

from procrun.candidates import build_match_candidates
from procrun.domain import FundingProject, ProcurementEvidence, PurchaseComponent


def _project() -> FundingProject:
    return FundingProject(
        operation_code="OP-1",
        project_title="Water upgrade",
        project_start=date(2026, 1, 1),
        project_end=date(2027, 12, 31),
        project_scope_text="New pumps.",
        nuts_code="ITC4",
        source_url="https://example.invalid/project",
    )


def _component() -> PurchaseComponent:
    return PurchaseComponent(
        component_id="cmp-1",
        operation_code="OP-1",
        category="water_wastewater:pumps",
        description="Pumps and pumping systems",
        scope_evidence="New pumps.",
    )


def _evidence(
    evidence_id: str,
    *,
    project_reference: str | None = None,
    cpv_codes: tuple[str, ...] = (),
    nuts_code: str | None = None,
    title: str = "Unrelated procurement",
) -> ProcurementEvidence:
    return ProcurementEvidence(
        evidence_id=evidence_id,
        component_id="cmp-1",
        notice_id=f"notice-{evidence_id}",
        publication_date=date(2026, 3, 1),
        title=title,
        cpv_codes=cpv_codes,
        nuts_code=nuts_code,
        project_reference=project_reference,
        source_url=f"https://example.invalid/{evidence_id}",
    )


def test_provably_rejected_broad_candidates_are_pruned_before_matching() -> None:
    project = _project()
    component = _component()
    irrelevant = _evidence("irrelevant", cpv_codes=("42122000",), nuts_code="ITF1")
    exact_reference = _evidence("reference", project_reference="OP-1")
    geographic_cpv = _evidence("geo", cpv_codes=("42122000",), nuts_code="ITC4")

    candidates = build_match_candidates(
        project,
        component,
        (irrelevant, exact_reference, geographic_cpv),
        project_reference_codes=("OP-1",),
    )

    assert tuple(candidate.evidence.evidence_id for candidate in candidates) == ("reference", "geo")


def test_title_plus_cpv_candidate_is_retained_without_geography() -> None:
    project = _project()
    component = _component()
    evidence = _evidence(
        "title",
        cpv_codes=("42122000",),
        title="Water upgrade pump procurement",
    )

    candidates = build_match_candidates(project, component, (evidence,))

    assert len(candidates) == 1
    assert candidates[0].features.project_title_or_location_match is True
    assert candidates[0].features.cpv_or_category_match is True
