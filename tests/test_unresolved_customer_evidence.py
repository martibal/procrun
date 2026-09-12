from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_unresolved_customer_view_shows_verbatim_project_source_text() -> None:
    page = (REPO_ROOT / "web/app/app/projects/[id]/page.tsx").read_text(encoding="utf-8")
    projection = (REPO_ROOT / "web/lib/production-projects.ts").read_text(encoding="utf-8")

    assert 'const unresolvedComponents = project.components.filter((item) => item.state === "UNRESOLVED")' in page
    assert "Withheld candidate needs" in page
    assert "Why unresolved" in page
    assert "Project source text" in page
    assert "unresolvedComponents.map((item) =>" in page
    assert "{item.scopeEvidence}" in page
    assert "shown verbatim from the admitted evidence" in page
    assert "It is not a generated explanation or a reason code." in page
    assert "scopeEvidence: string" in projection


def test_unresolved_rows_remain_withheld_from_standard_opportunity_feed() -> None:
    page = (REPO_ROOT / "web/app/app/page.tsx").read_text(encoding="utf-8")
    browser = (REPO_ROOT / "web/components/project-browser.tsx").read_text(encoding="utf-8")

    assert "project.openCount > 0" in page
    assert 'filter((item) => item.state === "OPEN")' in browser
    assert "ProcRun does not present unresolved candidate needs" in page
