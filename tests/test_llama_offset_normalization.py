from procrun import component_engine, llama_adapter, model_fallback

ComponentDomain = component_engine.ComponentDomain
AllowedComponentCategory = model_fallback.AllowedComponentCategory
LocalModelRequest = model_fallback.LocalModelRequest
ModelComponentProposal = model_fallback.ModelComponentProposal
ModelPromptSpan = model_fallback.ModelPromptSpan


def _request(text: str, *, start: int = 100) -> LocalModelRequest:
    return LocalModelRequest(
        operation_code="OP-OFFSET",
        source_sha256="a" * 64,
        domains=(ComponentDomain.RAIL_TRANSPORT,),
        unmatched_scope_spans=(
            ModelPromptSpan(start=start, end=start + len(text), text=text),
        ),
        allowed_categories=(
            AllowedComponentCategory(
                domain=ComponentDomain.RAIL_TRANSPORT,
                category="electrification_catenary",
                label="Electrification and catenary",
            ),
        ),
    )


def _envelope(*, start: int, end: int, source_text: str):
    return llama_adapter.GeneratedProposalEnvelope(
        proposals=(
            ModelComponentProposal(
                domain=ComponentDomain.RAIL_TRANSPORT,
                category="electrification_catenary",
                start=start,
                end=end,
                source_text=source_text,
            ),
        )
    )


def test_unique_exact_source_text_repairs_incorrect_model_offsets() -> None:
    request = _request("A obra inclui nova subestação de tração.")
    source_text = "nova subestação de tração"
    envelope = _envelope(start=0, end=len(source_text), source_text=source_text)

    validated = llama_adapter._validate_against_request(request, envelope)

    proposal = validated.proposals[0]
    expected_start = 100 + request.unmatched_scope_spans[0].text.index(source_text)
    assert proposal.start == expected_start
    assert proposal.end == expected_start + len(source_text)
    assert proposal.source_text == source_text


def test_ambiguous_source_text_is_not_repaired_from_guessed_offsets() -> None:
    request = _request("válvula e válvula")
    envelope = _envelope(start=0, end=7, source_text="válvula")

    try:
        llama_adapter._validate_against_request(request, envelope)
    except llama_adapter.LlamaAdapterError as exc:
        assert "ambiguous" in str(exc)
    else:
        raise AssertionError("ambiguous exact evidence must fail closed")


def test_correct_offsets_disambiguate_repeated_exact_source_text() -> None:
    request = _request("válvula e válvula")
    envelope = _envelope(start=110, end=117, source_text="válvula")

    validated = llama_adapter._validate_against_request(request, envelope)

    assert validated.proposals[0].start == 110
    assert validated.proposals[0].end == 117
