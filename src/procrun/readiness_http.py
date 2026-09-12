"""Minimal server-to-server JSON API for Readiness Dossier v2.

The endpoint is intentionally an internal backend surface. A future visual interface calls this
through its authenticated server layer; calculations remain in Python as the single source of truth.
"""

from __future__ import annotations

import json
import os
import time
from datetime import UTC, datetime
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse
from uuid import uuid4

import psycopg

from procrun.migrations import apply_all_migrations
from procrun.readiness_application import (
    ReadinessNotFoundError,
    create_and_persist_dossier,
    preview_by_bando,
)
from procrun.readiness_dossier import DossierBlockedError
from procrun.readiness_matrix import AdvisorConfirmation, AdvisorState
from procrun.readiness_purchase import (
    PurchaseCapabilityError,
    PurchaseScope,
    verify_purchase_capability,
)


def _database_url() -> str:
    value = os.environ.get("PROCRUN_DATABASE_URL", "").strip()
    if not value:
        raise RuntimeError("PROCRUN_DATABASE_URL is required")
    return value


def _api_token() -> str:
    value = os.environ.get("PROCRUN_READINESS_API_TOKEN", "").strip()
    if not value:
        raise RuntimeError("PROCRUN_READINESS_API_TOKEN is required")
    return value


def _purchase_secret() -> str:
    value = os.environ.get("PROCRUN_PURCHASE_CAPABILITY_SECRET", "").strip()
    if len(value) < 32:
        raise RuntimeError("PROCRUN_PURCHASE_CAPABILITY_SECRET must be at least 32 characters")
    return value


class ReadinessHandler(BaseHTTPRequestHandler):
    server_version = "ProcRunReadiness/2"

    def _json(self, status: HTTPStatus, payload: dict[str, object]) -> None:
        body = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        self.send_response(status.value)
        self.send_header("content-type", "application/json; charset=utf-8")
        self.send_header("content-length", str(len(body)))
        self.send_header("cache-control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _authorized(self) -> bool:
        expected = _api_token()
        actual = self.headers.get("authorization", "")
        return actual == f"Bearer {expected}"

    def _require_auth(self) -> bool:
        if self._authorized():
            return True
        self._json(HTTPStatus.UNAUTHORIZED, {"error": "unauthorized"})
        return False

    def do_GET(self) -> None:  # noqa: N802
        if not self._require_auth():
            return
        parsed = urlparse(self.path)
        if parsed.path != "/v1/readiness/preview":
            self._json(HTTPStatus.NOT_FOUND, {"error": "not_found"})
            return
        query = parse_qs(parsed.query)
        bando_code = query.get("bando_code", [""])[0]
        snapshot_id = query.get("snapshot_id", [""])[0]
        if not bando_code or not snapshot_id:
            self._json(HTTPStatus.BAD_REQUEST, {"error": "bando_code_and_snapshot_id_required"})
            return
        try:
            with psycopg.connect(_database_url()) as conn:
                result = preview_by_bando(
                    conn,
                    bando_code=bando_code,
                    benchmark_snapshot_id=snapshot_id,
                    as_of=datetime.now(UTC),
                )
            self._json(
                HTTPStatus.OK,
                {
                    "analysis_available": result.analysis_available,
                    "source_state": result.source_state.value,
                    "historical_reference": result.historical_reference,
                    "customer_message": result.customer_message,
                },
            )
        except ReadinessNotFoundError as exc:
            self._json(HTTPStatus.NOT_FOUND, {"error": str(exc)})

    def do_POST(self) -> None:  # noqa: N802
        if not self._require_auth():
            return
        parsed = urlparse(self.path)
        if parsed.path != "/v1/readiness/dossiers":
            self._json(HTTPStatus.NOT_FOUND, {"error": "not_found"})
            return
        try:
            length = int(self.headers.get("content-length", "0"))
            raw = self.rfile.read(length)
            body = json.loads(raw.decode("utf-8"))
            confirmations = tuple(
                AdvisorConfirmation(
                    requirement_id=str(item["requirement_id"]),
                    state=AdvisorState(str(item["state"])),
                )
                for item in body.get("confirmations", [])
            )
            proposed_duration_raw = body.get("proposed_duration_months")
            proposed_duration = (
                None if proposed_duration_raw is None else int(proposed_duration_raw)
            )
            scope = PurchaseScope(
                tenant_key=str(body["tenant_key"]),
                purchase_reference=str(body["purchase_reference"]),
                bando_code=str(body["bando_code"]),
                benchmark_snapshot_id=str(body["benchmark_snapshot_id"]),
                proposed_funding_eur=int(body["proposed_funding_eur"]),
                proposed_duration_months=proposed_duration,
                expires_unix=int(body["purchase_expires_unix"]),
            )
            verify_purchase_capability(
                scope,
                str(body["purchase_authorization"]),
                _purchase_secret(),
                now_unix=int(time.time()),
            )
            with psycopg.connect(_database_url()) as conn:
                payload, digest = create_and_persist_dossier(
                    conn,
                    dossier_id=str(uuid4()),
                    tenant_key=scope.tenant_key,
                    purchase_reference=scope.purchase_reference,
                    bando_code=scope.bando_code,
                    benchmark_snapshot_id=scope.benchmark_snapshot_id,
                    proposed_funding_eur=scope.proposed_funding_eur,
                    proposed_duration_months=scope.proposed_duration_months,
                    confirmations=confirmations,
                    created_at=datetime.now(UTC),
                )
            self._json(
                HTTPStatus.CREATED,
                {
                    "dossier_id": payload["dossier_id"],
                    "canonical_sha256": digest,
                    "payload": payload,
                },
            )
        except PurchaseCapabilityError as exc:
            self._json(HTTPStatus.PAYMENT_REQUIRED, {"error": str(exc)})
        except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
            self._json(HTTPStatus.BAD_REQUEST, {"error": str(exc)})
        except ReadinessNotFoundError as exc:
            self._json(HTTPStatus.NOT_FOUND, {"error": str(exc)})
        except DossierBlockedError as exc:
            self._json(HTTPStatus.CONFLICT, {"error": str(exc)})

    def log_message(self, format: str, *args: object) -> None:
        return


def main() -> None:
    host = os.environ.get("PROCRUN_READINESS_HOST", "127.0.0.1")
    port = int(os.environ.get("PROCRUN_READINESS_PORT", "8091"))
    with psycopg.connect(_database_url()) as conn:
        apply_all_migrations(conn)
    server = ThreadingHTTPServer((host, port), ReadinessHandler)
    server.serve_forever()


if __name__ == "__main__":
    main()
