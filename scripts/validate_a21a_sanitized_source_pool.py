"""Validate an already-sanitized A21a source pool before development-set selection."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "a21a-sanitized-source-pool-v1"
OPENCOESIONE_SOURCE_ID = "opencoesione_2021_2027_operations"
PUBLISHER_ZERO_PII_CONTRACT = "opencoesione-art49-minimum-rgs-v1"
ALLOWED_TOP_LEVEL = {
    "schema_version",
    "pii_review_status",
    "engine_output_present",
    "sanitization_provenance",
    "cases",
}
ALLOWED_PROVENANCE_FIELDS = {
    "raw_archive_present",
    "download_then_filter_used",
    "source_only_projection_confirmed",
    "projection_boundary",
    "transport_kind",
    "projection_evidence_url",
    "source_id",
    "publisher_resource_sha256",
    "list_updated_on",
    "publisher_zero_pii_contract",
}
ALLOWED_TRANSPORT_KINDS = {
    "field_selective_endpoint",
    "prebuilt_sanitized_resource",
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
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


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


def _validate_prebuilt_publisher_resource(provenance: dict[str, Any]) -> None:
    if provenance.get("source_id") != OPENCOESIONE_SOURCE_ID:
        raise ValueError("prebuilt resource must use the frozen OpenCoesione source id")
    if provenance.get("publisher_zero_pii_contract") != PUBLISHER_ZERO_PII_CONTRACT:
        raise ValueError("publisher zero-PII contract is not the frozen approved contract")
    source_hash = provenance.get("publisher_resource_sha256")
    if not isinstance(source_hash, str) or _SHA256_RE.fullmatch(source_hash) is None:
        raise ValueError("publisher_resource_sha256 must be a lowercase SHA-256")
    updated_on = provenance.get("list_updated_on")
    if not isinstance(updated_on, str) or _DATE_RE.fullmatch(updated_on) is None:
        raise ValueError("list_updated_on must be an ISO date")


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
    extra_provenance = set(provenance) - ALLOWED_PROVENANCE_FIELDS
    if extra_provenance:
        raise ValueError(f"unexpected sanitization provenance fields: {sorted(extra_provenance)}")
    if provenance.get("raw_archive_present") is not False:
        raise ValueError("unqualified raw archives are prohibited")
    if provenance.get("download_then_filter_used") is not False:
        raise ValueError("download-then-filter is prohibited")
    if provenance.get("source_only_projection_confirmed") is not True:
        raise ValueError("source-only projection must be explicitly confirmed")
    if provenance.get("projection_boundary") != "upstream_before_receipt":
        raise ValueError("privacy sanitization must occur upstream before ProcRun receipt")
    transport_kind = provenance.get("transport_kind")
    if transport_kind not in ALLOWED_TRANSPORT_KINDS:
        raise ValueError("transport_kind must prove field-selective or prebuilt sanitized transport")
    evidence_url = provenance.get("projection_evidence_url")
    if not isinstance(evidence_url, str) or not evidence_url.startswith("https://"):
        raise ValueError("HTTPS projection_evidence_url is required")
    if transport_kind == "prebuilt_sanitized_resource":
        _validate_prebuilt_publisher_resource(provenance)

    cases = document.get("cases")
    if not isinstance(cases, list) or not cases:
        raise ValueError("cases must be a non-empty list")

    forbidden = _contains_forbidden_key(cases)
    if forbidden is not None:
        raise ValueError(f"forbidden field detected: {forbidden}")

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
        "projection_boundary": "upstream_before_receipt",
        "transport_kind": transport_kind,
        "publisher_resource_sha256": provenance.get("publisher_resource_sha256"),
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
