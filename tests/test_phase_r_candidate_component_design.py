from procrun.component_engine_phrase import ComponentDomain
from procrun.phase_r_candidate_component_design import (
    CANDIDATE_COMPONENT_RULES,
    candidate_cpv_match,
    candidate_rules_for,
)


def test_candidate_domains_do_not_modify_production_taxonomy() -> None:
    assert {domain.value for domain in ComponentDomain} == {
        "water_wastewater",
        "rail_transport",
        "ports_coastal",
        "energy_efficiency",
        "resilience_fire",
    }


def test_candidate_rules_are_narrow_and_explicit() -> None:
    assert len(CANDIDATE_COMPONENT_RULES) == 4
    assert {rule.candidate_domain for rule in CANDIDATE_COMPONENT_RULES} == {
        "digital_transformation",
        "waste_circular_economy",
    }
    assert {rule.cpv_prefixes for rule in candidate_rules_for("digital_transformation")} == {
        ("302",),
        ("48",),
        ("72",),
    }
    assert {rule.cpv_prefixes for rule in candidate_rules_for("waste_circular_economy")} == {
        ("90514",),
    }


def test_digital_candidate_matches_only_selected_cpv_families() -> None:
    assert candidate_cpv_match("digital_transformation", "30213000-5")
    assert candidate_cpv_match("digital_transformation", "48000000-8")
    assert candidate_cpv_match("digital_transformation", "72222300-0")
    assert not candidate_cpv_match("digital_transformation", "90514000-3")
    assert not candidate_cpv_match("digital_transformation", "45000000-7")


def test_waste_candidate_is_recycling_specific() -> None:
    assert candidate_cpv_match("waste_circular_economy", "90514000-3")
    assert not candidate_cpv_match("waste_circular_economy", "90511000-2")
    assert not candidate_cpv_match("waste_circular_economy", "90513100-7")
    assert not candidate_cpv_match("waste_circular_economy", "90715270-5")
