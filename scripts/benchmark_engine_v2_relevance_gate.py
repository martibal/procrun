from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold

from procrun.evidence_retrieval_v2 import LocalSentenceTransformersEmbedder


def _canonical_sha(value: Any) -> str:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def _metrics(y_true: np.ndarray, probabilities: np.ndarray, threshold: float) -> dict[str, float | int]:
    predicted = probabilities >= threshold
    tp = int(np.sum(predicted & (y_true == 1)))
    fp = int(np.sum(predicted & (y_true == 0)))
    fn = int(np.sum((~predicted) & (y_true == 1)))
    tn = int(np.sum((~predicted) & (y_true == 0)))
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
    }


def _best(rows: list[dict[str, float | int]], *, min_precision: float = 0.0, min_recall: float = 0.0) -> dict[str, float | int] | None:
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
    texts = [
        f"{case.get('project_title') or ''}\n{case['project_scope_text']}".strip()
        for case in labelled_cases
    ]
    y = np.asarray(
        [1 if case["operation_code"] in positives else 0 for case in labelled_cases],
        dtype=np.int64,
    )

    embedder = LocalSentenceTransformersEmbedder()
    vectors = np.asarray(embedder.encode(texts, kind="passage"), dtype=np.float64)
    if vectors.shape[0] != len(labelled_cases):
        raise RuntimeError("embedding count mismatch")

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

    thresholds = sorted({0.0, 1.0, *[float(value) for value in oof]})
    rows = [_metrics(y, oof, threshold) for threshold in thresholds]
    best_f1 = max(
        rows,
        key=lambda row: (
            float(row["f1"]),
            float(row["recall"]),
            float(row["precision"]),
        ),
    )
    report = {
        "schema_version": "engine-v2-relevance-gate-oof-v1",
        "evaluation": "5-fold stratified out-of-fold; ambiguous cases excluded",
        "sample_canonical_sha256": labels["sample_canonical_sha256"],
        "embedding_model": embedder.model_name,
        "positive_cases": int(np.sum(y == 1)),
        "negative_cases": int(np.sum(y == 0)),
        "ambiguous_cases_excluded": len(ambiguous),
        "best_f1": best_f1,
        "best_at_precision_0_90": _best(rows, min_precision=0.90),
        "best_at_precision_0_95": _best(rows, min_precision=0.95),
        "best_at_recall_0_90": _best(rows, min_recall=0.90),
        "best_at_recall_0_95": _best(rows, min_recall=0.95),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"ENGINE_V2_OOF_BEST_F1={best_f1['f1']}")
    r95 = report["best_at_recall_0_95"]
    print(f"ENGINE_V2_OOF_R95_PRECISION={r95['precision'] if r95 else 'NONE'}")
    p95 = report["best_at_precision_0_95"]
    print(f"ENGINE_V2_OOF_P95_RECALL={p95['recall'] if p95 else 'NONE'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
