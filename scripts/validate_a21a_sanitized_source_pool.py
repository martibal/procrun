"""Validate an already-sanitized A21a source pool before development-set selection.

This validator never downloads source archives. It accepts only a pre-sanitized JSON package
containing the explicitly allowlisted project fields needed by A21a evidence retrieval.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "a21a-sanitized-source-pool-v1"
ALLOWED_TOP_LEVEL = {
    "schema_version",
    "pii_review_status",
    "engine_output_present",
    "sanitization_provenance",
    "cases",
}
ALLOWED_CASE_FIELDS = {
    "operation_code",
    "project_title",
    "project_scope_text",
    "region",
    "municipality",
    "nuts_code",
    "source_url",
    "language",
}
FORBIDDEN_FIELD_FRAGMENTS = (
    "beneficiary",
    "beneficiario",
    "tax_code",
    "taxcode",
    "codicefiscale",
    "person_name",
    "email",
    "phone",
    "telephone",
    "address",
    "contact",
    "extractor_output",
    "classification_output",
    "engine_output",
)


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()


def _contains_forbidden_key(value: Any) -> str | None:
    if isinstance(value, dict):
        for key, child in value.items():
            lowered = str(key).replace("-", "_").lower()
            for fragment in FORBIDDEN_FIELD_FRAGMENTS:
                if fragment in lowered:
                    return str(key)
            found = _contains_forbidden_key(child)
            if found is not None:
                return found
    elif isinstance(value, list):
        for child in value:
            found = _contains_forbidden_key(child)
            if found is not None:
                return found
    return None


def validate(document: dict[str, Any]) -> dict[str, Any]:
    if set(document) - ALLOWED_TOP_LEVEL:
        raise ValueError(f"unexpected top-level fields: {sorted(set(document) - ALLOWED_TOP_LEVEL)}")
    if document.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("unsupported sanitized source-pool schema")
    if document.get("pii_review_status") != "ZERO_PII_CONFIRMED":
        raise ValueError("pii_review_status must be ZERO_PII_CONFIRMED")
    if document.get("engine_output_present") is not False:
        raise ValueError("engine_output_present must be false")

    provenance = document.get("sanitization_provenance")
    if not isinstance(provenance, dict):
        raise ValueError("sanitization_provenance is required")
    if provenance.get("raw_archive_present") is not False:
        raise ValueError("raw archives are prohibited")
    if provenance.get("download_then_filter_used") is not False:
        raise ValueError("download-then-filter is prohibited")
    if provenance.get("source_only_projection_confirmed") is not True:
        raise ValueError("source-only projection must be explicitly confirmed")

    forbidden = _contains_forbidden_key(document)
    if forbidden is not None:
        raise ValueError(f"forbidden field detected: {forbidden}")

    cases = document.get("cases")
    if not isinstance(cases, list) or not cases:
        raise ValueError("cases must be a non-empty list")

    seen: set[str] = set()
    for case in cases:
        if not isinstance(case, dict):
            raise ValueError("each case must be an object")
        extra = set(case) - ALLOWED_CASE_FIELDS
        if extra:
            raise ValueError(f"unexpected case fields: {sorted(extra)}")
        operation_code = str(case.get("operation_code") or "").strip()
        scope = case.get("project_scope_text")
        source_url = case.get("source_url")
        if not operation_code or operation_code in seen:
            raise ValueError("operation_code values must be non-empty and unique")
        if not isinstance(scope, str) or not scope.strip():
            raise ValueError(f"{operation_code}: project_scope_text required")
        if not isinstance(source_url, str) or not source_url.startswith("https://"):
            raise ValueError(f"{operation_code}: HTTPS source_url required")
        seen.add(operation_code)

    canonical_sha256 = hashlib.sha256(_canonical_bytes(document)).hexdigest()
    return {
        "schema_version": "a21a-sanitized-source-ingress-report-v1",
        "case_count": len(cases),
        "zero_pii_confirmed": True,
        "raw_archive_present": False,
        "download_then_filter_used": False,
        "engine_output_present": False,
        "source_only_projection_confirmed": True,
        "canonical_sha256": canonical_sha256,
        "ingress_pass": True,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    document = json.loads(args.input.read_text(encoding="utf-8"))
    report = validate(document)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
        newline="",
    )
    print(f"A21A_SANITIZED_SOURCE_CASES={report['case_count']}")
    print(f"A21A_SANITIZED_SOURCE_SHA256={report['canonical_sha256']}")
    print("A21A_SANITIZED_SOURCE_INGRESS=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
