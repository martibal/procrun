from scripts.measure_phase_r_candidate_domains import CANDIDATE_RULES


def test_candidate_rules_are_exact_structured_combinations() -> None:
    assert CANDIDATE_RULES == {
        "digital_transformation": {
            "intervention_code": "013",
            "azione": "1.2.3",
            "expected_projects": 573,
        },
        "waste_circular_economy": {
            "intervention_code": "067",
            "azione": "2.6.2",
            "expected_projects": 142,
        },
    }


def test_candidate_domains_do_not_modify_production_taxonomy() -> None:
    from procrun.component_engine import ComponentDomain

    assert "digital_transformation" not in {item.value for item in ComponentDomain}
    assert "waste_circular_economy" not in {item.value for item in ComponentDomain}
