from datetime import date

import pytest

from procrun.source_contracts import SourceNotApprovedError, require_live_source
from procrun.source_validation import (
    MechanismValidationStatus,
    SOURCE_UNIVERSE_VALIDATION,
    SourceMechanismNotValidatedError,
    require_product_ready_funded_source,
    require_validated_funded_source,
)


def test_phase0_validation_is_scoped_to_portugal2030_universe() -> None:
    validation = SOURCE_UNIVERSE_VALIDATION["pt2030_project_search"]
    assert validation.status is MechanismValidationStatus.VALIDATED
    assert "Portugal 2030" in validation.universe
    assert "30-project cohort" in validation.evidence


def test_prr_cannot_inherit_portugal2030_phase0_validation() -> None:
    validation = SOURCE_UNIVERSE_VALIDATION["prr_projects_dados_gov"]
    assert validation.status is MechanismValidationStatus.NOT_VALIDATED
    with pytest.raises(SourceMechanismNotValidatedError):
        require_validated_funded_source("prr_projects_dados_gov")


def test_compliance_and_mechanism_validation_are_independent_gates() -> None:
    with pytest.raises(SourceNotApprovedError):
        require_live_source("pt2030_project_search", as_of=date(2026, 9, 3))
    assert (
        require_validated_funded_source("pt2030_project_search").status
        is MechanismValidationStatus.VALIDATED
    )


def test_no_current_funded_source_is_product_ready() -> None:
    for source_id in ("pt2030_project_search", "prr_projects_dados_gov"):
        with pytest.raises((SourceNotApprovedError, SourceMechanismNotValidatedError)):
            require_product_ready_funded_source(source_id)


def test_unregistered_funded_source_fails_validation_closed() -> None:
    with pytest.raises(SourceMechanismNotValidatedError):
        require_validated_funded_source("future-funded-source")
