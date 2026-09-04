"""Runtime transport for the approved OpenCoesione operation-list source.

GitHub-hosted runners are blocked by the publisher at the network layer. Production therefore uses
an isolated authenticated relay whose only upstream target is the already-approved frozen source URL.
The relay is transport infrastructure, not a new data source. This client verifies source identity,
payload digest and ZIP shape before handing bytes to the existing fail-closed parser.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from urllib.parse import urlparse

import httpx

from procrun.collectors.opencoesione import (
    OPENCOESIONE_PROGRAM_URL,
    OpenCoesioneBatch,
    OpenCoesioneSchemaError,
    parse_operation_list_zip,
)
from procrun.source_contracts import require_live_source

OPENCOESIONE_SOURCE_ID = "opencoesione_2021_2027_operations"
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


class OpenCoesioneRelayError(RuntimeError):
    """Raised when relay transport cannot prove it returned the frozen source payload."""


@dataclass(frozen=True)
class OpenCoesioneRelayConfig:
    url: str
    bearer_token: str

    def __post_init__(self) -> None:
        parsed = urlparse(self.url)
        if parsed.scheme != "https" or not parsed.hostname:
            raise ValueError("OpenCoesione relay URL must be HTTPS")
        if not self.bearer_token.strip():
            raise ValueError("OpenCoesione relay bearer token must not be blank")


def collect_open_coesione_via_relay(
    config: OpenCoesioneRelayConfig,
    *,
    client: httpx.Client | None = None,
    timeout_seconds: float = 90.0,
) -> OpenCoesioneBatch:
    """Fetch the approved payload through isolated transport and reuse the frozen parser."""

    require_live_source(OPENCOESIONE_SOURCE_ID)
    owns_client = client is None
    http = client or httpx.Client(timeout=timeout_seconds, follow_redirects=False)
    try:
        try:
            response = http.get(
                config.url,
                headers={
                    "Authorization": f"Bearer {config.bearer_token}",
                    "Accept": "application/zip",
                    "User-Agent": "ProcRun/0.1 collector-runtime",
                },
            )
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise OpenCoesioneRelayError("OpenCoesione relay HTTP request failed") from exc

        if response.is_redirect:
            raise OpenCoesioneRelayError("OpenCoesione relay redirects are prohibited")
        source_url = response.headers.get("x-procrun-source-url")
        if source_url != OPENCOESIONE_PROGRAM_URL:
            raise OpenCoesioneRelayError("relay did not attest the exact approved source URL")

        content_type = response.headers.get("content-type", "").lower()
        if "application/zip" not in content_type:
            raise OpenCoesioneRelayError("relay returned a non-ZIP content type")
        payload = response.content
        if not payload.startswith(b"PK"):
            raise OpenCoesioneRelayError("relay response is not a ZIP payload")

        claimed_digest = response.headers.get("x-procrun-source-sha256", "").lower()
        if not _SHA256_RE.fullmatch(claimed_digest):
            raise OpenCoesioneRelayError("relay omitted a valid source SHA-256 attestation")
        actual_digest = hashlib.sha256(payload).hexdigest()
        if actual_digest != claimed_digest:
            raise OpenCoesioneRelayError("relay source SHA-256 attestation does not match payload")

        try:
            batch = parse_operation_list_zip(payload, source_url=OPENCOESIONE_PROGRAM_URL)
        except OpenCoesioneSchemaError:
            raise
        if batch.source_sha256 != actual_digest:
            raise OpenCoesioneRelayError("parser provenance hash differs from relay payload hash")
        return batch
    finally:
        if owns_client:
            http.close()
