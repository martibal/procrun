from procrun.source_contracts import SOURCE_CONTRACTS, SourceStatus


def test_opencoesione_approval_is_bound_to_public_2021_2027_contract() -> None:
    contract = SOURCE_CONTRACTS["opencoesione_2021_2027_operations"]
    assert contract.status is SourceStatus.APPROVED
    assert contract.commercial_reuse_allowed is True
    assert any(
        "beneficiari_operazioni_2021_2027" in url for url in contract.legal_basis_urls
    )
    assert any("CC BY 4.0" in text for text in (contract.license_basis, contract.attribution_text or ""))
    assert any("beneficiary identity fields" in item for item in contract.obligations)


def test_ted_approval_is_bound_to_public_reuse_and_attribution() -> None:
    contract = SOURCE_CONTRACTS["ted_search_api"]
    assert contract.status is SourceStatus.APPROVED
    assert contract.server_side_projection is True
    assert contract.commercial_reuse_allowed is True
    assert any("ted.europa.eu/en/legal-notice" in url for url in contract.legal_basis_urls)
    assert contract.attribution_required is True
    assert contract.attribution_text is not None
    assert "not an official EU" in contract.attribution_text


def test_approved_sources_never_depend_on_human_permission() -> None:
    forbidden = ("permission", "contact form", "source-owner response", "legal opinion")
    for contract in SOURCE_CONTRACTS.values():
        if contract.status is not SourceStatus.APPROVED:
            continue
        combined = " ".join((contract.reason, contract.license_basis, *contract.obligations)).lower()
        assert not any(term in combined for term in forbidden)
