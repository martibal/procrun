from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np
from scipy.sparse import csr_matrix, hstack
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

from procrun.evidence_retrieval_v2 import LocalSentenceTransformersEmbedder

EXPECTED_HOLDOUT_SHA = "c1f8bfdee38f0f0b4b9f78da2bc196ad16db8af8f614b5f3fef5e558c58de758"


def _canonical_sha(value: Any) -> str:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def _text(case: dict[str, Any]) -> str:
    return f"{case.get('project_title') or ''}\n{case.get('project_scope_text') or ''}".strip()


def _vectorizer() -> TfidfVectorizer:
    return TfidfVectorizer(
        analyzer="char_wb",
        ngram_range=(3, 5),
        min_df=2,
        max_features=20000,
        sublinear_tf=True,
        lowercase=True,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--development", type=Path, required=True)
    parser.add_argument("--development-labels", type=Path, required=True)
    parser.add_argument("--holdout", type=Path, required=True)
    parser.add_argument("--holdout-labels", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    dev = json.loads(args.development.read_text(encoding="utf-8"))
    dev_labels = json.loads(args.development_labels.read_text(encoding="utf-8"))
    holdout = json.loads(args.holdout.read_text(encoding="utf-8"))
    hold_labels = json.loads(args.holdout_labels.read_text(encoding="utf-8"))
    candidate = json.loads(args.candidate.read_text(encoding="utf-8"))

    if _canonical_sha(dev) != dev_labels["sample_canonical_sha256"]:
        raise RuntimeError("RC2 development drift")
    if _canonical_sha(holdout) != EXPECTED_HOLDOUT_SHA:
        raise RuntimeError("RC2 final holdout drift")
    if hold_labels["holdout_canonical_sha256"] != EXPECTED_HOLDOUT_SHA:
        raise RuntimeError("RC2 final labels do not match holdout")

    positives = set(dev_labels["positive_operation_codes"])
    ambiguous = set(dev_labels["ambiguous_operation_codes"])
    dev_cases = [
        case
        for case in dev["cases"]
        if str(case["operation_code"]) not in ambiguous
    ]
    x_dev_text = [_text(case) for case in dev_cases]
    y_dev = np.asarray(
        [1 if str(case["operation_code"]) in positives else 0 for case in dev_cases],
        dtype=np.int64,
    )

    h_pos = set(hold_labels["positive_operation_codes"])
    h_neg = set(hold_labels["negative_operation_codes"])
    hold_cases = [
        case
        for case in holdout["cases"]
        if str(case["operation_code"]) in h_pos | h_neg
    ]
    hold_codes = [str(case["operation_code"]) for case in hold_cases]
    x_hold_text = [_text(case) for case in hold_cases]
    y_hold = np.asarray(
        [1 if code in h_pos else 0 for code in hold_codes],
        dtype=np.int64,
    )

    embedder = LocalSentenceTransformersEmbedder(candidate["model"]["embedding_model"])
    dev_emb = np.asarray(
        embedder.encode(x_dev_text, kind="passage"),
        dtype=np.float64,
    )
    hold_emb = np.asarray(
        embedder.encode(x_hold_text, kind="passage"),
        dtype=np.float64,
    )
    weight = float(candidate["model"]["embedding_weight"])

    vectorizer = _vectorizer()
    dev_char = vectorizer.fit_transform(x_dev_text)
    hold_char = vectorizer.transform(x_hold_text)
    x_dev = hstack([dev_char, csr_matrix(dev_emb * weight)], format="csr")
    x_hold = hstack([hold_char, csr_matrix(hold_emb * weight)], format="csr")

    cfg = candidate["model"]["logistic_regression"]
    model = LogisticRegression(
        C=float(cfg["C"]),
        class_weight=str(cfg["class_weight"]),
        max_iter=int(cfg["max_iter"]),
        solver=str(cfg["solver"]),
        random_state=int(cfg["random_state"]),
    )
    model.fit(x_dev, y_dev)
    probability = model.predict_proba(x_hold)[:, 1]
    threshold = float(candidate["model"]["decision_threshold"])
    predicted = probability >= threshold

    tp_mask = predicted & (y_hold == 1)
    fp_mask = predicted & (y_hold == 0)
    fn_mask = (~predicted) & (y_hold == 1)
    tn_mask = (~predicted) & (y_hold == 0)
    tp, fp, fn, tn = map(
        int,
        [tp_mask.sum(), fp_mask.sum(), fn_mask.sum(), tn_mask.sum()],
    )
    recall = tp / (tp + fn)
    precision = tp / (tp + fp)
    f1 = 2 * recall * precision / (recall + precision)
    final_gate = recall >= 0.95 and precision >= 0.95

    result = {
        "schema_version": "engine-v2-rc2-final-holdout-result-v1",
        "candidate_id": candidate["candidate_id"],
        "holdout_canonical_sha256": EXPECTED_HOLDOUT_SHA,
        "evaluated_cases": len(hold_cases),
        "positive_cases": len(h_pos),
        "negative_cases": len(h_neg),
        "ambiguous_cases_excluded": int(hold_labels["ambiguous_count"]),
        "threshold": threshold,
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "tn": tn,
        "recall": round(recall, 6),
        "precision": round(precision, 6),
        "f1": round(f1, 6),
        "false_positive_operation_codes": [
            hold_codes[i] for i in np.flatnonzero(fp_mask)
        ],
        "false_negative_operation_codes": [
            hold_codes[i] for i in np.flatnonzero(fn_mask)
        ],
        "final_gate_pass": final_gate,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"ENGINE_V2_RC2_FINAL_RECALL={result['recall']}")
    print(f"ENGINE_V2_RC2_FINAL_PRECISION={result['precision']}")
    print(f"ENGINE_V2_RC2_FINAL_F1={result['f1']}")
    print(f"ENGINE_V2_RC2_FINAL_GATE_PASS={str(final_gate).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
