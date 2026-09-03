"""Product-mechanism validation registry for funded-project source families.

Compliance approval and product validation are independent gates. A source cannot become a production
funded-project source merely because its legal/access/privacy contract becomes green.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from procrun.source_contracts import SourceContract, require_live_source


class MechanismValidationStatus(StrEnum):
    VALIDATED = "VALIDATED"
    NOT_VALIDATED = "NOT_VALIDATED"


class SourceMechanismNotValidatedError(RuntimeError):
    """Raised when a funded-project source family has not passed its own product validation."""


@dataclass(frozen=True)
class SourceUniverseValidation:
    source_id: str
    universe: str
    status: MechanismValidationStatus
    evidence: str


SOURCE_UNIVERSE_VALIDATION = {
    "pt2030_project_search": SourceUniverseValidation(
        source_id="pt2030_project_search",
        universe="Portugal 2030 public infrastructure / equipment / engineering wedge",
        status=MechanismValidationStatus.VALIDATED,
        evidence=(
            "Corrected preregistered Phase-0 v1.1: 30-project cohort, 18 CLOSED, 6 OPEN, "
            "4 PARTIAL, 2 UNRESOLVED; product-development GO for this wedge."
        ),
    ),
    "prr_projects_dados_gov": SourceUniverseValidation(
        source_id="prr_projects_dados_gov",
        universe="PRR Projects",
        status=MechanismValidationStatus.NOT_VALIDATED,
        evidence=(
            "No preregistered PRR Projects cohort has yet confirmed that the funded-project -> "
            "component -> procurement-runway mechanism transfers from the Portugal 2030 Phase-0 "
            "universe."
        ),
    ),
}


def require_validated_funded_source(source_id: str) -> SourceUniverseValidation:
    """Require source-family product validation independently of source compliance."""

    try:
        validation = SOURCE_UNIVERSE_VALIDATION[source_id]
    except KeyError as exc:
        raise SourceMechanismNotValidatedError(
            f"no product-mechanism validation is registered for funded source {source_id}"
        ) from exc
    if validation.status is not MechanismValidationStatus.VALIDATED:
        raise SourceMechanismNotValidatedError(
            f"funded source {source_id} has mechanism status {validation.status}"
        )
    return validation


def require_product_ready_funded_source(
    source_id: str,
) -> tuple[SourceContract, SourceUniverseValidation]:
    """Require both live-source approval and source-family product validation."""

    contract = require_live_source(source_id)
    validation = require_validated_funded_source(source_id)
    return contract, validation
