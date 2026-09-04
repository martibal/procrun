"""Fail CI if an actionable human-contact source-qualification path reappears."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCANNED = (ROOT / "docs", ROOT / "src")

# Generic words such as "contact" are intentionally not banned: the permanent prohibition itself
# contains them. These patterns target executable/request language rather than policy discussion.
FORBIDDEN = (
    re.compile(r"ready[- ]to[- ]send", re.IGNORECASE),
    re.compile(r"\bExmos\b", re.IGNORECASE),
    re.compile(r"email.{0,40}confirm", re.IGNORECASE),
    re.compile(r"request.{0,40}clarification", re.IGNORECASE),
    re.compile(r"send.{0,20}(?:an? )?email", re.IGNORECASE),
    re.compile(r"submit.{0,30}(?:form|request|inquiry|enquiry)", re.IGNORECASE),
    re.compile(
        r"(?:ask|contact).{0,30}(?:publisher|authority|source[- ]owner)",
        re.IGNORECASE,
    ),
)

SAFE_NEGATIONS = (
    "without ",
    "never ",
    "do not ",
    "must not ",
    "no future ",
    "no human",
    "prohibited",
    "forbidden",
    "reject",
    "blocked",
    "retired",
    "invalid",
)


def main() -> None:
    violations: list[str] = []
    for root in SCANNED:
        for path in root.rglob("*"):
            if not path.is_file() or path.suffix not in {".md", ".py", ".ts", ".tsx"}:
                continue
            text = path.read_text(encoding="utf-8")
            for line_number, line in enumerate(text.splitlines(), start=1):
                lowered = line.casefold()
                if any(marker in lowered for marker in SAFE_NEGATIONS):
                    continue
                if any(pattern.search(line) for pattern in FORBIDDEN):
                    relative = path.relative_to(ROOT)
                    violations.append(f"{relative}:{line_number}:{line.strip()}")
    if violations:
        joined = "\n".join(violations)
        raise SystemExit(f"human-contact qualification path detected:\n{joined}")
    print("no actionable human-contact qualification path detected in docs/ or src/")


if __name__ == "__main__":
    main()
