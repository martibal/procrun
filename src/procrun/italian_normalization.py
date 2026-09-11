"""Deterministic Italian morphology normalization for Phase R.

The normalizer is intentionally small, frozen, and dependency-free. It does not infer semantics.
It reduces common Italian inflectional endings and a short allowlist of administrative derivational
families so source text and rule phrases can be compared under the same transformation.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from typing import Final

ITALIAN_NORMALIZATION_VERSION: Final = "italian-morphology-v1"

_TOKEN_RE = re.compile(r"[^\W\d_]+(?:'[^\W\d_]+)?", flags=re.UNICODE)

_DERIVATIONAL_FAMILIES: Final[tuple[tuple[re.Pattern[str], str], ...]] = (
    (
        re.compile(r"^riqualific(?:azione|azioni|are|ato|ata|ati|ate|ando|ante|anti)$"),
        "riqualific",
    ),
    (re.compile(r"^efficientament(?:o|i)$"), "efficient"),
    (re.compile(r"^energetic(?:o|a|i|e)$"), "energet"),
)

_VERB_SUFFIXES: Final[tuple[str, ...]] = (
    "erebbero",
    "irebbero",
    "arebbero",
    "assero",
    "essero",
    "issero",
    "avano",
    "evano",
    "ivano",
    "ando",
    "endo",
    "ato",
    "ata",
    "ati",
    "ate",
    "uto",
    "uta",
    "uti",
    "ute",
    "ito",
    "ita",
    "iti",
    "ite",
    "are",
    "ere",
    "ire",
)

_NOUN_ADJECTIVE_SUFFIXES: Final[tuple[str, ...]] = (
    "zioni",
    "zione",
    "ici",
    "iche",
    "ico",
    "ica",
    "osi",
    "ose",
    "oso",
    "osa",
    "ali",
    "ale",
)


@dataclass(frozen=True)
class NormalizedToken:
    original: str
    normalized: str
    start: int
    end: int


def _fold(text: str) -> str:
    decomposed = unicodedata.normalize("NFKD", text.casefold())
    return "".join(character for character in decomposed if not unicodedata.combining(character))


def normalize_italian_token(token: str) -> str:
    """Normalize one Italian token deterministically."""

    folded = _fold(token).replace("’", "'")
    if "'" in folded:
        folded = folded.rsplit("'", 1)[-1]

    for pattern, replacement in _DERIVATIONAL_FAMILIES:
        if pattern.fullmatch(folded):
            return replacement

    for suffix in _VERB_SUFFIXES:
        if folded.endswith(suffix) and len(folded) - len(suffix) >= 4:
            return folded[: -len(suffix)]

    for suffix in _NOUN_ADJECTIVE_SUFFIXES:
        if folded.endswith(suffix) and len(folded) - len(suffix) >= 4:
            return folded[: -len(suffix)]

    # Conservative singular/plural and gender reduction for longer content words.
    if len(folded) >= 6 and folded[-1:] in {"a", "e", "i", "o"}:
        return folded[:-1]

    return folded


def normalized_tokens(text: str) -> tuple[NormalizedToken, ...]:
    """Tokenize text and return normalized tokens with exact original offsets."""

    return tuple(
        NormalizedToken(
            original=match.group(0),
            normalized=normalize_italian_token(match.group(0)),
            start=match.start(),
            end=match.end(),
        )
        for match in _TOKEN_RE.finditer(text)
    )


def normalize_italian_text(text: str) -> tuple[str, ...]:
    """Return the normalized token sequence used for deterministic comparison."""

    return tuple(token.normalized for token in normalized_tokens(text))
