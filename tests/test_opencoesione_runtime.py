import hashlib
import zipfile
from io import BytesIO

import httpx
import pytest

from procrun.collectors.opencoesione import (
    EXPECTED_HEADERS,
    OPENCOESIONE_PROGRAM_URL,
    OpenCoesioneSchemaError,
)
from procrun.opencoesione_runtime import (
    OpenCoesioneRelayConfig,
    OpenCoesioneRelayError,
    collect_open_coesione_via_relay,
)

RELAY_URL = "https://collector.example.test/opencoesione"
TOKEN = "test-secret-token"


def _row() -> list[str]:
    return [
        "FESR",
        "OBJ",
        "OP-1",
        "CUP1",
        "LEGAL123",
        "Comune X",
        "Water upgrade",
        "New pumps and controls",
        "2026-01-01",
        "2027-12-31",
        "1000000",
        "800000",
        "0.6",
        "00100",
        "IT",
        "Water",
        "2026-08-31",
    ]


def _zip(headers: tuple[str, ...] = EXPECTED_HEADERS) -> bytes:
    out = BytesIO()
    text = ";".join(headers) + "\n" + ";".join(_row()) + "\n"
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("beneficiari_2021-2027.csv", text.encode())
    return out.getvalue()


def _client(
    payload: bytes,
    *,
    status: int = 200,
    source_url: str = OPENCOESIONE_PROGRAM_URL,
    content_type: str = "application/zip",
    digest: str | None = None,
    location: str | None = None,
) -> httpx.Client:
    digest = digest if digest is not None else hashlib.sha256(payload).hexdigest()

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers["authorization"] == f"Bearer {TOKEN}"
        headers = {
            "content-type": content_type,
            "x-procrun-source-url": source_url,
            "x-procrun-source-sha256": digest,
        }
        if location is not None:
            headers["location"] = location
        return httpx.Response(status, headers=headers, content=payload, request=request)

    return httpx.Client(transport=httpx.MockTransport(handler), follow_redirects=False)


def _config() -> OpenCoesioneRelayConfig:
    return OpenCoesioneRelayConfig(RELAY_URL, TOKEN)


def test_valid_relay_payload_reuses_frozen_parser_and_provenance() -> None:
    payload = _zip()
    with _client(payload) as client:
        batch = collect_open_coesione_via_relay(_config(), client=client)
    assert len(batch.operations) == 1
    assert batch.source_url == OPENCOESIONE_PROGRAM_URL
    assert batch.source_sha256 == hashlib.sha256(payload).hexdigest()
    assert batch.operations[0].operation_id == "OP-1"


def test_wrong_source_attestation_fails_closed() -> None:
    payload = _zip()
    with _client(payload, source_url="https://example.test/wrong.zip") as client:
        with pytest.raises(OpenCoesioneRelayError, match="exact approved source URL"):
            collect_open_coesione_via_relay(_config(), client=client)


def test_redirect_fails_without_following() -> None:
    payload = _zip()
    with _client(payload, status=302, location="https://example.test/redirect") as client:
        with pytest.raises(OpenCoesioneRelayError, match="HTTP request failed"):
            collect_open_coesione_via_relay(_config(), client=client)


def test_wrong_content_type_fails_closed() -> None:
    payload = _zip()
    with _client(payload, content_type="text/html") as client:
        with pytest.raises(OpenCoesioneRelayError, match="non-ZIP"):
            collect_open_coesione_via_relay(_config(), client=client)


def test_invalid_digest_attestation_fails_closed() -> None:
    payload = _zip()
    with _client(payload, digest="not-a-digest") as client:
        with pytest.raises(OpenCoesioneRelayError, match="valid source SHA-256"):
            collect_open_coesione_via_relay(_config(), client=client)


def test_digest_mismatch_fails_closed() -> None:
    payload = _zip()
    with _client(payload, digest="0" * 64) as client:
        with pytest.raises(OpenCoesioneRelayError, match="does not match"):
            collect_open_coesione_via_relay(_config(), client=client)


def test_schema_drift_still_fails_in_existing_parser() -> None:
    payload = _zip(EXPECTED_HEADERS[:-1])
    with _client(payload) as client:
        with pytest.raises(OpenCoesioneSchemaError):
            collect_open_coesione_via_relay(_config(), client=client)


def test_secret_never_appears_in_transport_error() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(503, request=request)

    client = httpx.Client(transport=httpx.MockTransport(handler))
    try:
        with pytest.raises(OpenCoesioneRelayError) as exc:
            collect_open_coesione_via_relay(_config(), client=client)
        assert TOKEN not in str(exc.value)
    finally:
        client.close()


def test_relay_configuration_requires_https_and_nonblank_token() -> None:
    with pytest.raises(ValueError, match="HTTPS"):
        OpenCoesioneRelayConfig("http://collector.example.test/x", TOKEN)
    with pytest.raises(ValueError, match="must not be blank"):
        OpenCoesioneRelayConfig(RELAY_URL, " ")
