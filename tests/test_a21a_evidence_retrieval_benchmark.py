from __future__ import annotations

from scripts.run_a21a_evidence_retrieval_benchmark import build_report


def _case(case_id: str, operation_code: str, text: str, excerpts: list[dict[str, object]]):
    return {
        "case_id": case_id,
        "operation_code": operation_code,
        "source": {
            "project_scope_text": text,
            "source_url": f"https://example.test/{operation_code}",
            "language": "it",
        },
        "adjudication": {"relevant_excerpts": excerpts},
    }


def _span(text: str, fragment: str) -> dict[str, object]:
    start = text.index(fragment)
    return {"start_offset": start, "end_offset": start + len(fragment), "text": fragment}


def _document(cases: list[dict[str, object]]) -> dict[str, object]:
    return {
        "schema_version": "a21a-evidence-benchmark-v1",
        "sealed": False,
        "engine_output_used_for_gold": False,
        "pii_review_status": "ZERO_PII_CONFIRMED",
        "cases": cases,
    }


def test_reports_relevance_and_exact_source_integrity() -> None:
    text = (
        "Il progetto riguarda il miglioramento della rete locale. "
        "È prevista una procedura di gara per la fornitura delle apparecchiature. "
        "I lavori saranno completati entro il 2027."
    )
    relevant = "È prevista una procedura di gara per la fornitura delle apparecchiature."
    report = build_report(
        _document([_case("c1", "OP-1", text, [_span(text, relevant)])]), "abc"
    )

    assert report["hard_integrity_pass"] is True
    assert report["gold_positive_case_recall"] == 1.0
    assert report["gold_excerpt_recall"] == 1.0
    assert report["evidence_precision"] == 1.0
    assert report["exact_span_integrity_failures"] == 0
    assert report["provenance_failures"] == 0
    assert report["translation_violations"] == 0
    assert report["determinism_failures"] == 0
    assert report["threshold_gate_evaluated"] is False


def test_negative_case_measures_false_positive_without_declaring_go() -> None:
    text = "Il progetto riguarda esclusivamente attività di ricerca e monitoraggio ambientale."
    report = build_report(_document([_case("c2", "OP-2", text, [])]), "abc")

    assert report["gold_negative_case_count"] == 1
    assert report["gold_negative_cases_with_prediction"] == 0
    assert report["negative_case_false_positive_rate"] == 0.0
    assert report["threshold_gate_evaluated"] is False


def test_refuses_sealed_holdout() -> None:
    document = _document([_case("c3", "OP-3", "Testo senza gara.", [])])
    document["sealed"] = True

    try:
        build_report(document, "abc")
    except ValueError as exc:
        assert "sealed" in str(exc)
    else:
        raise AssertionError("sealed holdout should be rejected")


def test_refuses_non_exact_gold_span() -> None:
    text = "È prevista una gara pubblica."
    bad = {"start_offset": 0, "end_offset": 5, "text": "wrong"}

    try:
        build_report(_document([_case("c4", "OP-4", text, [bad])]), "abc")
    except ValueError as exc:
        assert "exact source span" in str(exc)
    else:
        raise AssertionError("non-exact gold span should be rejected")


def test_refuses_benchmark_without_zero_pii_confirmation() -> None:
    document = _document([_case("c5", "OP-5", "Testo.", [])])
    document["pii_review_status"] = "UNKNOWN"

    try:
        build_report(document, "abc")
    except ValueError as exc:
        assert "ZERO_PII_CONFIRMED" in str(exc)
    else:
        raise AssertionError("benchmark without zero-PII confirmation should be rejected")
