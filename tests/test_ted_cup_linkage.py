from types import SimpleNamespace

import pytest

from procrun.candidates import _reference_matches
from procrun.collectors.ted import TedContractError, canonicalize_ted_notice


def _notice(**overrides: object) -> dict[str, object]:
    notice: dict[str, object] = {
        "publication-number": "123456-2026",
        "publication-date": "2026-09-01",
        "notice-title": {"ita": "Procedura infrastrutturale"},
        "description-proc": {"ita": "servizi di monitoraggio"},
        "classification-cpv": ["71700000"],
        "contract-nature": "services",
        "procedure-type": "open",
        "estimated-value-proc": "100000",
        "estimated-value-cur-proc": "EUR",
        "place-of-performance-subdiv-proc": ["ITC4C"],
        "eu-funds-financing-id-lot": ["FESR-OTHER", "E12B23000120003"],
        "eu-funds-identifier": ["E12B23000120003", "PROGRAMME-42"],
        "links": {"html": "https://ted.europa.eu/en/notice/-/detail/123456-2026"},
    }
    notice.update(overrides)
    return notice


def test_canonicalize_retains_all_qualified_financing_identifiers_in_stable_order() -> None:
    record = canonicalize_ted_notice(_notice())

    assert record["project_reference"] == "FESR-OTHER|E12B23000120003|PROGRAMME-42"


def test_exact_project_reference_matches_whole_normalized_token_only() -> None:
    project = SimpleNamespace(operation_code="E12B23000120003")
    evidence = SimpleNamespace(project_reference="FESR-OTHER|E12B23-00012-0003|PROGRAMME-42")

    assert _reference_matches(project, evidence) is True

    evidence.project_reference = "PREFIX-E12B23000120003-SUFFIX"
    assert _reference_matches(project, evidence) is False


def test_ted_projection_still_rejects_identity_bearing_extra_field() -> None:
    notice = _notice()
    notice["buyer-name"] = "must never be received by this projection"

    with pytest.raises(TedContractError, match="non-projected fields"):
        canonicalize_ted_notice(notice)
