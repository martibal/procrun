import pytest

from procrun.canonical_report import (
    CanonicalizationError,
    canonicalize_and_hash,
    verify_canonical_record,
)


def test_identical_payload_has_identical_bytes_and_hash() -> None:
    payload = {"z": 2, "a": {"x": 1}, "list": [3, 2, 1]}
    first_bytes, first_hash = canonicalize_and_hash(payload)
    for _ in range(100):
        next_bytes, next_hash = canonicalize_and_hash(payload)
        assert next_bytes == first_bytes
        assert next_hash == first_hash


def test_float_is_rejected_at_persistence_boundary() -> None:
    with pytest.raises(CanonicalizationError, match="floating-point"):
        canonicalize_and_hash({"percentile": 0.75})


def test_verification_checks_hash_semantics_and_canonical_bytes() -> None:
    payload = {"a": 1, "b": "ø"}
    canonical_bytes, digest = canonicalize_and_hash(payload)
    verify_canonical_record(
        canonical_bytes=canonical_bytes,
        canonical_sha256=digest,
        json_payload=payload,
    )
    with pytest.raises(CanonicalizationError, match="SHA-256"):
        verify_canonical_record(
            canonical_bytes=canonical_bytes,
            canonical_sha256="0" * 64,
            json_payload=payload,
        )
