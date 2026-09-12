from procrun.component_engine import ComponentDomain
from procrun.eu_objective_mapping import INTERVENTION_FIELD_MAP


def test_phase_r_candidates_remain_outside_production_component_domain() -> None:
    values = {domain.value for domain in ComponentDomain}
    assert "digital_transformation" not in values
    assert "waste_circular_economy" not in values


def test_phase_r_candidate_intervention_codes_remain_unmapped() -> None:
    assert "013" not in INTERVENTION_FIELD_MAP
    assert "067" not in INTERVENTION_FIELD_MAP
