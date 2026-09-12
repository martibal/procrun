"""Source-linked readiness matrix with no qualification verdicts."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum

from procrun.readiness_source import PublishedRequirement, RequirementKind, SourcePackage


class AdvisorState(StrEnum):
    CONFIRMED_BY_ADVISOR = "CONFIRMED_BY_ADVISOR"
    NOT_CONFIRMED = "NOT_CONFIRMED"
    PROFESSIONAL_REVIEW_REQUIRED = "PROFESSIONAL_REVIEW_REQUIRED"


class MechanicalResultCode(StrEnum):
    BELOW_PUBLISHED_MINIMUM = "BELOW_PUBLISHED_MINIMUM"
    ABOVE_PUBLISHED_MAXIMUM = "ABOVE_PUBLISHED_MAXIMUM"
    WITHIN_PUBLISHED_BOUNDARY = "WITHIN_PUBLISHED_BOUNDARY"
    INPUT_NOT_SUPPLIED = "INPUT_NOT_SUPPLIED"


ADVISOR_KINDS = {
    RequirementKind.ADVISOR_CONFIRMATION,
    RequirementKind.PROFESSIONAL_VERIFICATION,
}


@dataclass(frozen=True)
class AdvisorConfirmation:
    requirement_id: str
    state: AdvisorState


def _field_for(kind: RequirementKind) -> str | None:
    if kind in {RequirementKind.MINIMUM_EUR, RequirementKind.MAXIMUM_EUR}:
        return "proposed_funding_eur"
    if kind in {RequirementKind.MINIMUM_MONTHS, RequirementKind.MAXIMUM_MONTHS}:
        return "proposed_duration_months"
    return None


def _mechanical_result(
    requirement: PublishedRequirement,
    project_inputs: Mapping[str, int | None],
) -> dict[str, object] | None:
    field = _field_for(requirement.kind)
    if field is None:
        return None
    boundary = requirement.boundary_value
    assert boundary is not None
    value = project_inputs.get(field)
    if value is None:
        code = MechanicalResultCode.INPUT_NOT_SUPPLIED
        statement = f"No project value was supplied for {field}."
    elif requirement.kind in {RequirementKind.MINIMUM_EUR, RequirementKind.MINIMUM_MONTHS}:
        if value < boundary:
            code = MechanicalResultCode.BELOW_PUBLISHED_MINIMUM
            statement = f"{value} is below the published minimum of {boundary}."
        else:
            code = MechanicalResultCode.WITHIN_PUBLISHED_BOUNDARY
            statement = f"{value} is not below the published minimum of {boundary}."
    else:
        if value > boundary:
            code = MechanicalResultCode.ABOVE_PUBLISHED_MAXIMUM
            statement = f"{value} is above the published maximum of {boundary}."
        else:
            code = MechanicalResultCode.WITHIN_PUBLISHED_BOUNDARY
            statement = f"{value} is not above the published maximum of {boundary}."
    return {
        "field": field,
        "user_value": value,
        "published_boundary": boundary,
        "result_code": code.value,
        "statement": statement,
        "scope_note": requirement.scope_note,
    }


def build_readiness_matrix(
    package: SourcePackage,
    *,
    project_inputs: Mapping[str, int | None],
    confirmations: tuple[AdvisorConfirmation, ...],
) -> dict[str, object]:
    confirmation_by_id = {item.requirement_id: item for item in confirmations}
    if len(confirmation_by_id) != len(confirmations):
        raise ValueError("duplicate advisor confirmations")
    requirement_by_id = {item.requirement_id: item for item in package.requirements}
    unknown = set(confirmation_by_id) - set(requirement_by_id)
    if unknown:
        raise ValueError(f"unknown requirement confirmations: {sorted(unknown)}")
    invalid_confirmation_targets = sorted(
        requirement_id
        for requirement_id in confirmation_by_id
        if requirement_by_id[requirement_id].kind not in ADVISOR_KINDS
    )
    if invalid_confirmation_targets:
        raise ValueError(
            "advisor confirmations are not allowed for mechanical/reference rows: "
            f"{invalid_confirmation_targets}"
        )

    rows: list[dict[str, object]] = []
    professional_points: list[dict[str, object]] = []
    advisor_check_ids: list[str] = []
    for requirement in package.requirements:
        confirmation = confirmation_by_id.get(requirement.requirement_id)
        if requirement.kind in ADVISOR_KINDS:
            advisor_check_ids.append(requirement.requirement_id)
        row: dict[str, object] = {
            "requirement_id": requirement.requirement_id,
            "label": requirement.label,
            "kind": requirement.kind.value,
            "published_source": {
                "document_id": requirement.source_document_id,
                "citation": requirement.source_citation,
                "text": requirement.source_text,
                "scope_note": requirement.scope_note,
            },
            "mechanical_comparison": _mechanical_result(requirement, project_inputs),
            "advisor_confirmation": (
                None if confirmation is None else {"state": confirmation.state.value}
            ),
        }
        rows.append(row)
        if requirement.kind is RequirementKind.PROFESSIONAL_VERIFICATION:
            professional_points.append(
                {
                    "requirement_id": requirement.requirement_id,
                    "label": requirement.label,
                    "source_document_id": requirement.source_document_id,
                    "source_citation": requirement.source_citation,
                    "source_text": requirement.source_text,
                    "advisor_state": None if confirmation is None else confirmation.state.value,
                }
            )

    addressed = sum(
        1
        for requirement_id in advisor_check_ids
        if requirement_id in confirmation_by_id
        and confirmation_by_id[requirement_id].state is AdvisorState.CONFIRMED_BY_ADVISOR
    )
    total = len(advisor_check_ids)
    return {
        "rows": rows,
        "points_requiring_professional_verification": professional_points,
        "completion": {
            "listed_advisor_checks": total,
            "checks_confirmed_by_advisor": addressed,
            "language": (
                f"{addressed} of {total} listed advisor checks have been confirmed. "
                "Completion is not a qualification or readiness verdict."
            ),
        },
    }
