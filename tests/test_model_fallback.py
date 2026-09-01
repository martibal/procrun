import pytest
from pydantic import ValidationError

from procrun.component_engine import ComponentDomain, extract_components
from procrun.domain import FundingProject
from procrun.model_fallback import (
    MODEL_FALLBACK_CONTRACT_VERSION,
    LocalModelIdentity,
    ModelComponentProposal,
    ModelFallbackError,
    ModelProposalBatch,
    apply_model_proposals,
    build_local_model_request,
)

MODEL = LocalModelIdentity(model_id="fixture-3b-q4", artifact_sha256="a" * 64)


def project(scope: str) -> FundingProject:
    return FundingProject(
        operation_code="PACS-FC-FALLBACK",
        project_scope_text=scope,
        source_url="https://example.invalid/project",
    )


def base_extraction(scope: str):
    item = project(scope)
    extraction = extract_components(item, (ComponentDomain.WATER_WASTEWATER,))
    return item, extraction


def batch_for(item: FundingProject, extraction, proposals=(), model=MODEL):
    request = build_local_model_request(item, extraction)
    return ModelProposalBatch(
        operation_code=item.operation_code,
        source_sha256=request.source_sha256,
        model_identity=model,
        proposals=proposals,
    )


def test_request_contains_only_unmatched_allowlisted_scope_and_taxonomy() -> None:
    item, extraction = base_extraction(
        "A operação inclui bombas. Inclui uma unidade técnica especial."
    )
    request = build_local_model_request(item, extraction)

    assert [span.text for span in request.unmatched_scope_spans] == [
        "Inclui uma unidade técnica especial."
    ]
    assert request.domains == (ComponentDomain.WATER_WASTEWATER,)
    assert any(category.category == "pumps" for category in request.allowed_categories)
    assert set(request.model_dump()) == {
        "contract_version",
        "operation_code",
        "source_sha256",
        "domains",
        "unmatched_scope_spans",
        "allowed_categories",
    }


def test_valid_proposal_becomes_component_with_exact_span_and_bound_model_hash() -> None:
    item, extraction = base_extraction("Inclui uma unidade de osmose inversa.")
    request = build_local_model_request(item, extraction)
    span = request.unmatched_scope_spans[0]
    proposal = ModelComponentProposal(
        domain=ComponentDomain.WATER_WASTEWATER,
        category="treatment_equipment",
        start=span.start,
        end=span.end,
        source_text=span.text,
    )

    result = apply_model_proposals(
        item,
        extraction,
        batch_for(item, extraction, (proposal,)),
        expected_model=MODEL,
    )

    assert result.extraction.model_fallback_required is False
    assert result.extraction.unmatched_scope_spans == ()
    assert len(result.extraction.components) == 1
    component = result.extraction.components[0]
    assert component.component.category == "water_wastewater:treatment_equipment"
    assert component.component.scope_evidence == span.text
    assert item.project_scope_text[span.start : span.end] == span.text
    assert MODEL.artifact_sha256 in result.extractor_version


def test_model_proposal_merges_with_existing_rule_component() -> None:
    scope = "A operação inclui bombas. Prevê ainda transferência redundante de caudal."
    item, extraction = base_extraction(scope)
    request = build_local_model_request(item, extraction)
    span = request.unmatched_scope_spans[0]
    proposal = ModelComponentProposal(
        domain=ComponentDomain.WATER_WASTEWATER,
        category="pumps",
        start=span.start,
        end=span.end,
        source_text=span.text,
    )

    result = apply_model_proposals(
        item,
        extraction,
        batch_for(item, extraction, (proposal,)),
        expected_model=MODEL,
    )
    pumps = [
        component
        for component in result.extraction.components
        if component.component.category == "water_wastewater:pumps"
    ]

    assert len(pumps) == 1
    assert len(pumps[0].evidence_spans) == 2
    assert result.extraction.model_fallback_required is False


def test_hallucinated_source_text_is_rejected() -> None:
    item, extraction = base_extraction("Inclui uma unidade técnica especial.")
    span = build_local_model_request(item, extraction).unmatched_scope_spans[0]
    proposal = ModelComponentProposal(
        domain=ComponentDomain.WATER_WASTEWATER,
        category="pumps",
        start=span.start,
        end=span.end,
        source_text="Texto que não existe na fonte.",
    )

    with pytest.raises(ModelFallbackError, match="exact cited source span"):
        apply_model_proposals(
            item,
            extraction,
            batch_for(item, extraction, (proposal,)),
            expected_model=MODEL,
        )


def test_out_of_bounds_span_is_rejected() -> None:
    item, extraction = base_extraction("Inclui uma unidade técnica especial.")
    proposal = ModelComponentProposal(
        domain=ComponentDomain.WATER_WASTEWATER,
        category="pumps",
        start=0,
        end=len(item.project_scope_text) + 50,
        source_text="x",
    )

    with pytest.raises(ModelFallbackError, match="offsets"):
        apply_model_proposals(
            item,
            extraction,
            batch_for(item, extraction, (proposal,)),
            expected_model=MODEL,
        )


def test_unknown_taxonomy_category_is_rejected() -> None:
    item, extraction = base_extraction("Inclui uma unidade técnica especial.")
    span = build_local_model_request(item, extraction).unmatched_scope_spans[0]
    proposal = ModelComponentProposal(
        domain=ComponentDomain.WATER_WASTEWATER,
        category="imaginary_category",
        start=span.start,
        end=span.end,
        source_text=span.text,
    )

    with pytest.raises(ModelFallbackError, match="outside the frozen taxonomy"):
        apply_model_proposals(
            item,
            extraction,
            batch_for(item, extraction, (proposal,)),
            expected_model=MODEL,
        )


def test_out_of_scope_domain_is_rejected() -> None:
    item, extraction = base_extraction("Inclui uma intervenção ferroviária específica.")
    span = build_local_model_request(item, extraction).unmatched_scope_spans[0]
    proposal = ModelComponentProposal(
        domain=ComponentDomain.RAIL_TRANSPORT,
        category="track",
        start=span.start,
        end=span.end,
        source_text=span.text,
    )

    with pytest.raises(ModelFallbackError, match="domain outside"):
        apply_model_proposals(
            item,
            extraction,
            batch_for(item, extraction, (proposal,)),
            expected_model=MODEL,
        )


def test_wrong_model_artifact_hash_is_rejected() -> None:
    item, extraction = base_extraction("Inclui uma unidade técnica especial.")
    wrong_model = LocalModelIdentity(model_id=MODEL.model_id, artifact_sha256="b" * 64)
    wrong_batch = batch_for(item, extraction, model=wrong_model)

    with pytest.raises(ModelFallbackError, match="artifact SHA-256"):
        apply_model_proposals(
            item,
            extraction,
            wrong_batch,
            expected_model=MODEL,
        )


def test_wrong_source_hash_is_rejected() -> None:
    item, extraction = base_extraction("Inclui uma unidade técnica especial.")
    valid = batch_for(item, extraction)
    wrong = valid.model_copy(update={"source_sha256": "b" * 64})

    with pytest.raises(ModelFallbackError, match="project scope hash"):
        apply_model_proposals(item, extraction, wrong, expected_model=MODEL)


def test_proposal_cannot_rewrite_already_rule_covered_scope() -> None:
    scope = "A operação inclui bombas. Inclui uma unidade técnica especial."
    item, extraction = base_extraction(scope)
    covered = extraction.components[0].evidence_spans[0]
    proposal = ModelComponentProposal(
        domain=ComponentDomain.WATER_WASTEWATER,
        category="pumps",
        start=covered.start,
        end=covered.end,
        source_text=covered.text,
    )

    with pytest.raises(ModelFallbackError, match="unmatched scope span"):
        apply_model_proposals(
            item,
            extraction,
            batch_for(item, extraction, (proposal,)),
            expected_model=MODEL,
        )


def test_extra_state_field_is_rejected_by_schema() -> None:
    item, extraction = base_extraction("Inclui uma unidade técnica especial.")
    request = build_local_model_request(item, extraction)
    span = request.unmatched_scope_spans[0]
    payload = {
        "contract_version": MODEL_FALLBACK_CONTRACT_VERSION,
        "operation_code": item.operation_code,
        "source_sha256": request.source_sha256,
        "model_identity": MODEL.model_dump(mode="json"),
        "proposals": [
            {
                "domain": ComponentDomain.WATER_WASTEWATER.value,
                "category": "pumps",
                "start": span.start,
                "end": span.end,
                "source_text": span.text,
                "state": "OPEN",
            }
        ],
    }

    with pytest.raises(ValidationError):
        ModelProposalBatch.model_validate(payload)


def test_empty_model_result_keeps_scope_unresolved_for_fallback() -> None:
    item, extraction = base_extraction("Inclui uma unidade técnica especial.")
    result = apply_model_proposals(
        item,
        extraction,
        batch_for(item, extraction),
        expected_model=MODEL,
    )

    assert result.accepted_proposals == ()
    assert result.extraction.model_fallback_required is True
    assert result.extraction.unmatched_scope_spans == extraction.unmatched_scope_spans
