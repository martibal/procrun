import json
from collections import Counter
from datetime import date
from pathlib import Path

from procrun.classification import aggregate_project_state
from procrun.domain import ComponentAssessment, ComponentState, ProjectState

FIXTURE = Path(__file__).parent / "fixtures" / "phase0_v1_1_expected.json"
ACTION_BY_STATE = {
    "CLOSED": "SUPPRESS",
    "OPEN": "DELIVER",
    "PARTIAL": "DELIVER_COMPONENTS_ONLY",
    "UNRESOLVED": "WITHHOLD",
}


def load_fixture() -> dict:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def component(component_id: str, state: ComponentState, cutoff: date) -> ComponentAssessment:
    return ComponentAssessment(
        component_id=component_id,
        state=state,
        cutoff_date=cutoff,
        rationale="Phase-0 classification oracle fixture",
        evidence_ids=(),
        coverage_note="Phase-0 classification oracle fixture",
    )


def synthetic_components(expected_state: str, cutoff: date) -> tuple[ComponentAssessment, ...]:
    if expected_state == "CLOSED":
        return (component("closed", ComponentState.CLOSED, cutoff),)
    if expected_state == "OPEN":
        return (component("open", ComponentState.OPEN, cutoff),)
    if expected_state == "UNRESOLVED":
        return (component("unresolved", ComponentState.UNRESOLVED, cutoff),)
    if expected_state == "PARTIAL":
        return (
            component("closed", ComponentState.CLOSED, cutoff),
            component("open", ComponentState.OPEN, cutoff),
        )
    raise AssertionError(f"unknown fixture state: {expected_state}")


def test_phase0_v1_1_oracle_is_complete_and_matches_frozen_counts() -> None:
    fixture = load_fixture()
    cases = fixture["cases"]

    assert len(cases) == 30
    assert [case["rank"] for case in cases] == list(range(1, 31))
    assert len({case["operation_code"] for case in cases}) == 30
    counts = Counter(case["expected_state"] for case in cases)
    assert dict(counts) == fixture["expected_counts"]
    assert fixture["source_specification_version"] == (
        "PROCUREMENT_RUNWAY_PHASE0_RESULT_V1_1_CORRECTED"
    )
    assert fixture["source_artifact_sha256"] == (
        "194c7ed3534d9c484c3b765495d25fded89a1b4e2c7bdba7373628a271f125f2"
    )


def test_phase0_action_semantics_are_locked_for_all_30_cases() -> None:
    for case in load_fixture()["cases"]:
        assert case["expected_action"] == ACTION_BY_STATE[case["expected_state"]]


def test_all_30_oracle_states_replay_project_aggregation_semantics() -> None:
    fixture = load_fixture()
    cutoff = date.fromisoformat(fixture["cutoff_date"])

    for case in fixture["cases"]:
        result = aggregate_project_state(
            case["operation_code"],
            cutoff,
            synthetic_components(case["expected_state"], cutoff),
        )
        assert result.state.value == case["expected_state"]


def test_corrected_pacs_fc_04022300_can_never_regress_to_open_in_oracle() -> None:
    cases = load_fixture()["cases"]
    corrected = next(case for case in cases if case["operation_code"] == "PACS-FC-04022300")

    assert corrected["expected_state"] == ProjectState.PARTIAL.value
    assert corrected["expected_action"] == "DELIVER_COMPONENTS_ONLY"
