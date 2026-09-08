from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_market_intelligence_uses_production_ledgers_not_fixture_read_model() -> None:
    page = (REPO_ROOT / "web/app/app/market/page.tsx").read_text(encoding="utf-8")
    source = (REPO_ROOT / "web/lib/market-needs.ts").read_text(encoding="utf-8")

    assert "opportunities" not in page
    assert "loadMarketOverview()" in page
    assert "loadMarketTrend()" in page
    assert "procrun.assessment_versions" in source
    assert "current_assessment" in source
    assert "procurement_observations" not in source


def test_market_intelligence_discloses_missingness_and_scope() -> None:
    page = (REPO_ROOT / "web/app/app/market/page.tsx").read_text(encoding="utf-8")
    source = (REPO_ROOT / "web/lib/market-needs.ts").read_text(encoding="utf-8")

    assert "Metadata completeness" in page
    assert "Missing values are excluded only where a measure requires that field" in page
    assert "missingProgrammeProjects" in page
    assert "missingFundingProjects" in page
    assert "missingRegionProjects" in page
    assert "programme IS NULL" in source
    assert "approved_funding_eur IS NULL" in source
    assert "region IS NULL" in source
    assert "TED only for MVP negative search." in page
    assert "PR FESR Lombardia 2021–2027" in page


def test_market_trend_reconstructs_historical_state_snapshots() -> None:
    source = (REPO_ROOT / "web/lib/market-needs.ts").read_text(encoding="utf-8")
    page = (REPO_ROOT / "web/app/app/market/page.tsx").read_text(encoding="utf-8")

    assert "LIMIT 30" in source
    assert "assessment_versions.cutoff_date <= recent_dates.cutoff_date" in source
    assert "PARTITION BY recent_dates.cutoff_date, assessment_versions.component_id" in source
    assert "snapshot_rank = 1" in source
    assert "latest 30 published cutoff dates" in page
    assert "Later revisions do not overwrite earlier snapshots." in page
