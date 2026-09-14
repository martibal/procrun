from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

import numpy as np
from scipy.sparse import csr_matrix, hstack
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold

from procrun.evidence_retrieval_v2 import LocalSentenceTransformersEmbedder

Family = Literal["e5", "char", "hybrid"]
_C_VALUES = (0.1, 0.3, 1.0, 3.0, 10.0)
_HYBRID_WEIGHTS = (0.5, 1.0, 2.0)
_RANDOM_STATE = 20260912


@dataclass(frozen=True)
class Config:
    family: Family
    c_value: float
    embedding_weight: float = 1.0

    @property
    def name(self) -> str:
        if self.family == "hybrid":
            return f"hybrid:C={self.c_value}:ew={self.embedding_weight}"
        return f"{self.family}:C={self.c_value}"


def _canonical_sha(value: Any) -> str:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def _case_text(case: dict[str, Any]) -> str:
    return f"{case.get('project_title') or ''}\n{case['project_scope_text']}".strip()


def _configs() -> tuple[Config, ...]:
    configs = [Config("e5", c) for c in _C_VALUES]
    configs.extend(Config("char", c) for c in _C_VALUES)
    configs.extend(
        Config("hybrid", c, weight)
        for c in _C_VALUES
        for weight in _HYBRID_WEIGHTS
    )
    return tuple(configs)


def _vectorizer() -> TfidfVectorizer:
    return TfidfVectorizer(
        analyzer="char_wb",
        ngram_range=(3, 5),
        min_df=2,
        max_features=20000,
        sublinear_tf=True,
        lowercase=True,
    )


def _fit_predict(
    config: Config,
    texts: list[str],
    embeddings: np.ndarray,
    y: np.ndarray,
    train_idx: np.ndarray,
    test_idx: np.ndarray,
) -> np.ndarray:
    if config.family == "e5":
        x_train: Any = embeddings[train_idx]
        x_test: Any = embeddings[test_idx]
    else:
        vectorizer = _vectorizer()
        char_train = vectorizer.fit_transform([texts[i] for i in train_idx])
        char_test = vectorizer.transform([texts[i] for i in test_idx])
        if config.family == "char":
            x_train = char_train
            x_test = char_test
        else:
            dense_train = csr_matrix(embeddings[train_idx] * config.embedding_weight)
            dense_test = csr_matrix(embeddings[test_idx] * config.embedding_weight)
            x_train = hstack([char_train, dense_train], format="csr")
            x_test = hstack([char_test, dense_test], format="csr")

    model = LogisticRegression(
        C=config.c_value,
        class_weight="balanced",
        max_iter=5000,
        solver="liblinear",
        random_state=_RANDOM_STATE,
    )
    model.fit(x_train, y[train_idx])
    return np.asarray(model.predict_proba(x_test)[:, 1], dtype=np.float64)


def _metric(y: np.ndarray, probabilities: np.ndarray, threshold: float) -> dict[str, Any]:
    predicted = probabilities >= threshold
    tp = int(np.sum(predicted & (y == 1)))
    fp = int(np.sum(predicted & (y == 0)))
    fn = int(np.sum((~predicted) & (y == 1)))
    tn = int(np.sum((~predicted) & (y == 0)))
    recall = tp / (tp + fn) if tp + fn else 0.0
    precision = tp / (tp + fp) if tp + fp else 1.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {
        "threshold": float(threshold),
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "tn": tn,
        "recall": recall,
        "precision": precision,
        "f1": f1,
    }


def _metric_rank(metric: dict[str, Any]) -> tuple[float, ...]:
    recall = float(metric["recall"])
    precision = float(metric["precision"])
    passes = 1.0 if recall >= 0.95 and precision >= 0.95 else 0.0
    return (
        passes,
        min(recall, precision),
        float(metric["f1"]),
        recall,
        precision,
    )


def _select_threshold(y: np.ndarray, probabilities: np.ndarray) -> dict[str, Any]:
    thresholds = sorted({0.0, 1.0, *[float(value) for value in probabilities]})
    rows = [_metric(y, probabilities, threshold) for threshold in thresholds]
    return max(rows, key=_metric_rank)


def _inner_oof(
    config: Config,
    texts: list[str],
    embeddings: np.ndarray,
    y: np.ndarray,
    indices: np.ndarray,
) -> tuple[np.ndarray, dict[str, Any]]:
    local_y = y[indices]
    splitter = StratifiedKFold(n_splits=4, shuffle=True, random_state=_RANDOM_STATE)
    probabilities = np.zeros(len(indices), dtype=np.float64)
    for local_train, local_test in splitter.split(np.zeros(len(indices)), local_y):
        train_idx = indices[local_train]
        test_idx = indices[local_test]
        probabilities[local_test] = _fit_predict(
            config,
            texts,
            embeddings,
            y,
            train_idx,
            test_idx,
        )
    threshold = _select_threshold(local_y, probabilities)
    return probabilities, threshold


def _select_config(
    texts: list[str],
    embeddings: np.ndarray,
    y: np.ndarray,
    indices: np.ndarray,
) -> tuple[Config, dict[str, Any]]:
    candidates: list[tuple[Config, dict[str, Any]]] = []
    for config in _configs():
        _, metric = _inner_oof(config, texts, embeddings, y, indices)
        candidates.append((config, metric))
    return max(candidates, key=lambda item: (_metric_rank(item[1]), item[0].name))


def _rounded(metric: dict[str, Any]) -> dict[str, Any]:
    result = dict(metric)
    for key in ("threshold", "recall", "precision", "f1"):
        result[key] = round(float(result[key]), 6)
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sample", type=Path, required=True)
    parser.add_argument("--labels", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    sample: dict[str, Any] = json.loads(args.sample.read_text(encoding="utf-8"))
    labels: dict[str, Any] = json.loads(args.labels.read_text(encoding="utf-8"))
    if _canonical_sha(sample) != labels["sample_canonical_sha256"]:
        raise RuntimeError("RC2 source-only development sample drift")
    if sample.get("engine_output_present") is not False:
        raise RuntimeError("RC2 benchmark requires source-only sample")

    positives = set(labels["positive_operation_codes"])
    ambiguous = set(labels["ambiguous_operation_codes"])
    cases = [case for case in sample["cases"] if case["operation_code"] not in ambiguous]
    texts = [_case_text(case) for case in cases]
    codes = [str(case["operation_code"]) for case in cases]
    y = np.asarray([1 if code in positives else 0 for code in codes], dtype=np.int64)

    embedder = LocalSentenceTransformersEmbedder()
    embeddings = np.asarray(embedder.encode(texts, kind="passage"), dtype=np.float64)

    outer = StratifiedKFold(n_splits=5, shuffle=True, random_state=_RANDOM_STATE)
    outer_predictions = np.zeros(len(cases), dtype=bool)
    fold_results: list[dict[str, Any]] = []
    for fold, (train_idx, test_idx) in enumerate(outer.split(np.zeros(len(cases)), y), start=1):
        config, inner_metric = _select_config(texts, embeddings, y, train_idx)
        probabilities = _fit_predict(config, texts, embeddings, y, train_idx, test_idx)
        threshold = float(inner_metric["threshold"])
        outer_predictions[test_idx] = probabilities >= threshold
        fold_metric = _metric(y[test_idx], probabilities, threshold)
        fold_results.append(
            {
                "fold": fold,
                "config": config.name,
                "inner_selection_metric": _rounded(inner_metric),
                "outer_metric": _rounded(fold_metric),
            }
        )

    outer_probabilities = outer_predictions.astype(np.float64)
    outer_metric = _metric(y, outer_probabilities, 0.5)

    all_indices = np.arange(len(cases), dtype=np.int64)
    final_config, final_selection_metric = _select_config(
        texts,
        embeddings,
        y,
        all_indices,
    )

    report = {
        "schema_version": "engine-v2-rc2-nested-development-benchmark-v1",
        "evaluation": (
            "5-fold outer CV; 4-fold inner CV for model family, regularization and threshold; "
            "ambiguous cases excluded"
        ),
        "sample_canonical_sha256": labels["sample_canonical_sha256"],
        "embedding_model": embedder.model_name,
        "positive_cases": int(np.sum(y == 1)),
        "negative_cases": int(np.sum(y == 0)),
        "ambiguous_cases_excluded": len(ambiguous),
        "outer_metric": _rounded(outer_metric),
        "outer_gate_pass": (
            float(outer_metric["recall"]) >= 0.95
            and float(outer_metric["precision"]) >= 0.95
        ),
        "folds": fold_results,
        "full_development_selection": {
            "config": final_config.name,
            "selection_metric": _rounded(final_selection_metric),
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
        newline="",
    )
    print(f"ENGINE_V2_RC2_NESTED_RECALL={report['outer_metric']['recall']}")
    print(f"ENGINE_V2_RC2_NESTED_PRECISION={report['outer_metric']['precision']}")
    print(f"ENGINE_V2_RC2_NESTED_F1={report['outer_metric']['f1']}")
    print(f"ENGINE_V2_RC2_NESTED_GATE_PASS={str(report['outer_gate_pass']).lower()}")
    print(f"ENGINE_V2_RC2_SELECTED_CONFIG={final_config.name}")
    print(f"ENGINE_V2_RC2_SELECTED_THRESHOLD={report['full_development_selection']['selection_metric']['threshold']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
