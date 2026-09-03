from datetime import date

from procrun.component_engine import ComponentDomain, extract_components
from procrun.domain import ComponentState, FundingProject, ProcurementEvidence, ProjectState
from procrun.runway import ComponentCoverage, assess_project_runway


def test_pacs_fc_04022300_can_never_regress_to_false_open_or_false_closed() -> None:
    """Replay the corrected Phase-0 failure mode under the stricter production contract.

    Phase-0 established that the funded scope contains eight level crossings while procedure
    3809/2026 covers a narrower PK 60-66 works scope. The production implementation deliberately
    withholds the grouped crossing component until that group can be decomposed or whole-group
    procurement can be proven. This is stricter than the historical PARTIAL label, but it preserves
    the critical invariant: the case can never become the old false OPEN or a false CLOSED.
    """

    project = FundingProject(
        operation_code="PACS-FC-04022300",
        project_title="Supressão de Passagens de Nível - Linha do Norte 2.º Aviso",
        project_start=date(2024, 2, 8),
        project_end=date(2029, 12, 31),
        approved_funding_eur=41_300_000,
        project_scope_text=(
            "Supressão de 8 passagens de nível: PK 60+090, PK 66+019, PK 69+474, "
            "PK 74+552, PK 76+789, PK 75+816, PK 83+230 e PN 84+031."
        ),
        programme="Sustentável 2030",
        region="Santarém/Cartaxo",
        source_url="https://sustentavel2030.gov.pt/operacao/pacs-fc-04022300/",
    )
    extracted = extract_components(project, (ComponentDomain.RAIL_TRANSPORT,))
    crossing = next(
        item.component
        for item in extracted.components
        if item.component.category == "rail_transport:crossings"
    )
    procedure = ProcurementEvidence(
        evidence_id="dre-3809-2026",
        component_id=crossing.component_id,
        notice_id="3809/2026",
        publication_date=date(2026, 2, 17),
        title=(
            "Empreitada L. NORTE - PK 60 A 66 - DESNIVELAMENTOS PARA SUPRESSÃO "
            "DE PASSAGENS DE NIVEL - EXECUÇÃO"
        ),
        scope_description=(
            "Empreitada L. NORTE - PK 60 A 66 - DESNIVELAMENTOS PARA SUPRESSÃO "
            "DE PASSAGENS DE NIVEL - EXECUÇÃO"
        ),
        cpv_codes=("45234100",),
        procedure_type="Concurso público",
        base_value_eur=19_000_000,
        source_url=(
            "https://diariodarepublica.pt/dr/detalhe/anuncio-procedimento/"
            "3809-2026-1051479936"
        ),
    )
    coverage = ComponentCoverage(
        required_source_ids=frozenset({"ted_search_api", "pt_national_procurement"}),
        complete_source_ids=frozenset({"ted_search_api", "pt_national_procurement"}),
        boundary_resolved=True,
        note="Historical fixture coverage complete through 2026-07-31.",
    )
    result = assess_project_runway(
        project,
        domains=(ComponentDomain.RAIL_TRANSPORT,),
        cutoff_date=date(2026, 7, 31),
        evidence_by_component={crossing.component_id: (procedure,)},
        coverage_by_component={crossing.component_id: coverage},
    )

    assert len(result.components) == 1
    assert result.components[0].match.assessment.state is ComponentState.UNRESOLVED
    assert result.assessment.state is ProjectState.UNRESOLVED
