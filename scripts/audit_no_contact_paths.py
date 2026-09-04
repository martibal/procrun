"""Fail CI if an actionable human-contact source-qualification path reappears."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCANNED = (ROOT / "docs", ROOT / "src")

FORBIDDEN = (
    re.compile(r"ready[- ]to[- ]send", re.IGNORECASE),
    re.compile(r"\bExmos\b", re.IGNORECASE),
    re.compile(r"email.{0,40}confirm", re.IGNORECASE),
    re.compile(r"request.{0,40}clarification", re.IGNORECASE),
    re.compile(r"send.{0,20}(?:an? )?email", re.IGNORECASE),
    re.compile(r"contact.{0,50}(?:obtain|confirm|clarif|approval|required)", re.IGNORECASE),
    re.compile(r"(?:publisher|authority|source[- ]owner).{0,40}confirmation required", re.IGNORECASE),
)


def main() -> None:
    violations: list[str] = []
    for root in SCANNED:
        for path in root.rglob("*"):
            if not path.is_file() or path.suffix not in {".md", ".py", ".ts", ".tsx"}:
                continue
            text = path.read_text(encoding="utf-8")
            for line_number, line in enumerate(text.splitlines(), start=1):
                if any(pattern.search(line) for pattern in FORBIDDEN):
                    violations.append(f"{path.relative_to(ROOT)}:{line_number}:{line.strip()}")
    if violations:
        joined = "\n".join(violations)
        raise SystemExit(f"human-contact qualification path detected:\n{joined}")
    print("no actionable human-contact qualification path detected in docs/ or src/")


if __name__ == "__main__":
    main()
