from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

EXPECTED_HOLDOUT_SHA = "c1f8bfdee38f0f0b4b9f78da2bc196ad16db8af8f614b5f3fef5e558c58de758"
EXPECTED_COUNTS = {"POSITIVE": 191, "NEGATIVE": 255, "AMBIGUOUS": 354}

_POSITIVE = tuple(
    re.compile(p, re.IGNORECASE)
    for p in (
        r"\bacquist[oa]\b",
        r"\bfornitur",
        r"\binstallaz",
        r"\bsostituzion",
        r"\bristruttur",
        r"\briqualific",
        r"\bmanutenzion",
        r"\badeguament",
        r"\befficientament",
        r"efficienza energetica",
        r"\bfotovolta",
        r"pompa di calore",
        r"\bimpiant",
        r"\bcaldaia\b",
        r"\billuminaz",
        r"\brelamping\b",
        r"\bdigitalizz",
        r"transizione digitale",
        r"\bautomaz",
        r"\bcybersecurity\b",
        r"\berp\b",
        r"\bcrm\b",
        r"\bcloud\b",
        r"\bmes\b",
        r"business intelligence",
        r"\bintegrazione dati",
        r"\bworkflow\b",
        r"\bsupply chain\b",
        r"\bmacchin",
        r"\battrezzatur",
        r"\bpressa\b",
        r"\btornio\b",
        r"\brobot",
        r"\bsoftware\b",
        r"\bpiattaforma\b",
        r"\bsistema\b.*\bgestione\b",
        r"\brealizzazione\b",
        r"\bconstru",
        r"\bcostruz",
        r"\bampliament",
        r"\bprogetto esecutivo\b",
        r"\bassistenza tecnica\b",
    )
)

_NEGATIVE = tuple(
    re.compile(p, re.IGNORECASE)
    for p in (
        r"\bfiera\b",
        r"\bfiere\b",
        r"fieristic",
        r"\beicma\b",
        r"\bhost 20",
        r"\bbimu\b",
        r"lineapelle",
        r"milano unica",
        r"\bmipel\b",
        r"tuttofood",
        r"salone del mobile",
        r"myplant",
        r"\bmiart\b",
        r"expocomfort",
        r"vitrum",
        r"white milano",
        r"partecipazione",
        r"esposizione",
        r"\bexport\b",
        r"internazionalizz",
        r"mercato spagnolo",
        r"mercato estero",
        r"\bbranding\b",
        r"notoriet",
        r"promozion",
        r"campagna di comunicazione",
        r"networking",
        r"accordi commercial",
        r"linea competenze",
        r"sviluppo delle competenze",
        r"potenziamento delle competenze",
        r"percorso di accelerazione",
        r"\bformazione\b",
        r"\bbrevetto\b",
        r"\binvenzion",
        r"\bmetodo per\b",
        r"\bcomposizion",
        r"studio e sviluppo",
        r"ricerca e sviluppo",
        r"\bricerca\b",
        r"\bsperimentaz",
        r"trasferimento tecnologico",
    )
)

_AMBIGUOUS_FIRST = tuple(
    re.compile(p, re.IGNORECASE)
    for p in (
        r"^nuova domanda$",
        r"^progetto di innovazione",
        r"^progetto innovazione",
        r"^intervento di sviluppo tecnologico$",
        r"^digitalizzazione 4\.0\.?$",
        r"^progetto price tool$",
        r"^innovazione e digitalizzazione",
        r"^strategia di digitalizzazione",
        r"^piano di innovazione digitale",
        r"^progetto di efficienza energetica e innovazione tecnologica",
    )
)

_FAIR = re.compile(
    r"\bfiera\b|\bfiere\b|fieristic|eicma|host 20|lineapelle|mipel|tuttofood|salone|"
    r"myplant|miart|expocomfort|vitrum|partecipazione|esposizione",
    re.IGNORECASE,
)


def _canonical_sha(value: Any) -> str:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def _matches(patterns: tuple[re.Pattern[str], ...], text: str) -> bool:
    return any(pattern.search(text) is not None for pattern in patterns)


def _label(text: str) -> str:
    value = " ".join(text.lower().split())
    if _matches(_NEGATIVE, value):
        if _matches(_POSITIVE, value) and not _FAIR.search(value):
            return "AMBIGUOUS"
        return "NEGATIVE"
    if _matches(_AMBIGUOUS_FIRST, value):
        return "AMBIGUOUS"
    if _matches(_POSITIVE, value):
        return "POSITIVE"
    return "AMBIGUOUS"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    holdout: dict[str, Any] = json.loads(args.input.read_text(encoding="utf-8"))
    if _canonical_sha(holdout) != EXPECTED_HOLDOUT_SHA:
        raise RuntimeError("RC2 final holdout drift")
    if holdout.get("engine_output_present") is not False:
        raise RuntimeError("blind adjudication requires source-only holdout")

    buckets: dict[str, list[str]] = {"POSITIVE": [], "NEGATIVE": [], "AMBIGUOUS": []}
    for case in holdout["cases"]:
        text = (
            f"{case.get('project_title') or ''}\n{case.get('project_scope_text') or ''}"
        ).strip()
        buckets[_label(text)].append(str(case["operation_code"]))

    counts = {key: len(value) for key, value in buckets.items()}
    if counts != EXPECTED_COUNTS:
        raise RuntimeError(f"blind adjudication drift: {counts}")

    labels = {
        "schema_version": "engine-v2-rc2-final-holdout-labels-v1",
        "holdout_canonical_sha256": EXPECTED_HOLDOUT_SHA,
        "adjudication_basis": (
            "frozen blind source-only conservative semantic rubric; "
            "no Engine V2 output used"
        ),
        "positive_count": counts["POSITIVE"],
        "negative_count": counts["NEGATIVE"],
        "ambiguous_count": counts["AMBIGUOUS"],
        "positive_operation_codes": buckets["POSITIVE"],
        "negative_operation_codes": buckets["NEGATIVE"],
        "ambiguous_operation_codes": buckets["AMBIGUOUS"],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(labels, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"ENGINE_V2_RC2_FINAL_LABEL_POSITIVE={counts['POSITIVE']}")
    print(f"ENGINE_V2_RC2_FINAL_LABEL_NEGATIVE={counts['NEGATIVE']}")
    print(f"ENGINE_V2_RC2_FINAL_LABEL_AMBIGUOUS={counts['AMBIGUOUS']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
