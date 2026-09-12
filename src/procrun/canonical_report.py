"""Canonical report serialization and hashing for ProcRun v1.

ProcRun report payloads deliberately use a restricted JSON scalar domain: integers, strings,
booleans, null, arrays and objects with ASCII field names. Floats are prohibited in persisted
payloads; calculated ratios must be rendered as scaled integers or decimal strings before this
boundary. Within that domain, the serializer below produces RFC 8785-compatible JSON bytes.
"""

from __future__ import annotations

import hashlib
import json


CANONICALIZATION_VERSION = "rfc8785-restricted-v1"


class CanonicalizationError(ValueError):
    pass


def _validate(value: object, *, path: str = "$") -> None:
    if value is None or isinstance(value, (str, bool, int)):
        return
    if isinstance(value, float):
        raise CanonicalizationError(f"floating-point value prohibited at {path}")
    if isinstance(value, list):
        for index, item in enumerate(value):
            _validate(item, path=f"{path}[{index}]")
        return
    if isinstance(value, dict):
        for key, item in value.items():
            if not isinstance(key, str):
                raise CanonicalizationError(f"non-string key at {path}")
            if not key.isascii():
                raise CanonicalizationError(f"non-ASCII key prohibited at {path}.{key}")
            _validate(item, path=f"{path}.{key}")
        return
    raise CanonicalizationError(f"unsupported JSON value {type(value).__name__} at {path}")


def canonicalize(payload: dict[str, object]) -> bytes:
    """Return canonical UTF-8 JSON bytes for the restricted ProcRun report domain."""
    _validate(payload)
    text = json.dumps(
        payload,
        ensure_ascii=False,
        allow_nan=False,
        separators=(",", ":"),
        sort_keys=True,
    )
    return text.encode("utf-8")


def sha256_hex(canonical_bytes: bytes) -> str:
    return hashlib.sha256(canonical_bytes).hexdigest()


def canonicalize_and_hash(payload: dict[str, object]) -> tuple[bytes, str]:
    canonical = canonicalize(payload)
    return canonical, sha256_hex(canonical)


def verify_canonical_record(
    *, canonical_bytes: bytes, canonical_sha256: str, json_payload: dict[str, object]
) -> None:
    """Fail closed unless hash, canonical form, and JSON semantics all agree."""
    if sha256_hex(canonical_bytes) != canonical_sha256:
        raise CanonicalizationError("stored SHA-256 does not match canonical bytes")
    parsed = json.loads(canonical_bytes.decode("utf-8"))
    if parsed != json_payload:
        raise CanonicalizationError("canonical bytes and JSON payload differ semantically")
    regenerated = canonicalize(parsed)
    if regenerated != canonical_bytes:
        raise CanonicalizationError("stored bytes are not canonical")
