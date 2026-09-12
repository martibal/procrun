"""Canonical Readiness Dossier v2 composition, language guard and hashing."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
import hashlib
import json

from procrun.readiness_benchmark import BenchmarkObservation, compute_historical_dimensioning
from procrun.readiness_matrix import AdvisorConfirmation, build_readiness_matrix
from procrun.readiness_source import SourcePackage, SourcePackageState, package_manifest, package_sha256

DOSSIER_SCHEMA_VERSION = "readiness-dossier-v2"
CANONICALIZATION_VERSION = "rfc8785-restricted-ascii-keys-v1"

FORBIDDEN_CUSTOMER_PHRASES = (
    "eligible",
    "ineligible",
    "complete verifica preliminare",
    "procRun approved",
)


class DossierBlockedError(RuntimeError):
    pass


@dataclass(frozen=True)
class DossierBuildInput:
    dossier_id: str
    tenant_key: str
    purchase_reference: str
    source_package: SourcePackage
    invalidated_at: datetime | None
    benchmark_snapshot_id: str
    benchmark_data_through: str
    benchmark_snapshot_sha256: str
    observations: tuple[BenchmarkObservation, ...]
    proposed_funding_eur: int
    proposed_duration_months: int | None
    confirmations: tuple[AdvisorConfirmation, ...]
    created_at: datetime


def _validate_canonical_value(value: object, path: str = "$") -> None:
    if value is None or isinstance(value, (str, bool, int)):
        return
    if isinstance(value, list):
        for index, item in enumerate(value):
            _validate_canonical_value(item, f"{path}[{index}]")
        return
    if isinstance(value, dict):
        for key, item in value.items():
            if not isinstance(key, str):
                raise TypeError(f"non-string key at {path}")
            if not key.isascii():
                raise TypeError(f"non-ASCII key at {path}.{key}")
            _validate_canonical_value(item, f"{path}.{key}")
        return
    raise TypeError(f"unsupported canonical value {type(value).__name__} at {path}")


def canonicalize(payload: dict[str, object]) -> bytes:
    """Canonical UTF-8 bytes for ProcRun's restricted RFC8785-compatible domain."""
    _validate_canonical_value(payload)
    return json.dumps(
        payload,
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def assert_customer_language(payload: dict[str, object]) -> None:
    rendered = json.dumps(payload, ensure_ascii=False).lower()
    for phrase in FORBIDDEN_CUSTOMER_PHRASES:
        if phrase.lower() in rendered:
            raise ValueError(f"forbidden customer-facing phrase detected: {phrase}")


def build_dossier(input_data: DossierBuildInput) -> tuple[dict[str, object], bytes, str]:
    if input_data.created_at.tzinfo is None:
        raise ValueError("created_at must be timezone-aware")
    if not input_data.purchase_reference.strip():
        raise DossierBlockedError("trusted purchase reference is required for dossier creation")
    state = input_data.source_package.state_at(
        input_data.created_at,
        invalidated_at=input_data.invalidated_at,
    )
    if state is not SourcePackageState.FRESH:
        raise DossierBlockedError(f"paid dossier unavailable: source package state is {state.value}")
    if len(input_data.benchmark_snapshot_sha256) != 64:
        raise ValueError("benchmark snapshot sha256 must be 64 hex characters")
    int(input_data.benchmark_snapshot_sha256, 16)

    project_inputs = {
        "proposed_funding_eur": input_data.proposed_funding_eur,
        "proposed_duration_months": input_data.proposed_duration_months,
    }
    payload: dict[str, object] = {
        "schema_version": DOSSIER_SCHEMA_VERSION,
        "dossier_id": input_data.dossier_id,
        "tenant_key": input_data.tenant_key,
        "created_at": input_data.created_at.astimezone(UTC).isoformat(),
        "purchase_reference": input_data.purchase_reference,
        "project_inputs": project_inputs,
        "source_package": {
            "source_package_id": input_data.source_package.source_package_id,
            "bando_code": input_data.source_package.bando_code,
            "version": input_data.source_package.version,
            "verified_at": input_data.source_package.verified_at.astimezone(UTC).isoformat(),
            "refresh_due_at": input_data.source_package.refresh_due_at.isoformat(),
            "package_sha256": package_sha256(input_data.source_package),
            "manifest": package_manifest(input_data.source_package),
        },
        "published_requirements_matrix": build_readiness_matrix(
            input_data.source_package,
            project_inputs=project_inputs,
            confirmations=input_data.confirmations,
        ),
        "historical_dimensioning": {
            "snapshot_id": input_data.benchmark_snapshot_id,
            "data_through": input_data.benchmark_data_through,
            "snapshot_sha256": input_data.benchmark_snapshot_sha256,
            "analysis": compute_historical_dimensioning(
                input_data.observations,
                proposed_funding_eur=input_data.proposed_funding_eur,
                proposed_duration_months=input_data.proposed_duration_months,
            ),
        },
        "epistemic_contract": {
            "integrity_is_not_correctness": (
                "Cryptographic integrity proves which source package and benchmark snapshot were used; "
                "it does not prove that source extraction is legally complete or correct."
            ),
            "completion_is_not_a_verdict": (
                "Checklist completion records what the advisor addressed; it is not a qualification, "
                "readiness, approval, compliance, or funding verdict."
            ),
            "professional_judgment": (
                "ProcRun does not decide DNSH, PMI consolidation, ATECO interpretation, or other "
                "professional or discretionary requirements on the advisor's behalf."
            ),
        },
        "canonicalization_version": CANONICALIZATION_VERSION,
    }
    assert_customer_language(payload)
    canonical = canonicalize(payload)
    return payload, canonical, sha256_hex(canonical)


def verify_dossier(payload: dict[str, object], canonical_bytes: bytes, digest: str) -> None:
    if sha256_hex(canonical_bytes) != digest:
        raise ValueError("dossier hash mismatch")
    if json.loads(canonical_bytes.decode("utf-8")) != payload:
        raise ValueError("canonical dossier bytes differ from payload")
    if canonicalize(payload) != canonical_bytes:
        raise ValueError("dossier bytes are not canonical")
