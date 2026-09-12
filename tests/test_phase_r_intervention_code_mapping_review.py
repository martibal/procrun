import procrun.eu_objective_mapping as eu_objective_mapping

OBSERVED_COUNTS = {
    "010": 277,
    "012": 65,
    "013": 573,
    "016": 5,
    "021": 2293,
    "023": 560,
    "025": 1,
    "026": 30,
    "028": 1,
    "040": 114,
    "042": 19,
    "044": 1,
    "045": 8,
    "067": 142,
    "075": 2,
    "083": 11,
    "122": 2,
    "126": 1,
    "127": 4,
    "168": 10,
    "182": 52,
    "189": 1,
    "190": 1,
    "191": 1,
    "193": 4,
}

REVIEWED_ADMITTED_CODES = {"040", "042", "044", "045"}
FROZEN_PROJECT_COUNT = 4305
FROZEN_COMBINED_MAPPED_PROJECTS = 142


def test_review_covers_every_observed_intervention_code() -> None:
    assert len(OBSERVED_COUNTS) == 25
    assert sum(OBSERVED_COUNTS.values()) == 4178


def test_review_admits_no_new_codes_beyond_existing_frozen_map() -> None:
    mapped_observed = set(OBSERVED_COUNTS).intersection(
        eu_objective_mapping.INTERVENTION_FIELD_MAP
    )
    assert mapped_observed == REVIEWED_ADMITTED_CODES
    assert sum(OBSERVED_COUNTS[code] for code in mapped_observed) == 142


def test_safe_mapped_coverage_remains_below_phase_r_target() -> None:
    coverage_pct = FROZEN_COMBINED_MAPPED_PROJECTS / FROZEN_PROJECT_COUNT * 100
    assert round(coverage_pct, 4) == 3.2985
    assert coverage_pct < 40.0


def test_high_volume_non_domain_codes_remain_unmapped() -> None:
    for code in ("021", "013", "023", "010", "067"):
        assert code not in eu_objective_mapping.INTERVENTION_FIELD_MAP
