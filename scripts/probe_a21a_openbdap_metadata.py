"""Qualify OpenBDAP MOP for A21a without requesting any project rows.

The A21a product needs exact project wording that can be shown verbatim as source evidence.
Before testing OData projection, this probe verifies from the public dataset metadata whether the
candidate even documents a project-title / project-description field class. If not, the candidate
is blocked as insufficient for A21a and no row request is permitted.
"""

from __future__ import annotations

import json
import re
import sys
from html.parser import HTMLParser
from urllib.parse import urlparse
from urllib.request import Request, build_opener

DATASET_URL = (
    "https://bdap-opendata.rgs.mef.gov.it/opendata/"
    "spd_mop_prg_mon_reg03_01_9999"
)
APPROVED_HOST = "bdap-opendata.rgs.mef.gov.it"
MAX_METADATA_BYTES = 1_000_000

# A21a requires human-readable project wording, not only identifiers, taxonomy or status fields.
EVIDENCE_TEXT_CONCEPTS = (
    "titolo progetto",
    "titolo dell'opera",
    "descrizione progetto",
    "descrizione dell'opera",
    "sintesi progetto",
    "sintesi dell'opera",
)

# These concepts are useful for project administration but cannot substitute for source wording.
STRUCTURED_PROJECT_CONCEPTS = (
    "cup",
    "stato",
    "natura",
    "tipologia",
    "settore",
    "sottosettore",
    "categoria",
)


class _VisibleTextParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []
        self._ignored_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        del attrs
        if tag.casefold() in {"script", "style"}:
            self._ignored_depth += 1

    def handle_endtag(self, tag: str) -> None:
        if tag.casefold() in {"script", "style"} and self._ignored_depth:
            self._ignored_depth -= 1

    def handle_data(self, data: str) -> None:
        if not self._ignored_depth and data.strip():
            self.parts.append(data)


def _normalise(value: str) -> str:
    return re.sub(r"\s+", " ", value.casefold()).strip()


def visible_text(html: bytes) -> str:
    parser = _VisibleTextParser()
    parser.feed(html.decode("utf-8", errors="strict"))
    return _normalise(" ".join(parser.parts))


def evaluate_metadata_text(text: str) -> dict[str, object]:
    normalised = _normalise(text)
    evidence_hits = tuple(concept for concept in EVIDENCE_TEXT_CONCEPTS if concept in normalised)
    structured_hits = tuple(
        concept for concept in STRUCTURED_PROJECT_CONCEPTS if concept in normalised
    )
    if evidence_hits:
        status = "PROCEED_TO_PROJECTION_GATE"
        reason = "public metadata documents an A21a-capable project wording concept"
    else:
        status = "BLOCKED_INSUFFICIENT_EVIDENCE_TEXT"
        reason = (
            "public metadata documents structured project attributes but no explicit project-title "
            "or project-description field class required for verbatim A21a source evidence"
        )
    return {
        "probe_version": "a21a-openbdap-metadata-utility-v1",
        "dataset_url": DATASET_URL,
        "project_rows_requested": False,
        "odata_rows_requested": False,
        "evidence_text_concept_hits": evidence_hits,
        "structured_project_concept_hits": structured_hits,
        "candidate_status": status,
        "reason": reason,
    }


def _fetch_metadata() -> bytes:
    parsed = urlparse(DATASET_URL)
    if parsed.scheme != "https" or parsed.hostname != APPROVED_HOST:
        raise RuntimeError("OpenBDAP metadata URL is outside the frozen approved origin")
    request = Request(
        DATASET_URL,
        headers={
            "User-Agent": "ProcRun-A21a-OpenBDAP-Metadata-Probe/1.0",
            "Accept": "text/html,application/xhtml+xml",
        },
    )
    with build_opener().open(request, timeout=60) as response:  # noqa: S310
        final = urlparse(response.geturl())
        if final.scheme != "https" or final.hostname != APPROVED_HOST:
            raise RuntimeError("OpenBDAP metadata request redirected outside approved origin")
        payload = response.read(MAX_METADATA_BYTES + 1)
    if len(payload) > MAX_METADATA_BYTES:
        raise RuntimeError("OpenBDAP metadata response exceeds safety bound")
    if not payload:
        raise RuntimeError("OpenBDAP metadata response is empty")
    return payload


def probe() -> dict[str, object]:
    return evaluate_metadata_text(visible_text(_fetch_metadata()))


def main() -> int:
    report = probe()
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    # A deterministic BLOCKED result is a successful safety/utility qualification outcome.
    return 0


if __name__ == "__main__":
    sys.exit(main())
