import httpx

import procrun.collectors.ted as ted_module
from procrun.collectors.ted import _post_with_throttle_retry


def test_live_request_pacing_is_applied_before_transport(monkeypatch) -> None:
    paced = {"count": 0}

    def mark_paced() -> None:
        paced["count"] += 1

    monkeypatch.setattr(ted_module, "_pace_live_request", mark_paced)

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={"notices": [], "timedOut": False},
            headers={"content-type": "application/json"},
            request=request,
        )

    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        response = _post_with_throttle_retry(
            client,
            {"query": "buyer-country=ITA"},
            sleep=lambda _: None,
            pace_live=True,
        )

    assert response.status_code == 200
    assert paced["count"] == 1
