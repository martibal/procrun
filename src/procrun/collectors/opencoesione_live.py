"""Production transport for the approved OpenCoesione 2021-2027 operation-list route.

The OpenCoesione site may require a normal same-site session before serving the
public ZIP to automated infrastructure.  This module performs only two GETs on
the already-approved public origin: the publication landing page, followed by
the frozen Lombardia ZIP route.  It does not broaden the source contract or
admit any additional fields.
"""

from __future__ import annotations

from typing import Final
from urllib.parse import urlparse

import httpx

from procrun.collectors.opencoesione import (
    OPENCOESIONE_PROGRAM_URL,
    OPENCOESIONE_SOURCE_ID,
    OpenCoesioneBatch,
    OpenCoesioneSchemaError,
    parse_operation_list_zip,
)
from procrun.source_contracts import require_live_source

OPENCOESIONE_PUBLICATION_PAGE: Final = (
    "https://opencoesione.gov.it/it/beneficiari_operazioni_2021_2027/"
)

_BROWSER_HEADERS: Final[dict[str, str]] = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9,it;q=0.8",
}


def _same_origin(url: str) -> bool:
    parsed = urlparse(url)
    return parsed.scheme == "https" and parsed.hostname == "opencoesione.gov.it"


def _validate_zip_final_url(url: str) -> None:
    expected = urlparse(OPENCOESIONE_PROGRAM_URL)
    actual = urlparse(url)
    if (actual.scheme, actual.hostname, actual.path) != (
        expected.scheme,
        expected.hostname,
        expected.path,
    ):
        raise OpenCoesioneSchemaError(
            f"approved source redirected outside frozen route: {url}"
        )


def collect_open_coesione_live(
    *, client: httpx.Client | None = None, timeout_seconds: float = 60.0
) -> OpenCoesioneBatch:
    """Fetch through a same-site session and fail closed before row admission."""
    contract = require_live_source(OPENCOESIONE_SOURCE_ID)
    if OPENCOESIONE_PROGRAM_URL not in contract.retrieval_route:
        raise OpenCoesioneSchemaError("runtime source contract does not pin the pilot route")

    owns_client = client is None
    active_client = client or httpx.Client(
        timeout=timeout_seconds,
        follow_redirects=True,
        headers=_BROWSER_HEADERS,
    )
    try:
        landing = active_client.get(
            OPENCOESIONE_PUBLICATION_PAGE,
            headers={"Accept": "text/html,application/xhtml+xml"},
        )
        landing.raise_for_status()
        if not _same_origin(str(landing.url)):
            raise OpenCoesioneSchemaError(
                f"publication page redirected outside approved origin: {landing.url}"
            )

        response = active_client.get(
            OPENCOESIONE_PROGRAM_URL,
            headers={
                "Accept": "application/zip,application/octet-stream;q=0.9,*/*;q=0.1",
                "Referer": OPENCOESIONE_PUBLICATION_PAGE,
            },
        )
        response.raise_for_status()
        _validate_zip_final_url(str(response.url))
        content_type = response.headers.get("content-type", "").lower()
        if not any(token in content_type for token in ("zip", "octet-stream")):
            raise OpenCoesioneSchemaError(
                f"unexpected content type for approved ZIP route: {content_type or '<missing>'}"
            )
        if not response.content:
            raise OpenCoesioneSchemaError("approved ZIP route returned an empty response")
        return parse_operation_list_zip(response.content, source_url=str(response.url))
    finally:
        if owns_client:
            active_client.close()
