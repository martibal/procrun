from procrun.component_engine_phrase import ComponentDomain
from procrun.phase_r_candidate_domain_rules import (
    CANDIDATE_COMPONENT_RULES,
    CandidateDomain,
    candidate_rules_for,
    cpv_matches_candidate_prefixes,
)


def test_production_component_domain_enum_remains_frozen() -> None:
    assert tuple(domain.value for domain in ComponentDomain) == (
        "water_wastewater",
        "rail_transport",
        "ports_coastal",
        "energy_efficiency",
        "resilience_fire",
    )


def test_candidate_domains_are_isolated_from_production_enum() -> None:
    production_values = {domain.value for domain in ComponentDomain}
    candidate_values = {domain.value for domain in CandidateDomain}
    assert production_values.isdisjoint(candidate_values)


def test_digital_transformation_uses_bounded_official_cpv_families() -> None:
    rules = candidate_rules_for(CandidateDomain.DIGITAL_TRANSFORMATION)
    assert tuple(rule.category for rule in rules) == (
        "computer_hardware",
        "software_information_systems",
        "it_services",
    )
    assert {prefix for rule in rules for prefix in rule.cpv_prefixes} == {"302", "48", "72"}


def test_waste_circular_economy_uses_bounded_official_cpv_families() -> None:
    rules = candidate_rules_for(CandidateDomain.WASTE_CIRCULAR_ECONOMY)
    assert tuple(rule.category for rule in rules) == (
        "recycling_equipment",
        "waste_treatment_infrastructure",
        "waste_collection_treatment_recycling_services",
    )
    assert {prefix for rule in rules for prefix in rule.cpv_prefixes} == {
        "42914",
        "452221",
        "9051",
    }


def test_candidate_prefix_matcher_is_deterministic_and_fail_closed() -> None:
    assert cpv_matches_candidate_prefixes("30200000-1", ("302",))
    assert cpv_matches_candidate_prefixes("48000000-8", ("48",))
    assert cpv_matches_candidate_prefixes("72222300-0", ("72",))
    assert cpv_matches_candidate_prefixes("42914000-6", ("42914",))
    assert cpv_matches_candidate_prefixes("45222100-0", ("452221",))
    assert cpv_matches_candidate_prefixes("90514000-3", ("9051",))
    assert not cpv_matches_candidate_prefixes("90420000-7", ("9051",))
    assert not cpv_matches_candidate_prefixes(None, ("302",))
    assert not cpv_matches_candidate_prefixes("", ("302",))


def test_candidate_rule_set_has_no_duplicate_domain_category_pairs() -> None:
    pairs = [(rule.domain.value, rule.category) for rule in CANDIDATE_COMPONENT_RULES]
    assert len(pairs) == len(set(pairs))
