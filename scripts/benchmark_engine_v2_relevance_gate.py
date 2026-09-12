from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold

from procrun.evidence_retrieval_v2 import LocalSentenceTransformersEmbedder

_FAIR_NOISE = re.compile(
    r"\b(fiera|fiere|partecipazione|manifestazione|eicma|host|bimu|tuttofood|lineapelle|"
    r"myplant|micam|milano unica|made expo|greenplast|bovimac|print4all|mido|simei|"
    r"artigiano in fiera|fornitore offresi|salone)\b",
    re.IGNORECASE,
)
_PROMO_NOISE = re.compile(
    r"\b(promozione|presenta(?:no)?|espansione internazionale|rilancio commerciale|"
    r"azione commerciale|mercati internazionali)\b",
    re.IGNORECASE,
)
_GRANT_NOISE = re.compile(r"linea competenze per la transizione industriale", re.IGNORECASE)
_RND_PRODUCT_NOISE = re.compile(
    r"\b(brevetto|composizione|metodo di trattamento|dispositivo di blocco|polimero|"
    r"raccordo|seal and method|lampada tocco)\b",
    re.IGNORECASE,
)
_MEDIA_NOISE = re.compile(
    r"\b(opera audiovisiva|archivio|campagna di comunicazione)\b",
    re.IGNORECASE,
)
_POSITIVE_ANCHOR = re.compile(
    r"\b(fornitura|acquisto|installazione|posa|sostituzione|riqualificazione|ristrutturazione|"
    r"efficientamento|automazione|digitalizzazione|assistenza tecnica|climatizzazione|"
    r"fotovoltaic|compressore|impianto|piattaforma cloud|sistema mes|integrazione dati|"
    r"progetto esecutivo|case mobili|infrastruttura tecnologica|risparmio energetico)\b",
    re.IGNORECASE,
)


def _canonical_sha(value: Any) -> str:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def _noise_reject(text: str) -> bool:
    normalized = " ".join(text.split())
    if _GRANT_NOISE.search(normalized):
        return True
    if _POSITIVE_ANCHOR.search(normalized):
        return False
    if _FAIR_NOISE.search(normalized) or _PROMO_NOISE.search(normalized):
        return True
    if _RND_PRODUCT_NOISE.search(normalized) or _MEDIA_NOISE.search(normalized):
        return True
    if normalized.casefold() in {"nuova domanda", "000000"}:
        return True
    return len(normalized) < 32


def _metrics(
    codes: list[str], y_true: np.ndarray, probabilities: np.ndarray, threshold: float
) -> dict[str, Any]:
    predicted = probabilities >= threshold
    tp_mask = predicted & (y_true == 1)
    fp_mask = predicted & (y_true == 0)
    fn_mask = (~predicted) & (y_true == 1)
    tn_mask = (~predicted) & (y_true == 0)
    tp = int(np.sum(tp_mask))
    fp = int(np.sum(fp_mask))
    fn = int(np.sum(fn_mask))
    tn = int(np.sum(tn_mask))
    recall = tp / (tp + fn) if tp + fn else 0.0
    precision = tp / (tp + fp) if tp + fp else 1.0
    fpr = fp / (fp + tn) if fp + tn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {
        "threshold": round(float(threshold), 8),
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "tn": tn,
        "recall": round(recall, 6),
        "precision": round(precision, 6),
        "negative_case_fpr": round(fpr, 6),
        "f1": round(f1, 6),
        "false_positive_operation_codes": [codes[i] for i in np.flatnonzero(fp_mask)],
        "false_negative_operation_codes": [codes[i] for i in np.flatnonzero(fn_mask)],
    }


def _best(
    rows: list[dict[str, Any]], *, min_precision: float = 0.0, min_recall: float = 0.0
) -> dict[str, Any] | None:
    eligible = [
        row
        for row in rows
        if float(row["precision"]) >= min_precision and float(row["recall"]) >= min_recall
    ]
    if not eligible:
        return None
    return max(
        eligible,
        key=lambda row: (
            float(row["f1"]),
            float(row["recall"]),
            float(row["precision"]),
        ),
    )


def _summary(
    codes: list[str], y: np.ndarray, probabilities: np.ndarray
) -> dict[str, Any]:
    thresholds = sorted({0.0, 1.0, *[float(value) for value in probabilities]})
    rows = [_metrics(codes, y, probabilities, threshold) for threshold in thresholds]
    best_f1 = max(
        rows,
        key=lambda row: (
            float(row["f1"]),
            float(row["recall"]),
            float(row["precision"]),
        ),
    )
    return {
        "best_f1": best_f1,
        "best_at_precision_0_90": _best(rows, min_precision=0.90),
        "best_at_precision_0_95": _best(rows, min_precision=0.95),
        "best_at_recall_0_90": _best(rows, min_recall=0.90),
        "best_at_recall_0_95": _best(rows, min_recall=0.95),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sample", type=Path, required=True)
    parser.add_argument("--labels", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    sample = json.loads(args.sample.read_text(encoding="utf-8"))
    labels = json.loads(args.labels.read_text(encoding="utf-8"))
    if _canonical_sha(sample) != labels["sample_canonical_sha256"]:
        raise RuntimeError("blind sample drift")

    positives = set(labels["positive_operation_codes"])
    ambiguous = set(labels["ambiguous_operation_codes"])
    labelled_cases = [case for case in sample["cases"] if case["operation_code"] not in ambiguous]
    codes = [str(case["operation_code"]) for case in labelled_cases]
    texts = [
        f"{case.get('project_title') or ''}\n{case['project_scope_text']}".strip()
        for case in labelled_cases
    ]
    y = np.asarray([1 if code in positives else 0 for code in codes], dtype=np.int64)

    embedder = LocalSentenceTransformersEmbedder()
    vectors = np.asarray(embedder.encode(texts, kind="passage"), dtype=np.float64)
    splitter = StratifiedKFold(n_splits=5, shuffle=True, random_state=20260912)
    oof = np.zeros(len(labelled_cases), dtype=np.float64)
    for train_idx, test_idx in splitter.split(vectors, y):
        model = LogisticRegression(
            C=1.0,
            class_weight="balanced",
            max_iter=4000,
            solver="liblinear",
            random_state=20260912,
        )
        model.fit(vectors[train_idx], y[train_idx])
        oof[test_idx] = model.predict_proba(vectors[test_idx])[:, 1]

    rejected = np.asarray([_noise_reject(text) for text in texts], dtype=bool)
    gated = oof.copy()
    gated[rejected] = -1.0

    report = {
        "schema_version": "engine-v2-relevance-gate-oof-v2",
        "evaluation": "5-fold stratified OOF; ambiguous excluded; deterministic noise gate post-score",
        "sample_canonical_sha256": labels["sample_canonical_sha256"],
        "embedding_model": embedder.model_name,
        "positive_cases": int(np.sum(y == 1)),
        "negative_cases": int(np.sum(y == 0)),
        "ambiguous_cases_excluded": len(ambiguous),
        "noise_gate_rejected_total": int(np.sum(rejected)),
        "noise_gate_rejected_positives": int(np.sum(rejected & (y == 1))),
        "noise_gate_rejected_negatives": int(np.sum(rejected & (y == 0))),
        "raw_classifier": _summary(codes, y, oof),
        "classifier_plus_noise_gate": _summary(codes, y, gated),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    gated_r95 = report["classifier_plus_noise_gate"]["best_at_recall_0_95"]
    gated_p95 = report["classifier_plus_noise_gate"]["best_at_precision_0_95"]
    print(f"ENGINE_V2_NOISE_REJECTED_POSITIVES={report['noise_gate_rejected_positives']}")
    print(f"ENGINE_V2_NOISE_REJECTED_NEGATIVES={report['noise_gate_rejected_negatives']}")
    print(f"ENGINE_V2_GATED_R95_PRECISION={gated_r95['precision'] if gated_r95 else 'NONE'}")
    print(f"ENGINE_V2_GATED_P95_RECALL={gated_p95['recall'] if gated_p95 else 'NONE'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
