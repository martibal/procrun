from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_customer_project_projection_excludes_municipality() -> None:
    projection = (REPO_ROOT / "web/lib/production-projects.ts").read_text(encoding="utf-8")
    project_list = (REPO_ROOT / "web/app/app/page.tsx").read_text(encoding="utf-8")
    project_detail = (REPO_ROOT / "web/app/app/projects/[id]/page.tsx").read_text(encoding="utf-8")

    assert "municipality" not in projection
    assert "municipality" not in project_list
    assert "municipality" not in project_detail


def test_customer_category_baselines_fail_closed_below_twenty() -> None:
    source = (REPO_ROOT / "web/lib/category-baselines.ts").read_text(encoding="utf-8")

    assert "MIN_CATEGORY_BASELINE_N = 20" in source
    assert "HAVING count(*) >= ${MIN_CATEGORY_BASELINE_N}" in source
    assert "durations.length < MIN_CATEGORY_BASELINE_N" in source


def test_market_copy_discloses_minimum_baseline_sample() -> None:
    page = (REPO_ROOT / "web/app/app/market/page.tsx").read_text(encoding="utf-8")

    assert "at least 20 completed comparable lifecycles" in page
    assert "n ≥ 20" in page
