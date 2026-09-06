"""Production transport and bounded cache for the approved OpenCoesione Lombardia route."""

from __future__ import annotations

import json
import os
import tempfile
from datetime import date, datetime, timezone
from decimal import Decimal
from pathlib import Path
from typing import Any, Final
from urllib.parse import urlparse

import httpx

from procrun.collectors.opencoesione import (
    OPENCOESIONE_PROGRAM_URL,
    OPENCOESIONE_SOURCE_ID,
    OpenCoesioneBatch,
    OpenCoesioneOperation,
    OpenCoesioneSchemaError,
    parse_operation_list_zip,
)
from procrun.source_contracts import require_live_source

OPENCOESIONE_PUBLICATION_PAGE: Final = (
    "https://opencoesione.gov.it/it/beneficiari_operazioni_2021_2027/"
)
OPENCOESIONE_CANONICAL_ZIP_URL: Final = (
    "https://opencoesione.gov.it/media/open_data/beneficiari/2021-2027/"
    "beneficiari_PR_FESR_LOMBARDIA.zip"
)
DEFAULT_CACHE_PATH: Final = Path("/var/lib/procrun/cache/opencoesione-lombardia.json")
CACHE_VERSION: Final = "opencoesione-admitted-cache-v1"

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


def _route_identity(url: str) -> tuple[str, str | None, str]:
    parsed = urlparse(url)
    return parsed.scheme, parsed.hostname, parsed.path


def _validate_zip_final_url(url: str) -> None:
    allowed_final_routes = {
        _route_identity(OPENCOESIONE_PROGRAM_URL),
        _route_identity(OPENCOESIONE_CANONICAL_ZIP_URL),
    }
    if _route_identity(url) not in allowed_final_routes:
        raise OpenCoesioneSchemaError(
            f"approved source redirected outside frozen route: {url}"
        )


def _fetch_network(
    *, client: httpx.Client | None = None, timeout_seconds: float = 60.0
) -> OpenCoesioneBatch:
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


def _operation_payload(operation: OpenCoesioneOperation) -> dict[str, Any]:
    return {
        "operation_id": operation.operation_id,
        "cup": operation.cup,
        "operation_name": operation.operation_name,
        "operation_summary": operation.operation_summary,
        "start_date": operation.start_date.isoformat() if operation.start_date else None,
        "end_date": operation.end_date.isoformat() if operation.end_date else None,
        "total_cost_eur": str(operation.total_cost_eur) if operation.total_cost_eur is not None else None,
        "eligible_expenditure_eur": str(operation.eligible_expenditure_eur) if operation.eligible_expenditure_eur is not None else None,
        "eu_cofinancing_rate": str(operation.eu_cofinancing_rate) if operation.eu_cofinancing_rate is not None else None,
        "fund": operation.fund,
        "specific_objective": operation.specific_objective,
        "postcode": operation.postcode,
        "country": operation.country,
        "intervention_category": operation.intervention_category,
        "list_updated_on": operation.list_updated_on.isoformat(),
        "source_url": operation.source_url,
    }


def write_open_coesione_cache(batch: OpenCoesioneBatch, path: Path) -> None:
    """Persist only already-admitted, non-beneficiary fields for reuse between source releases."""

    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "cache_version": CACHE_VERSION,
        "observed_at": batch.observed_at.astimezone(timezone.utc).isoformat(),
        "source_url": batch.source_url,
        "source_sha256": batch.source_sha256,
        "list_updated_on": batch.list_updated_on.isoformat(),
        "operations": [_operation_payload(item) for item in batch.operations],
    }
    text = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", dir=path.parent, delete=False, prefix=f".{path.name}."
    ) as handle:
        handle.write(text)
        handle.flush()
        os.fsync(handle.fileno())
        temp_path = Path(handle.name)
    temp_path.replace(path)


def load_open_coesione_cache(path: Path) -> OpenCoesioneBatch:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if raw.get("cache_version") != CACHE_VERSION:
        raise OpenCoesioneSchemaError("OpenCoesione cache version is not approved")
    source_url = str(raw["source_url"])
    _validate_zip_final_url(source_url)
    operations = tuple(
        OpenCoesioneOperation(
            operation_id=str(item["operation_id"]),
            cup=item["cup"],
            operation_name=str(item["operation_name"]),
            operation_summary=str(item["operation_summary"]),
            start_date=date.fromisoformat(item["start_date"]) if item["start_date"] else None,
            end_date=date.fromisoformat(item["end_date"]) if item["end_date"] else None,
            total_cost_eur=Decimal(item["total_cost_eur"]) if item["total_cost_eur"] else None,
            eligible_expenditure_eur=Decimal(item["eligible_expenditure_eur"]) if item["eligible_expenditure_eur"] else None,
            eu_cofinancing_rate=Decimal(item["eu_cofinancing_rate"]) if item["eu_cofinancing_rate"] else None,
            fund=item["fund"],
            specific_objective=item["specific_objective"],
            postcode=item["postcode"],
            country=item["country"],
            intervention_category=item["intervention_category"],
            list_updated_on=date.fromisoformat(item["list_updated_on"]),
            source_url=str(item["source_url"]),
        )
        for item in raw["operations"]
    )
    if not operations:
        raise OpenCoesioneSchemaError("OpenCoesione cache contains no admitted operations")
    return OpenCoesioneBatch(
        operations=operations,
        observed_at=datetime.fromisoformat(str(raw["observed_at"])),
        source_url=source_url,
        source_sha256=str(raw["source_sha256"]),
        list_updated_on=date.fromisoformat(str(raw["list_updated_on"])),
    )


def refresh_open_coesione_cache(
    *,
    cache_path: Path | None = None,
    client: httpx.Client | None = None,
    timeout_seconds: float = 60.0,
) -> OpenCoesioneBatch:
    path = cache_path or Path(os.environ.get("PROCRUN_OPENCOESIONE_CACHE", DEFAULT_CACHE_PATH))
    batch = _fetch_network(client=client, timeout_seconds=timeout_seconds)
    write_open_coesione_cache(batch, path)
    return batch


def collect_open_coesione_live(
    *,
    client: httpx.Client | None = None,
    timeout_seconds: float = 60.0,
    cache_path: Path | None = None,
) -> OpenCoesioneBatch:
    """Use the bimonthly admitted cache; bootstrap it once if it does not yet exist."""

    if client is not None:
        return _fetch_network(client=client, timeout_seconds=timeout_seconds)
    path = cache_path or Path(os.environ.get("PROCRUN_OPENCOESIONE_CACHE", DEFAULT_CACHE_PATH))
    if path.exists():
        return load_open_coesione_cache(path)
    return refresh_open_coesione_cache(cache_path=path, timeout_seconds=timeout_seconds)
