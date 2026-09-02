from pathlib import Path

from procrun.model_benchmark import benchmark_request, load_component_benchmark

REPO_ROOT = Path(__file__).resolve().parents[1]
PRIMARY = REPO_ROOT / "tests" / "fixtures" / "component_benchmark_v1.json"
HOLDOUT = REPO_ROOT / "tests" / "fixtures" / "component_benchmark_holdout_v1.json"


def test_holdout_corpus_is_valid_and_disjoint_from_primary_fixture() -> None:
    primary = load_component_benchmark(PRIMARY).corpus
    holdout = load_component_benchmark(HOLDOUT).corpus

    primary_case_ids = {case.case_id for case in primary.cases}
    holdout_case_ids = {case.case_id for case in holdout.cases}
    primary_operation_codes = {case.operation_code for case in primary.cases}
    holdout_operation_codes = {case.operation_code for case in holdout.cases}

    assert len(holdout.cases) == 12
    assert sum(bool(case.expected_proposals) for case in holdout.cases) == 10
    assert sum(not case.expected_proposals for case in holdout.cases) == 2
    assert primary_case_ids.isdisjoint(holdout_case_ids)
    assert primary_operation_codes.isdisjoint(holdout_operation_codes)


def test_holdout_requests_include_frozen_category_selection_rules() -> None:
    holdout = load_component_benchmark(HOLDOUT).corpus

    for case in holdout.cases:
        request = benchmark_request(case)
        assert request.allowed_categories
        assert all(item.selection_rule.strip() for item in request.allowed_categories)
