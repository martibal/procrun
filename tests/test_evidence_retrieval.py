from procrun.domain import FundingProject
from procrun.evidence_retrieval import (
    EVIDENCE_RETRIEVAL_VERSION,
    extract_source_evidence,
)


def _project(scope: str) -> FundingProject:
    return FundingProject(
        operation_code="TEST-001",
        project_scope_text=scope,
        source_url="https://example.invalid/project/TEST-001",
    )


def test_extracts_exact_original_sentence_with_offsets() -> None:
    scope = (
        "Il progetto riguarda opere di riqualificazione. "
        "È prevista una procedura di gara per la fornitura degli impianti. "
        "I lavori interesseranno il territorio comunale."
    )
    excerpts = extract_source_evidence(_project(scope))
    assert len(excerpts) == 1
    excerpt = excerpts[0]
    assert excerpt.original_text == "È prevista una procedura di gara per la fornitura degli impianti."
    assert scope[excerpt.start_offset : excerpt.end_offset] == excerpt.original_text
    assert excerpt.extractor_version == EVIDENCE_RETRIEVAL_VERSION
    assert excerpt.original_language == "it"


def test_returns_nothing_when_no_defensible_procurement_evidence_exists() -> None:
    excerpts = extract_source_evidence(
        _project("Il progetto migliora la qualità urbana e interessa diversi spazi pubblici.")
    )
    assert excerpts == ()


def test_returns_at_most_three_ranked_sentences_in_source_order() -> None:
    scope = (
        "È previsto un acquisto di apparecchiature. "
        "La procedura di gara sarà avviata successivamente. "
        "È previsto un contratto per la fornitura. "
        "L'aggiudicazione sarà documentata con successivo atto."
    )
    excerpts = extract_source_evidence(_project(scope))
    assert len(excerpts) == 3
    assert [item.start_offset for item in excerpts] == sorted(
        item.start_offset for item in excerpts
    )
    for excerpt in excerpts:
        assert scope[excerpt.start_offset : excerpt.end_offset] == excerpt.original_text


def test_translation_is_not_invented_by_retrieval_layer() -> None:
    scope = "È prevista una procedura di gara per la fornitura degli impianti."
    excerpt = extract_source_evidence(_project(scope))[0]
    assert excerpt.english_translation is None


def test_rejects_more_than_three_sentences() -> None:
    try:
        extract_source_evidence(_project("gara per fornitura."), max_sentences=4)
    except ValueError as exc:
        assert "between 1 and 3" in str(exc)
    else:
        raise AssertionError("expected max_sentences gate to reject 4")
