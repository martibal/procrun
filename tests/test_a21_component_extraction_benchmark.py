import json

from scripts.run_a21_component_extraction_benchmark import build_report


def _case(case_number: int, scope: str, components: list[dict[str, str]]) -> dict[str, object]:
    domains = sorted({item["domain"] for item in components})
    return {
        "case_number": case_number,
        "operation_code": f"A21-{case_number}",
        "source_context": {
            "project_scope_text": scope,
            "project_title": None,
            "region": "Lombardia",
        },
        "adjudication": {
            "domains": domains,
            "components": components,
        },
    }


def test_build_report_scores_italian_storage_exactly() -> None:
    cases = [
        _case(
            1,
            "Installazione impianto fotovoltaico, sistema di accumulo e relamping.",
            [
                {"domain": "energy_efficiency", "category": "photovoltaic"},
                {"domain": "energy_efficiency", "category": "battery_storage"},
                {"domain": "energy_efficiency", "category": "lighting"},
            ],
        )
    ]
    cases.extend(
        _case(index, "Nessun componente supportato.", []) for index in range(2, 201)
    )
    document = {
        "schema_version": "a21-final-benchmark-v1",
        "engine_output_used": False,
        "case_count": 200,
        "cases": cases,
    }

    report = build_report(document, "a" * 64)

    assert report["component_rule_version"] == "component-taxonomy-v2"
    assert report["gold_component_count"] == 3
    assert report["predicted_component_count"] == 3
    assert report["true_positive"] == 3
    assert report["false_positive"] == 0
    assert report["false_negative"] == 0
    assert report["component_precision"] == 1.0
    assert report["component_recall"] == 1.0
    assert report["sealed_holdout_used"] is False


def test_runner_refuses_sealed_holdout() -> None:
    document = {
        "schema_version": "a21-final-benchmark-v1",
        "engine_output_used": False,
        "sealed": True,
        "cases": [],
    }
    try:
        build_report(document, "a" * 64)
    except ValueError as exc:
        assert "sealed holdout" in str(exc)
    else:
        raise AssertionError("sealed holdout must be rejected")


def test_fixture_is_json_serializable() -> None:
    document = {
        "schema_version": "a21-final-benchmark-v1",
        "engine_output_used": False,
        "case_count": 200,
        "cases": [_case(i, "Nessun componente supportato.", []) for i in range(1, 201)],
    }
    json.dumps(document)
