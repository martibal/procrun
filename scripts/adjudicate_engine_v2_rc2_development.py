from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

_SCHEMA = "engine-v2-rc2-development-labels-v1"

_NEGATIVE_PATTERNS = tuple(
    re.compile(pattern, re.IGNORECASE)
    for pattern in (
        r"\bfiera\b",
        r"\bfiere\b",
        r"fieristic",
        r"eicma|\bbimu\b|linea ?pelle|lineapelle|milano unica|\bmipel\b",
        r"fornitore offresi|\bhost\b|ipack.?ima|tuttofood|salone del mobile",
        r"packaging premi|myplant|\bmiart\b|\bmade expo\b|\bplas?t 2026\b",
        r"\bexpocomfort\b|\bvitrum\b|\bproposte 2025\b|\bhomi\b|\bwhite milano\b",
        r"partecipazione|esposizione|mostra convegno|networking",
        r"promozion|internazional|export|espansione.*mercat|visibilit.? globale|branding",
        r"accordi commercial|acquisizione ordini",
        r"linea competenze|sviluppo delle competenze|competenze innovative",
        r"potenziamento delle competenze|percorso di accelerazione",
        r"opera audiovisiva|campagna di comunicazione|archivio al patrimonio",
        r"collezione primavera",
        r"brevetto|composizion|metodo di trattamento|cella elettrochimica",
        r"dispositivo chirurgico|dispositivo di aggancio|dispositivo di sanificazione",
        r"valvola per colonna|gruppo portautensile|apparato per confezionamento",
        r"macchine e metodi per la misura|macchine per spingere|attrezzo sportivo innovativo",
        r"miscela per |estensione internazionale.*invenzioni",
        r"studio e sviluppo|ricerca e sviluppo|development of analytical technologies",
        r"food guardian via advanced reactive devices|autocampionatore per analisi chimiche",
        r"sviluppo di un innovativ[oa] pompa|sviluppo di un convertitore elettronico",
        r"sviluppo di un nuovo sistema di gestione delle formule",
    )
)

_POSITIVE_PATTERNS = tuple(
    re.compile(pattern, re.IGNORECASE)
    for pattern in (
        r"efficientamento|efficienza energetica|efficentamento|riduzione consumi",
        r"risparmio energetico|neutralit.? energetica|sostenibilit energetica",
        r"digitalizz|transizione digitale|automati[sz]|automazione|cybersecurity",
        r"\bcloud\b|\berp\b|\bcrm\b|sistema mes|business intelligence",
        r"integrazione.*process|processi digital|digital collaboration|applicativo bpm",
        r"smart factory|piattaforma.*welfare|sistema di gestione predittiva",
        r"adozione e integrazione|digital roadmap|rinnovo digitale|digitalflow|digital hub",
        r"transformazione digitale|trasformazione digitale|maturit.? digitale",
        r"ristruttur|riqualific|adeguamento strutturale|manut.*straordin|\blavori\b",
        r"realizzazione di .*hub|realizzazione di .*centro|realizzazione di .*hotel",
        r"studentato|housing ",
        r"\bacquisto\b|\bfornitura\b|\binstallaz|\bsostituzione\b",
        r"ammodernamento attrezz|nuove macchine|nuovo pastorizzatore",
        r"pastorizzatore ad alta efficienza|tornio cnc|caldaia|pompa calore|fotovolta",
        r"illuminazione|impiant|infrastruttur|show room a led|sistema integrato di pesatura",
        r"centro del riutilizzo|compostaggio di comunit|food hub",
        r"interventi di innovazione tecnologica degli impianti|attrezzature per",
        r"sostituzione attrezzatura|progetto esecutivo|assistenza tecnica",
    )
)

_EXPLICIT_POSITIVE = re.compile(
    r"\b(acquisto|fornitura|installazione|sostituzione|ristrutturazione|riqualificazione|"
    r"efficientamento|efficienza energetica|digitalizzazione|automazione|cybersecurity|"
    r"assistenza tecnica|lavori)\b",
    re.IGNORECASE,
)
_FAIR_CONTEXT = re.compile(
    r"fiera|fiere|fieristic|eicma|bimu|host|lineapelle|milano unica|mipel|tuttofood|"
    r"salone|ipack|myplant|miart|expocomfort|vitrum",
    re.IGNORECASE,
)


def _canonical_sha(value: Any) -> str:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def _matches(patterns: tuple[re.Pattern[str], ...], text: str) -> bool:
    return any(pattern.search(text) is not None for pattern in patterns)


def _label(text: str) -> str:
    negative = _matches(_NEGATIVE_PATTERNS, text)
    positive = _matches(_POSITIVE_PATTERNS, text)
    explicit_positive = _EXPLICIT_POSITIVE.search(text) is not None
    fair_context = _FAIR_CONTEXT.search(text) is not None
    if fair_context:
        return "NEGATIVE"
    if negative and not explicit_positive:
        return "NEGATIVE"
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
        raise RuntimeError("RC2 adjudication accepts source-only input only")
    if int(sample.get("rc1_overlap_count", -1)) != 0:
        raise RuntimeError("RC2 development sample overlaps RC1 data")
    cases = sample.get("cases")
    if not isinstance(cases, list) or not cases:
        raise ValueError("RC2 development sample must contain cases")

    positives: list[str] = []
    ambiguous: list[str] = []
    for case in cases:
        text = str(case.get("project_title") or case.get("project_scope_text") or "").strip()
        label = _label(text)
        if label == "POSITIVE":
            positives.append(str(case["operation_code"]))
        elif label == "AMBIGUOUS":
            ambiguous.append(str(case["operation_code"]))

    negative_count = len(cases) - len(positives) - len(ambiguous)
    labels = {
        "schema_version": _SCHEMA,
        "adjudication_basis": (
            "source-only conservative high-confidence development labeling; "
            "no RC1 holdout errors or Engine V2 outputs used"
        ),
        "sample_canonical_sha256": _canonical_sha(sample),
        "positive_count": len(positives),
        "negative_count": negative_count,
        "ambiguous_count": len(ambiguous),
        "positive_operation_codes": positives,
        "ambiguous_operation_codes": ambiguous,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(labels, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
        newline="",
    )
    print(f"ENGINE_V2_RC2_LABEL_POSITIVE={len(positives)}")
    print(f"ENGINE_V2_RC2_LABEL_NEGATIVE={negative_count}")
    print(f"ENGINE_V2_RC2_LABEL_AMBIGUOUS={len(ambiguous)}")
    print(f"ENGINE_V2_RC2_SAMPLE_SHA256={labels['sample_canonical_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
