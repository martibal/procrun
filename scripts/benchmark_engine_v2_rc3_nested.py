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

Family = Literal["charword", "hybrid2", "hybrid3"]
_C_VALUES = (0.3, 1.0, 3.0)
_EMBEDDING_WEIGHTS = (0.5, 1.0, 2.0)
_RANDOM_STATE = 20260912


@dataclass(frozen=True)
class Config:
    family: Family
    c_value: float
    embedding_weight: float = 1.0

    @property
    def name(self) -> str:
        if self.family == "charword":
            return f"charword:C={self.c_value}"
        return f"{self.family}:C={self.c_value}:ew={self.embedding_weight}"


def _canonical_sha(value: Any) -> str:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def _text(case: dict[str, Any]) -> str:
    return f"{case.get('project_title') or ''}\n{case.get('project_scope_text') or ''}".strip()


def _char_vectorizer() -> TfidfVectorizer:
    return TfidfVectorizer(
        analyzer="char_wb",
        ngram_range=(3, 5),
        min_df=2,
        max_features=25000,
        sublinear_tf=True,
        lowercase=True,
    )


def _word_vectorizer() -> TfidfVectorizer:
    return TfidfVectorizer(
        analyzer="word",
        ngram_range=(1, 2),
        min_df=2,
        max_features=30000,
        sublinear_tf=True,
        lowercase=True,
    )


def _configs() -> tuple[Config, ...]:
    result = [Config("charword", c) for c in _C_VALUES]
    result.extend(
        Config(family, c, weight)
        for family in ("hybrid2", "hybrid3")
        for c in _C_VALUES
        for weight in _EMBEDDING_WEIGHTS
    )
    return tuple(result)


def _fit_predict(
    config: Config,
    texts: list[str],
    embeddings: np.ndarray,
    y: np.ndarray,
    train_idx: np.ndarray,
    test_idx: np.ndarray,
) -> np.ndarray:
    train_texts = [texts[i] for i in train_idx]
    test_texts = [texts[i] for i in test_idx]
    char = _char_vectorizer()
    word = _word_vectorizer()
    char_train = char.fit_transform(train_texts)
    char_test = char.transform(test_texts)
    word_train = word.fit_transform(train_texts)
    word_test = word.transform(test_texts)

    if config.family == "charword":
        x_train = hstack([char_train, word_train], format="csr")
        x_test = hstack([char_test, word_test], format="csr")
    else:
        dense_train = csr_matrix(embeddings[train_idx] * config.embedding_weight)
        dense_test = csr_matrix(embeddings[test_idx] * config.embedding_weight)
        if config.family == "hybrid2":
            x_train = hstack([char_train, dense_train], format="csr")
            x_test = hstack([char_test, dense_test], format="csr")
        else:
            x_train = hstack([char_train, word_train, dense_train], format="csr")
            x_test = hstack([char_test, word_test, dense_test], format="csr")

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


def _rank_metric(metric: dict[str, Any]) -> tuple[float, ...]:
    recall = float(metric["recall"])
    precision = float(metric["precision"])
    return (
        1.0 if recall >= 0.95 and precision >= 0.95 else 0.0,
        min(recall, precision),
        float(metric["f1"]),
        recall,
        precision,
    )


def _select_threshold(y: np.ndarray, probabilities: np.ndarray) -> dict[str, Any]:
    thresholds = sorted({0.0, 1.0, *[float(value) for value in probabilities]})
    return max((_metric(y, probabilities, t) for t in thresholds), key=_rank_metric)


def _inner_oof(
    config: Config,
    texts: list[str],
    embeddings: np.ndarray,
    y: np.ndarray,
    indices: np.ndarray,
) -> dict[str, Any]:
    local_y = y[indices]
    splitter = StratifiedKFold(n_splits=4, shuffle=True, random_state=_RANDOM_STATE)
    probabilities = np.zeros(len(indices), dtype=np.float64)
    for local_train, local_test in splitter.split(np.zeros(len(indices)), local_y):
        train_idx = indices[local_train]
        test_idx = indices[local_test]
        probabilities[local_test] = _fit_predict(
            config, texts, embeddings, y, train_idx, test_idx
        )
    return _select_threshold(local_y, probabilities)


def _select_config(
    texts: list[str], embeddings: np.ndarray, y: np.ndarray, indices: np.ndarray
) -> tuple[Config, dict[str, Any]]:
    rows = [(config, _inner_oof(config, texts, embeddings, y, indices)) for config in _configs()]
    return max(rows, key=lambda item: (_rank_metric(item[1]), item[0].name))


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
        raise RuntimeError("RC3 development sample drift")
    if sample.get("engine_output_present") is not False:
        raise RuntimeError("RC3 benchmark requires source-only sample")

    positives = set(labels["positive_operation_codes"])
    ambiguous = set(labels["ambiguous_operation_codes"])
    cases = [case for case in sample["cases"] if str(case["operation_code"]) not in ambiguous]
    texts = [_text(case) for case in cases]
    codes = [str(case["operation_code"]) for case in cases]
    y = np.asarray([1 if code in positives else 0 for code in codes], dtype=np.int64)

    embedder = LocalSentenceTransformersEmbedder()
    embeddings = np.asarray(embedder.encode(texts, kind="passage"), dtype=np.float64)
    outer = StratifiedKFold(n_splits=5, shuffle=True, random_state=_RANDOM_STATE)
    outer_predictions = np.zeros(len(cases), dtype=bool)
    folds: list[dict[str, Any]] = []

    for fold, (train_idx, test_idx) in enumerate(outer.split(np.zeros(len(cases)), y), start=1):
        config, inner_metric = _select_config(texts, embeddings, y, train_idx)
        probabilities = _fit_predict(config, texts, embeddings, y, train_idx, test_idx)
        threshold = float(inner_metric["threshold"])
        outer_predictions[test_idx] = probabilities >= threshold
        folds.append(
            {
                "fold": fold,
                "config": config.name,
                "inner_selection_metric": _rounded(inner_metric),
                "outer_metric": _rounded(_metric(y[test_idx], probabilities, threshold)),
            }
        )

    outer_metric = _metric(y, outer_predictions.astype(np.float64), 0.5)
    all_indices = np.arange(len(cases), dtype=np.int64)
    final_config, final_metric = _select_config(texts, embeddings, y, all_indices)
    report = {
        "schema_version": "engine-v2-rc3-nested-development-benchmark-v1",
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
        "folds": folds,
        "full_development_selection": {
            "config": final_config.name,
            "selection_metric": _rounded(final_metric),
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
        newline="",
    )
    print(f"ENGINE_V2_RC3_OUTER_RECALL={report['outer_metric']['recall']}")
    print(f"ENGINE_V2_RC3_OUTER_PRECISION={report['outer_metric']['precision']}")
    print(f"ENGINE_V2_RC3_OUTER_GATE_PASS={str(report['outer_gate_pass']).lower()}")
    print(f"ENGINE_V2_RC3_FINAL_CONFIG={final_config.name}")
    print(f"ENGINE_V2_RC3_FINAL_THRESHOLD={report['full_development_selection']['selection_metric']['threshold']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
