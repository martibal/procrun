#!/usr/bin/env python3
"""Metadata-only capability probe for the public OpenCoesione API.

The probe must never request project rows. It is restricted to API root/documentation
and OPTIONS-style metadata needed to determine whether a server-side field projection
mechanism exists before any row-level qualification is considered.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request

ROOT_URLS = (
    "https://opencoesione.gov.it/api/",
    "https://www.opencoesione.gov.it/api/",
)
PROJECT_URLS = (
    "https://opencoesione.gov.it/api/progetti/",
    "https://www.opencoesione.gov.it/api/progetti/",
)
HEADERS = {
    "User-Agent": "ProcRun/phase-r-opencoesione-api-metadata-v1",
    "Accept": "application/json,text/html;q=0.9,*/*;q=0.1",
}
PROJECTION_TERMS = (
    "fields",
    "field",
    "select",
    "projection",
    "include",
    "exclude",
    "only",
)


def request(url: str, method: str) -> dict[str, object]:
    req = urllib.request.Request(url, headers=HEADERS, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            body = response.read(250_000).decode("utf-8", errors="replace")
            return {
                "url": url,
                "method": method,
                "status": response.status,
                "allow": response.headers.get("Allow"),
                "content_type": response.headers.get("Content-Type"),
                "body": body,
            }
    except urllib.error.HTTPError as error:
        body = error.read(250_000).decode("utf-8", errors="replace")
        return {
            "url": url,
            "method": method,
            "status": error.code,
            "allow": error.headers.get("Allow"),
            "content_type": error.headers.get("Content-Type"),
            "body": body,
        }
    except urllib.error.URLError as error:
        return {
            "url": url,
            "method": method,
            "status": None,
            "allow": None,
            "content_type": None,
            "body": "",
            "error": type(error).__name__,
        }


def projection_evidence(text: str) -> list[str]:
    lowered = text.lower()
    return [term for term in PROJECTION_TERMS if term in lowered]


def safe_summary(result: dict[str, object]) -> dict[str, object]:
    body = str(result.get("body", ""))
    return {
        "url": result["url"],
        "method": result["method"],
        "status": result["status"],
        "allow": result["allow"],
        "content_type": result["content_type"],
        "projection_terms_seen": projection_evidence(body),
        "body_length": len(body),
        "error": result.get("error"),
    }


def main() -> int:
    root_results = [request(url, "GET") for url in ROOT_URLS]
    options_results = [request(url, "OPTIONS") for url in PROJECT_URLS]

    summaries = [safe_summary(item) for item in [*root_results, *options_results]]
    projection_possible = any(item["projection_terms_seen"] for item in summaries)

    report = {
        "probe_contract": "opencoesione-api-metadata-options-only-v1",
        "qualification_result": (
            "PROJECTION_METADATA_CANDIDATE"
            if projection_possible
            else "BLOCKED_NO_PRE_RECEIPT_PROJECTION"
        ),
        "boundary": {
            "api_root_only": True,
            "options_only_for_project_resource": True,
            "project_rows_requested": False,
            "project_detail_requested": False,
            "subject_rows_requested": False,
            "beneficiary_data_requested": False,
            "free_text_project_data_requested": False,
            "downloads_requested": False,
        },
        "requests": summaries,
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
