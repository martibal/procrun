from scripts.score_classification_quality_benchmark import ScoredRow, score


def row(
    *,
    category: str = "energy_efficiency:lighting",
    sector: str = "energy_efficiency",
    state: str = "OPEN",
    need_present: bool = True,
    correct_category: str | None = None,
    correct_sector: str | None = None,
    correct_state: str | None = None,
    evidence_sufficient: bool = True,
    duplicate: bool = False,
    over_specific: bool = False,
    double_review: bool = False,
) -> ScoredRow:
    expected_category = category if correct_category is None else correct_category
    expected_sector = sector if correct_sector is None else correct_sector
    expected_state = state if correct_state is None else correct_state
    return ScoredRow(
        predicted_category=category,
        predicted_sector=sector,
        predicted_state=state,
        need_present=need_present,
        correct_category=expected_category,
        correct_sector=expected_sector,
        correct_state=expected_state,
        evidence_sufficient=evidence_sufficient,
        duplicate=duplicate,
        over_specific=over_specific,
        reviewer="reviewer-a",
        reviewer_2="reviewer-b" if double_review else "",
        need_present_2="yes" if double_review and need_present else ("no" if double_review else ""),
        correct_category_2=expected_category if double_review else "",
        correct_sector_2=expected_sector if double_review else "",
        correct_state_2=expected_state if double_review else "",
        evidence_sufficient_2="yes" if double_review and evidence_sufficient else ("no" if double_review else ""),
    )


def test_launch_gate_passes_only_with_full_sample_and_reference_reliability() -> None:
    rows = [row(double_review=index < 30) for index in range(300)]
    result = score(rows)

    assert result["pass"] is True
    assert result["sample_size"] == 300
    assert result["overall_precision"] == 1.0
    assert result["open_precision"] == 1.0
    assert result["double_review_n"] == 30
    assert all(result["checks"].values())


def test_wrong_domain_is_a_real_classification_failure() -> None:
    rows = [row(double_review=index < 30) for index in range(300)]
    rows[0] = row(
        category="water_wastewater:monitoring",
        sector="water_wastewater",
        correct_category="monitoring",
        correct_sector="",
        over_specific=True,
        double_review=True,
    )
    result = score(rows)

    assert result["pass"] is False
    assert result["overall_precision"] < 1.0
    assert result["over_specificity_rate"] > 0.0


def test_open_requires_both_supported_need_and_correct_open_state() -> None:
    rows = [row(double_review=index < 30) for index in range(300)]
    rows[0] = row(need_present=False, correct_category="", correct_sector="", double_review=True)
    rows[1] = row(correct_state="CLOSED", double_review=True)
    result = score(rows)

    assert result["open_precision"] == 298 / 300
    assert result["pass"] is False


def test_sample_below_300_cannot_pass_even_when_every_row_is_correct() -> None:
    rows = [row(double_review=index < 30) for index in range(299)]
    result = score(rows)

    assert result["checks"]["benchmark_n"] is False
    assert result["pass"] is False
