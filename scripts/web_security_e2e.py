#!/usr/bin/env python3
"""Remote fail-closed security smoke test for a deployed ProcRun web build.

Set PROCRUN_E2E_BASE_URL to the deployment origin, for example
https://example.com. This script uses only the Python standard library and
performs no authenticated mutation.
"""

from __future__ import annotations

import os
import sys
from urllib.error import HTTPError
from urllib.parse import urljoin
from urllib.request import HTTPRedirectHandler, Request, build_opener


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):  # type: ignore[override]
        return None


def request(path: str, *, method: str = "GET", data: bytes | None = None):
    base = os.environ.get("PROCRUN_E2E_BASE_URL", "").strip().rstrip("/")
    if not base:
        raise RuntimeError("PROCRUN_E2E_BASE_URL is required")

    target = urljoin(base + "/", path.lstrip("/"))
    opener = build_opener(NoRedirect)
    req = Request(target, data=data, method=method)
    try:
        return opener.open(req, timeout=20)
    except HTTPError as exc:
        return exc


def require_header(response, name: str, expected: str) -> None:
    actual = response.headers.get(name)
    if actual != expected:
        raise AssertionError(f"{name}: expected {expected!r}, got {actual!r}")


def main() -> int:
    public = request("/")
    if public.status != 200:
        raise AssertionError(f"public homepage returned {public.status}")
    require_header(public, "X-Content-Type-Options", "nosniff")
    require_header(public, "X-Frame-Options", "DENY")
    require_header(public, "Referrer-Policy", "strict-origin-when-cross-origin")

    workspace = request("/app")
    if workspace.status not in {302, 303, 307, 308}:
        raise AssertionError(f"unauthenticated /app did not redirect: {workspace.status}")
    location = workspace.headers.get("Location", "")
    if "/login" not in location and "clerk" not in location.casefold():
        raise AssertionError(f"unauthenticated /app redirect was unexpected: {location!r}")
    require_header(workspace, "X-Content-Type-Options", "nosniff")
    require_header(workspace, "X-Frame-Options", "DENY")

    webhook = request(
        "/api/stripe/webhook",
        method="POST",
        data=b'{"type":"checkout.session.completed"}',
    )
    if webhook.status == 200:
        raise AssertionError("unsigned Stripe webhook was accepted")
    if webhook.status != 400:
        raise AssertionError(f"unsigned Stripe webhook returned {webhook.status}, expected 400")

    print("ProcRun remote security smoke: PASS")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ProcRun remote security smoke: FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1) from None
