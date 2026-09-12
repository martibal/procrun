import pytest
from pydantic import ValidationError

from procrun.benchmark_api_contract import (
    BenchmarkPreviewResponse,
    CohortSelection,
    CohortTier,
    ReferenceAvailability,
)


def test_free_preview_contains_no_paid_analysis_fields() -> None:
    preview = BenchmarkPreviewResponse(
        reference_availability=ReferenceAvailability.FULL,
        message="Historical reference available. Unlock the analysis to see the result.",
    )
    payload = preview.model_dump(mode="json")
    forbidden = {
        "n",
        "sample_size",
        "percentile",
        "median",
        "q1",
        "q3",
        "p90",
        "comparables",
        "operation_code",
        "project_title",
    }
    assert forbidden.isdisjoint(payload)


def test_free_preview_rejects_extra_analysis_fields() -> None:
    with pytest.raises(ValidationError):
        BenchmarkPreviewResponse.model_validate(
            {
                "reference_availability": "FULL",
                "message": "ready",
                "percentile": 91.0,
            }
        )


def test_cohort_contract_requires_keys_for_selected_tier() -> None:
    with pytest.raises(ValidationError):
        CohortSelection(tier=CohortTier.SAME_BANDO)

    assert CohortSelection(
        tier=CohortTier.SAME_ACTION_INTERVENTION,
        action_code="1.2.3",
        intervention_code="013",
    ).tier is CohortTier.SAME_ACTION_INTERVENTION
