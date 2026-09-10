from datetime import date

import pytest

from procrun.collectors.ted import TedCollectionResult
from procrun.production_delivery import (
    ProductionDeliveryError,
    _ted_year_ranges,
    collect_complete_ted_italy,
)


def _record(notice_id: str, publication_date: str) -> dict[str, object]:
    return {"notice_id": notice_id, "publication_date": publication_date}


def test_ted_year_ranges_are_exhaustive_and_non_overlapping() -> None:
    assert _ted_year_ranges(date(2023, 2, 3)) == (
        (date(2021, 1, 1), date(2021, 12, 31)),
        (date(2022, 1, 1), date(2022, 12, 31)),
        (date(2023, 1, 1), date(2023, 2, 3)),
    )


def test_segmented_ted_collection_merges_deterministically(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[str] = []

    def fake_collect(query: str, **kwargs) -> TedCollectionResult:
        del kwargs
        calls.append(query)
        if "20210101" in query:
            records = (_record("B", "2021-12-31"), _record("A", "2021-01-01"))
        else:
            records = (_record("C", "2022-02-01"),)
        return TedCollectionResult(
            records=records,
            total_notice_count=len(records),
            pages_fetched=1,
            complete=True,
            stop_reason="complete",
        )

    monkeypatch.setattr("procrun.production_delivery.collect_ted_notices", fake_collect)
    result = collect_complete_ted_italy(date(2022, 2, 1))

    assert set(calls) == {
        "buyer-country = ITA AND publication-date >= 20210101 AND publication-date <= 20211231",
        "buyer-country = ITA AND publication-date >= 20220101 AND publication-date <= 20220201",
    }
    assert [record["notice_id"] for record in result.records] == ["A", "B", "C"]
    assert result.total_notice_count == 3
    assert result.pages_fetched == 2
    assert result.complete is True
    assert result.stop_reason == "complete_segmented"


def test_one_incomplete_segment_fails_closed(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_collect(query: str, **kwargs) -> TedCollectionResult:
        del kwargs
        incomplete = "20220101" in query
        return TedCollectionResult(
            records=(),
            total_notice_count=1 if incomplete else 0,
            pages_fetched=1,
            complete=not incomplete,
            stop_reason="missing_iteration_token" if incomplete else "complete",
        )

    monkeypatch.setattr("procrun.production_delivery.collect_ted_notices", fake_collect)
    with pytest.raises(ProductionDeliveryError, match="segment coverage is incomplete"):
        collect_complete_ted_italy(date(2022, 2, 1))


def test_segmented_merge_rejects_duplicate_record_identity(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_collect(query: str, **kwargs) -> TedCollectionResult:
        del query, kwargs
        record = _record("DUP", "2022-01-01")
        return TedCollectionResult(
            records=(record,),
            total_notice_count=1,
            pages_fetched=1,
            complete=True,
            stop_reason="complete",
        )

    monkeypatch.setattr("procrun.production_delivery.collect_ted_notices", fake_collect)
    with pytest.raises(ProductionDeliveryError, match="duplicate/overlapping"):
        collect_complete_ted_italy(date(2022, 2, 1))
