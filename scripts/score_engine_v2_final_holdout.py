from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np
from sklearn.linear_model import LogisticRegression

from procrun.evidence_retrieval_v2 import LocalSentenceTransformersEmbedder
from scripts.benchmark_engine_v2_relevance_gate import _noise_reject

RC1_CANDIDATE_ID = "engine-v2-rc1"
RC1_THRESHOLD = 0.48335432
RC1_EMBEDDING_MODEL = "intfloat/multilingual-e5-small"
RC1_RANDOM_STATE = 20260912


def _canonical_sha(value: Any) -> str:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"{path}: expected JSON object")
    return value


def _metrics(codes: list[str], y_true: np.ndarray, predicted: np.ndarray) -> dict[str, Any]:
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


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--development-sample", type=Path, required=True)
    parser.add_argument("--development-labels", type=Path, required=True)
    parser.add_argument("--holdout", type=Path, required=True)
    parser.add_argument("--holdout-labels", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    development = _load(args.development_sample)
    development_labels = _load(args.development_labels)
    holdout = _load(args.holdout)
    holdout_labels = _load(args.holdout_labels)

    if _canonical_sha(development) != development_labels["sample_canonical_sha256"]:
        raise RuntimeError("development sample drift")
    if holdout.get("candidate_id") != RC1_CANDIDATE_ID:
        raise RuntimeError("unexpected holdout candidate id")
    if bool(holdout.get("engine_output_present")):
        raise RuntimeError("holdout must be source-only before scoring")
    if int(holdout.get("development_overlap_count", -1)) != 0:
        raise RuntimeError("holdout overlaps development set")
    if _canonical_sha(holdout) != holdout_labels["holdout_canonical_sha256"]:
        raise RuntimeError("holdout labels do not match frozen holdout")

    development_positive = set(development_labels["positive_operation_codes"])
    development_ambiguous = set(development_labels["ambiguous_operation_codes"])
    development_cases = [case for case in development["cases"] if case["operation_code"] not in development_ambiguous]
    development_codes = [str(case["operation_code"]) for case in development_cases]
    development_texts = [f"{case.get('project_title') or ''}\n{case['project_scope_text']}".strip() for case in development_cases]
    y_train = np.asarray([1 if code in development_positive else 0 for code in development_codes], dtype=np.int64)

    holdout_positive = set(holdout_labels["positive_operation_codes"])
    holdout_ambiguous = set(holdout_labels["ambiguous_operation_codes"])
    holdout_cases = [case for case in holdout["cases"] if case["operation_code"] not in holdout_ambiguous]
    holdout_codes = [str(case["operation_code"]) for case in holdout_cases]
    holdout_texts = [f"{case.get('project_title') or ''}\n{case['project_scope_text']}".strip() for case in holdout_cases]
    y_test = np.asarray([1 if code in holdout_positive else 0 for code in holdout_codes], dtype=np.int64)

    embedder = LocalSentenceTransformersEmbedder(RC1_EMBEDDING_MODEL)
    train_vectors = np.asarray(embedder.encode(development_texts, kind="passage"), dtype=np.float64)
    test_vectors = np.asarray(embedder.encode(holdout_texts, kind="passage"), dtype=np.float64)

    model = LogisticRegression(C=1.0, class_weight="balanced", max_iter=4000, solver="liblinear", random_state=RC1_RANDOM_STATE)
    model.fit(train_vectors, y_train)
    probabilities = model.predict_proba(test_vectors)[:, 1]

    rejected = np.asarray([_noise_reject(text) for text in holdout_texts], dtype=bool)
    predicted = (probabilities >= RC1_THRESHOLD) & (~rejected)

    result = _metrics(holdout_codes, y_test, predicted)
    result.update({
        "schema_version": "engine-v2-rc1-final-holdout-result-v1",
        "candidate_id": RC1_CANDIDATE_ID,
        "threshold": RC1_THRESHOLD,
        "embedding_model": embedder.model_name,
        "development_sample_canonical_sha256": development_labels["sample_canonical_sha256"],
        "holdout_canonical_sha256": holdout_labels["holdout_canonical_sha256"],
        "holdout_positive_cases": int(np.sum(y_test == 1)),
        "holdout_negative_cases": int(np.sum(y_test == 0)),
        "holdout_ambiguous_cases_excluded": len(holdout_ambiguous),
        "noise_gate_rejected_total": int(np.sum(rejected)),
        "noise_gate_rejected_positives": int(np.sum(rejected & (y_test == 1))),
        "noise_gate_rejected_negatives": int(np.sum(rejected & (y_test == 0))),
        "pass_recall_0_95": float(result["recall"]) >= 0.95,
        "pass_precision_0_95": float(result["precision"]) >= 0.95,
        "final_gate_pass": float(result["recall"]) >= 0.95 and float(result["precision"]) >= 0.95,
    })
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")

    print(f"ENGINE_V2_FINAL_RECALL={result['recall']}")
    print(f"ENGINE_V2_FINAL_PRECISION={result['precision']}")
    print(f"ENGINE_V2_FINAL_F1={result['f1']}")
    print(f"ENGINE_V2_FINAL_GATE_PASS={str(result['final_gate_pass']).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
