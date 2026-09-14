from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


def _canonical_sha(value: Any) -> str:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def _cases(document: dict[str, Any], name: str) -> list[dict[str, Any]]:
    cases = document.get("cases")
    if not isinstance(cases, list) or not cases:
        raise ValueError(f"{name} must contain cases")
    return cases


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rc1-development", type=Path, required=True)
    parser.add_argument("--rc1-holdout", type=Path, required=True)
    parser.add_argument("--rc2-development", type=Path, required=True)
    parser.add_argument("--rc2-holdout", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    documents = [
        ("rc1-development", json.loads(args.rc1_development.read_text(encoding="utf-8"))),
        ("rc1-holdout", json.loads(args.rc1_holdout.read_text(encoding="utf-8"))),
        ("rc2-development", json.loads(args.rc2_development.read_text(encoding="utf-8"))),
        ("rc2-holdout", json.loads(args.rc2_holdout.read_text(encoding="utf-8"))),
    ]

    merged: dict[str, dict[str, Any]] = {}
    component_hashes: dict[str, str] = {}
    for name, document in documents:
        if document.get("engine_output_present") is not False:
            raise RuntimeError(f"{name} must be source-only")
        component_hashes[name] = _canonical_sha(document)
        for case in _cases(document, name):
            code = str(case["operation_code"])
            if code in merged:
                raise RuntimeError(f"duplicate consumed case: {code}")
            merged[code] = case

    if len(merged) != 2200:
        raise RuntimeError(f"expected 2200 consumed cases, got {len(merged)}")

    output = {
        "schema_version": "engine-v2-rc3-development-source-only-v1",
        "candidate_id": "engine-v2-rc3-development",
        "component_canonical_sha256": component_hashes,
        "case_count": len(merged),
        "engine_output_present": False,
        "cases": [merged[code] for code in sorted(merged)],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(output, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
        newline="",
    )
    print(f"ENGINE_V2_RC3_DEV_CASES={len(merged)}")
    print(f"ENGINE_V2_RC3_DEV_SHA256={_canonical_sha(output)}")
    print("ENGINE_V2_RC3_DEV_ENGINE_OUTPUT_PRESENT=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
