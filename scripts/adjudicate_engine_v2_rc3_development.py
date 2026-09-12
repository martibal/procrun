from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any


def _patterns(values: tuple[str, ...]) -> tuple[re.Pattern[str], ...]:
    return tuple(re.compile(value, re.IGNORECASE) for value in values)


_NEGATIVE = _patterns((
    r"\bfiera\b", r"\bfiere\b", r"fieristic", r"\beicma\b", r"\bhost 20", r"\bbimu\b",
    r"lineapelle", r"milano unica", r"\bmipel\b", r"tuttofood", r"salone", r"euroluce",
    r"myplant", r"\bmiart\b", r"expocomfort", r"vitrum", r"partecipazione", r"esposizione",
    r"\bexport\b", r"internazionalizz", r"mercato spagnolo", r"mercato estero",
    r"\bbranding\b", r"notoriet", r"promozion", r"campagna di comunicazione", r"networking",
    r"accordi commercial", r"linea competenze", r"sviluppo delle competenze",
    r"potenziamento delle competenze", r"percorso di accelerazione", r"\bformazione\b",
    r"\bbrevetto\b", r"valorizzazione.*brevetto", r"\binvenzion", r"\bmetodo per\b",
    r"\bcomposizion", r"studio e sviluppo", r"ricerca e sviluppo", r"\bricerca\b",
    r"\bsperimentaz", r"trasferimento tecnologico", r"simulatore.*ispezione", r"modelli iperrealistici",
))

_POSITIVE = _patterns((
    r"\bacquist[oa]\b", r"\bfornitur", r"\binstallaz", r"\bsostituzion",
    r"\bristruttur", r"\briqualific", r"\bmanutenzion", r"\badeguament",
    r"\befficientament", r"efficienza energetica", r"\bfotovolta", r"pompa di calore",
    r"\bimpiant", r"\bcaldaia\b", r"\billuminaz", r"\brelamping\b",
    r"\bdigitalizz", r"transizione digitale", r"\bautomaz", r"\bcybersecurity\b",
    r"\berp\b", r"\bcrm\b", r"\bcloud\b", r"\bmes\b", r"business intelligence",
    r"\bintegrazione dati", r"\bworkflow\b", r"\bsupply chain\b",
    r"\bmacchin", r"\bmacchinari\b", r"\battrezzatur", r"\bpressa\b", r"\btornio\b",
    r"\brobot", r"isola robotizzata", r"piegatrice", r"elettroerosione", r"pastorizzatore",
    r"\bsoftware\b", r"\bpiattaforma\b", r"\bsistema\b.*\bgestione\b",
    r"\brealizzazione\b", r"\bcostruz", r"\bampliament", r"foresteria",
    r"\bprogetto esecutivo\b", r"\bassistenza tecnica\b",
))

_ALWAYS_AMBIGUOUS = _patterns((
    r"^nuova domanda$", r"^progetto di innovazione", r"^progetto innovazione",
    r"^intervento di sviluppo tecnologico$", r"^progetto price tool$",
    r"^innovazione e digitalizzazione", r"^strategia di digitalizzazione",
    r"^piano di innovazione digitale", r"^progetto di efficienza energetica e innovazione tecnologica",
))


def _canonical_sha(value: Any) -> str:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def _matches(patterns: tuple[re.Pattern[str], ...], text: str) -> bool:
    return any(pattern.search(text) is not None for pattern in patterns)


def _label(text: str) -> str:
    value = " ".join(text.lower().split())
    negative = _matches(_NEGATIVE, value)
    positive = _matches(_POSITIVE, value)
    if negative:
        return "NEGATIVE"
    if _matches(_ALWAYS_AMBIGUOUS, value):
        return "AMBIGUOUS"
    if positive:
        return "POSITIVE"
    return "AMBIGUOUS"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    sample: dict[str, Any] = json.loads(args.input.read_text(encoding="utf-8"))
    if sample.get("engine_output_present") is not False:
        raise RuntimeError("RC3 adjudication accepts source-only input only")
    cases = sample.get("cases")
    if not isinstance(cases, list) or not cases:
        raise ValueError("RC3 development sample must contain cases")

    buckets: dict[str, list[str]] = {"POSITIVE": [], "NEGATIVE": [], "AMBIGUOUS": []}
    for case in cases:
        text = f"{case.get('project_title') or ''}\n{case.get('project_scope_text') or ''}".strip()
        buckets[_label(text)].append(str(case["operation_code"]))

    labels = {
        "schema_version": "engine-v2-rc3-development-labels-v1",
        "adjudication_basis": "source-only conservative procurement-need rubric refined after RC2 was closed",
        "sample_canonical_sha256": _canonical_sha(sample),
        "positive_count": len(buckets["POSITIVE"]),
        "negative_count": len(buckets["NEGATIVE"]),
        "ambiguous_count": len(buckets["AMBIGUOUS"]),
        "positive_operation_codes": buckets["POSITIVE"],
        "negative_operation_codes": buckets["NEGATIVE"],
        "ambiguous_operation_codes": buckets["AMBIGUOUS"],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(labels, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
        newline="",
    )
    print(f"ENGINE_V2_RC3_LABEL_POSITIVE={labels['positive_count']}")
    print(f"ENGINE_V2_RC3_LABEL_NEGATIVE={labels['negative_count']}")
    print(f"ENGINE_V2_RC3_LABEL_AMBIGUOUS={labels['ambiguous_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
