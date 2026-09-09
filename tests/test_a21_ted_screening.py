from datetime import date

import pytest

from scripts.run_a21_ted_screening import (
    _candidate_score,
    _cup,
    _is_candidate,
    _tokens,
    _year_windows,
)


def _case() -> dict[str, object]:
    return {
        "case_number": 1,
        "operation_code": "F88C25000730007---6094137",
        "region": "Lombardia",
        "project_title": "Installazione impianto fotovoltaico e relamping",
        "project_scope_text": "Installazione impianto fotovoltaico con relamping LED",
        "project_start": "2025-01-11",
        "approved_funding_eur": 26750,
        "domains": ["energy_efficiency"],
        "components": [
            {"domain": "energy_efficiency", "category": "photovoltaic"},
            {"domain": "energy_efficiency", "category": "lighting"},
        ],
        "component_count_band": "MULTI",
        "description_precision_band": "HIGH",
    }


def test_cup_is_derived_only_from_expected_operation_code_shape() -> None:
    assert _cup("F88C25000730007---6094137") == "F88C25000730007"
    assert _cup("6094137") is None
    assert _cup("TOO-SHORT---X") is None


def test_tokens_drop_common_words_and_keep_specific_scope_terms() -> None:
    tokens = _tokens("Realizzazione della installazione fotovoltaico con relamping LED")
    assert "realizzazione" not in tokens
    assert "della" not in tokens
    assert "fotovoltaico" in tokens
    assert "relamping" in tokens


def test_exact_cup_reference_is_high_priority_candidate() -> None:
    notice = {
        "notice_id": "1-2025",
        "publication_date": "2025-02-01",
        "title": "Unrelated wording",
        "scope_description": None,
        "cpv_codes": (),
        "project_reference": "F88C25000730007",
    }
    score, reasons = _candidate_score(_case(), notice)
    assert score >= 100
    assert reasons["exact_cup_reference"] is True
    assert _is_candidate(_case(), score, reasons) is True


def test_domain_cpv_requires_lexical_support_before_candidate_acceptance() -> None:
    notice = {
        "notice_id": "2-2025",
        "publication_date": "2025-02-01",
        "title": "Generic supply contract",
        "scope_description": "Generic unrelated acquisition",
        "cpv_codes": ("09331200",),
        "project_reference": None,
    }
    score, reasons = _candidate_score(_case(), notice)
    assert reasons["domain_cpv_match"] is True
    assert reasons["token_overlap"] == []
    assert _is_candidate(_case(), score, reasons) is False


def test_two_specific_shared_tokens_are_retained_as_candidate() -> None:
    notice = {
        "notice_id": "3-2025",
        "publication_date": "2025-02-01",
        "title": "Impianto fotovoltaico e relamping edificio pubblico",
        "scope_description": None,
        "cpv_codes": (),
        "project_reference": None,
    }
    score, reasons = _candidate_score(_case(), notice)
    assert {"fotovoltaico", "relamping"}.issubset(set(reasons["token_overlap"]))
    assert _is_candidate(_case(), score, reasons) is True


def test_year_windows_are_deterministic_and_cutoff_bounded() -> None:
    windows = _year_windows(date(2026, 9, 9))
    assert windows[0] == (date(2022, 1, 1), date(2022, 12, 31))
    assert windows[-1] == (date(2026, 1, 1), date(2026, 9, 9))


def test_candidate_input_with_no_specific_overlap_is_not_promoted() -> None:
    notice = {
        "notice_id": "4-2025",
        "publication_date": "2025-02-01",
        "title": "Servizi amministrativi generali",
        "scope_description": "Supporto organizzativo",
        "cpv_codes": ("79900000",),
        "project_reference": None,
    }
    score, reasons = _candidate_score(_case(), notice)
    assert score == 0
    assert _is_candidate(_case(), score, reasons) is False


def test_cup_rejects_lowercase_or_malformed_identifiers() -> None:
    assert _cup("f88c25000730007---6094137") is None
    assert _cup("F88C2500073000---6094137") is None
