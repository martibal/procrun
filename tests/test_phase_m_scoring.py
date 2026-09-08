from scripts.score_phase_m_reviews import score_closed, score_open


def _rows(verdicts: list[str]) -> list[dict[str, str]]:
    return [
        {
            "human_verdict": verdict,
            "human_reason": "Reviewed source documents manually.",
            "reviewer": "human-reviewer",
            "reviewed_at": "2026-09-08T12:00:00Z",
        }
        for verdict in verdicts
    ]


def test_closed_precision_passes_at_exact_threshold() -> None:
    score = score_closed(_rows(["CORRECT"] * 27 + ["FALSE_CLOSED"] * 3))
    assert score.rate == 0.9
    assert score.passed is True


def test_closed_precision_excludes_doubtful() -> None:
    score = score_closed(_rows(["CORRECT"] * 27 + ["FALSE_CLOSED"] * 3 + ["DOUBTFUL"] * 2))
    assert score.denominator == 30
    assert score.excluded == 2
    assert score.passed is True


def test_open_false_negative_passes_at_exact_threshold() -> None:
    score = score_open(_rows(["CONFIRMED_ABSENCE"] * 27 + ["FALSE_OPEN"] * 3))
    assert score.rate == 0.1
    assert score.passed is True


def test_open_excludes_outside_ted_coverage() -> None:
    score = score_open(
        _rows(["CONFIRMED_ABSENCE"] * 27 + ["FALSE_OPEN"] * 3 + ["OUTSIDE_TED_COVERAGE"] * 2)
    )
    assert score.denominator == 30
    assert score.excluded == 2
    assert score.passed is True
