import json

import httpx
import pytest

from procrun.collectors.ted import (
    TED_PROJECTED_FIELDS,
    TedContractError,
    TedTransportError,
    _post_with_throttle_retry,
    canonicalize_ted_notice,
    collect_ted_notices,
)
from procrun.ingest.ted import normalize_ted_record


def notice(**extra: object) -> dict[str, object]:
    result: dict[str, object] = {
        "publication-number": "123456-2026",
        "publication-date": "2026-09-01",
        "notice-title": {"por": "Titulo PT", "eng": "English title"},
        "description-proc": {"eng": "Water infrastructure works"},
        "classification-cpv": ["45200000"],
        "contract-nature": "works",
        "procedure-type": "open",
        "estimated-value-proc": 1000,
        "estimated-value-cur-proc": "EUR",
        "place-of-performance-subdiv-proc": ["PT170"],
        "eu-funds-identifier": ["PACS-FC-X"],
        "links": {"xml": "https://example.invalid/notice.xml"},
    }
    result.update(extra)
    return result


def response(body: dict[str, object]) -> httpx.Response:
    return httpx.Response(
        200,
        json=body,
        headers={"content-type": "application/json"},
    )


def test_iteration_uses_frozen_projection_and_token() -> None:
    calls: list[dict[str, object]] = []
    pages = [
        {
            "notices": [notice()],
            "totalNoticeCount": 1,
            "iterationNextToken": "first-token",
            "timedOut": False,
        },
        {
            "notices": [],
            "totalNoticeCount": 1,
            "iterationNextToken": "completion-token",
            "timedOut": False,
        },
    ]

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(json.loads(request.content))
        return response(pages.pop(0))

    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        result = collect_ted_notices("buyer-country=PRT", client=client)

    assert result.complete
    assert result.stop_reason == "complete"
    assert result.pages_fetched == 2
    assert len(result.records) == 1
    assert calls[0]["fields"] == list(TED_PROJECTED_FIELDS)
    assert calls[0]["paginationMode"] == "ITERATION"
    assert calls[0]["checkQuerySyntax"] is False
    assert "iterationNextToken" not in calls[0]
    assert calls[1]["iterationNextToken"] == "first-token"

    unqualified_or_prohibited = {
        "buyer-name",
        "buyer-email",
        "buyer-contact-point",
        "buyer-person",
        "buyer-touchpoint-email",
        "business-email",
        "business-tel",
        "business-street",
        "place-of-performance-city-proc",
        "result-value-notice",
        "result-value-cur-notice",
    }
    assert not unqualified_or_prohibited.intersection(calls[0]["fields"])


def test_collected_record_is_compatible_with_canonical_ingest() -> None:
    canonical = canonicalize_ted_notice(notice())
    normalized = normalize_ted_record(
        canonical,
        evidence_id="ev-1",
        component_id="component-1",
    )

    assert normalized.notice_id == "123456-2026"
    assert normalized.title == "English title"
    assert normalized.contracting_authority_name is None
    assert normalized.project_reference == "PACS-FC-X"
    assert normalized.estimated_value_eur == 1000
    assert normalized.awarded_value_eur is None
    assert normalized.municipality is None
    assert normalized.place_of_performance is None


def test_unknown_response_field_fails_closed() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        del request
        return response({"notices": [], "timedOut": False, "unexpected": 1})

    with (
        httpx.Client(transport=httpx.MockTransport(handler)) as client,
        pytest.raises(TedContractError),
    ):
        collect_ted_notices("buyer-country=PRT", client=client)


def test_non_projected_notice_field_fails_closed() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        del request
        return response(
            {
                "notices": [notice(**{"buyer-name": "Authority A"})],
                "totalNoticeCount": 1,
                "iterationNextToken": "token",
                "timedOut": False,
            }
        )

    with (
        httpx.Client(transport=httpx.MockTransport(handler)) as client,
        pytest.raises(TedContractError),
    ):
        collect_ted_notices("buyer-country=PRT", client=client)


def test_timed_out_page_is_never_accepted_as_complete() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        del request
        return response(
            {
                "notices": [notice()],
                "totalNoticeCount": 1,
                "timedOut": True,
            }
        )

    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        result = collect_ted_notices("buyer-country=PRT", client=client)

    assert not result.complete
    assert result.stop_reason == "timed_out"
    assert result.records == ()


def test_max_pages_marks_coverage_incomplete() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        del request
        return response(
            {
                "notices": [notice()],
                "totalNoticeCount": 2,
                "iterationNextToken": "token",
                "timedOut": False,
            }
        )

    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        result = collect_ted_notices(
            "buyer-country=PRT",
            client=client,
            max_pages=1,
        )

    assert not result.complete
    assert result.stop_reason == "max_pages"


def test_non_eur_values_are_not_mislabeled_as_eur() -> None:
    canonical = canonicalize_ted_notice(
        notice(**{"estimated-value-cur-proc": "USD"})
    )

    assert canonical["estimated_value_eur"] is None
    assert canonical["awarded_value_eur"] is None


def test_fractional_eur_value_is_not_silently_rounded() -> None:
    canonical = canonicalize_ted_notice(
        notice(**{"estimated-value-proc": "1000.50"})
    )

    assert canonical["estimated_value_eur"] is None


def test_throttle_retry_reuses_identical_request_and_then_succeeds() -> None:
    calls: list[bytes] = []
    statuses = [429, 429, 200]

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request.content)
        status = statuses.pop(0)
        if status == 429:
            return httpx.Response(status, headers={"retry-after": "0"}, request=request)
        return httpx.Response(
            status,
            json={"notices": [], "timedOut": False},
            headers={"content-type": "application/json"},
            request=request,
        )

    sleeps: list[float] = []
    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        result = _post_with_throttle_retry(
            client, {"query": "buyer-country=ITA"}, sleep=sleeps.append
        )

    assert result.status_code == 200
    assert len(calls) == 3
    assert calls[0] == calls[1] == calls[2]
    assert sleeps == [2.0, 4.0]


def test_transient_gateway_retry_reuses_identical_request_and_then_succeeds() -> None:
    calls: list[bytes] = []
    statuses = [502, 503, 504, 200]

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request.content)
        status = statuses.pop(0)
        if status != 200:
            return httpx.Response(status, request=request)
        return httpx.Response(
            status,
            json={"notices": [], "timedOut": False},
            headers={"content-type": "application/json"},
            request=request,
        )

    sleeps: list[float] = []
    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        result = _post_with_throttle_retry(
            client, {"query": "buyer-country=ITA"}, sleep=sleeps.append
        )

    assert result.status_code == 200
    assert len(calls) == 4
    assert calls[0] == calls[1] == calls[2] == calls[3]
    assert sleeps == [2.0, 4.0, 8.0]


def test_non_transient_http_error_remains_immediate_fail_closed() -> None:
    calls = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        return httpx.Response(500, request=request)

    with (
        httpx.Client(transport=httpx.MockTransport(handler)) as client,
        pytest.raises(TedTransportError, match="HTTP request failed"),
    ):
        _post_with_throttle_retry(
            client,
            {"query": "buyer-country=ITA"},
            sleep=lambda _: None,
        )

    assert calls == 1


def test_throttle_retry_exhaustion_remains_fail_closed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import procrun.collectors.ted as ted_module

    monkeypatch.setattr(ted_module, "TED_MAX_THROTTLE_RETRIES", 2)

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(429, request=request)

    with (
        httpx.Client(transport=httpx.MockTransport(handler)) as client,
        pytest.raises(TedTransportError, match="remained unavailable"),
    ):
        _post_with_throttle_retry(
            client,
            {"query": "buyer-country=ITA"},
            sleep=lambda _: None,
        )


def test_gateway_retry_exhaustion_remains_fail_closed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import procrun.collectors.ted as ted_module

    monkeypatch.setattr(ted_module, "TED_MAX_THROTTLE_RETRIES", 2)

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(502, request=request)

    with (
        httpx.Client(transport=httpx.MockTransport(handler)) as client,
        pytest.raises(TedTransportError, match="HTTP 502"),
    ):
        _post_with_throttle_retry(
            client,
            {"query": "buyer-country=ITA"},
            sleep=lambda _: None,
        )
