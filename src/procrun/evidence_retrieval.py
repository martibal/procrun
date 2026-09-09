"""Deterministic source-evidence extraction for the ProcRun 2.0 evidence-first product layer."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date

from pydantic import Field, model_validator

from procrun.domain import FundingProject, StrictModel

EVIDENCE_RETRIEVAL_VERSION = "evidence-retrieval-v1"
SOURCE_FIELD = "project_scope_text"

_SENTENCE_RE = re.compile(r"[^.!?\n]+(?:[.!?]+|(?=\n|$))", re.UNICODE)

# Conservative procurement/status vocabulary. The extractor ranks exact source sentences only;
# these terms never become customer-facing evidence by themselves.
_KEYWORD_WEIGHTS: tuple[tuple[str, int], ...] = (
    ("aggiudicazione", 8),
    ("aggiudicat", 8),
    ("affidamento", 8),
    ("affidat", 8),
    ("gara", 8),
    ("appalto", 8),
    ("bando", 7),
    ("procedura", 6),
    ("contratto", 6),
    ("fornitura", 5),
    ("acquisto", 5),
    ("acquisizione", 5),
    ("tender", 8),
    ("procurement", 8),
    ("award", 8),
    ("contract", 6),
    ("purchase", 5),
    ("supply", 5),
    ("realizzazione", 2),
    ("installazione", 2),
    ("fornire", 2),
)


class SourceEvidenceExcerpt(StrictModel):
    operation_code: str
    source_field: str = SOURCE_FIELD
    source_url: str
    original_language: str = Field(min_length=2, max_length=16)
    original_text: str = Field(min_length=1)
    start_offset: int = Field(ge=0)
    end_offset: int = Field(gt=0)
    document_date: date | None = None
    extractor_version: str = EVIDENCE_RETRIEVAL_VERSION
    english_translation: str | None = None

    @model_validator(mode="after")
    def validate_span(self) -> "SourceEvidenceExcerpt":
        if self.end_offset <= self.start_offset:
            raise ValueError("evidence end_offset must be greater than start_offset")
        return self


@dataclass(frozen=True)
class _SentenceCandidate:
    start: int
    end: int
    text: str
    score: int
    keyword_hits: int


def _score_sentence(text: str) -> tuple[int, int]:
    normalized = text.casefold()
    score = 0
    hits = 0
    for keyword, weight in _KEYWORD_WEIGHTS:
        if keyword in normalized:
            score += weight
            hits += 1
    return score, hits


def _sentence_candidates(source_text: str) -> tuple[_SentenceCandidate, ...]:
    candidates: list[_SentenceCandidate] = []
    for match in _SENTENCE_RE.finditer(source_text):
        raw = match.group(0)
        left_trim = len(raw) - len(raw.lstrip())
        right_trimmed = raw.rstrip()
        if not right_trimmed.strip():
            continue
        start = match.start() + left_trim
        end = match.start() + len(right_trimmed)
        text = source_text[start:end]
        score, hits = _score_sentence(text)
        candidates.append(
            _SentenceCandidate(
                start=start,
                end=end,
                text=text,
                score=score,
                keyword_hits=hits,
            )
        )
    return tuple(candidates)


def extract_source_evidence(
    project: FundingProject,
    *,
    original_language: str = "it",
    max_sentences: int = 3,
    minimum_score: int = 5,
) -> tuple[SourceEvidenceExcerpt, ...]:
    """Return up to three exact procurement-relevant source sentences, fail-closed on weak text.

    The function never rewrites source text and never infers procurement or project state. It only
    ranks literal sentences from ``FundingProject.project_scope_text`` and returns exact offsets.
    """

    if max_sentences < 1 or max_sentences > 3:
        raise ValueError("max_sentences must be between 1 and 3")
    if minimum_score < 1:
        raise ValueError("minimum_score must be positive")

    source_text = project.project_scope_text
    ranked = sorted(
        (
            candidate
            for candidate in _sentence_candidates(source_text)
            if candidate.score >= minimum_score
        ),
        key=lambda item: (-item.score, -item.keyword_hits, item.start, item.end),
    )
    selected = sorted(ranked[:max_sentences], key=lambda item: (item.start, item.end))

    excerpts: list[SourceEvidenceExcerpt] = []
    for candidate in selected:
        if source_text[candidate.start : candidate.end] != candidate.text:
            raise RuntimeError("evidence extraction lost exact source-span integrity")
        excerpts.append(
            SourceEvidenceExcerpt(
                operation_code=project.operation_code,
                source_url=project.source_url,
                original_language=original_language,
                original_text=candidate.text,
                start_offset=candidate.start,
                end_offset=candidate.end,
            )
        )
    return tuple(excerpts)
