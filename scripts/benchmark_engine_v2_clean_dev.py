from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from procrun.domain import FundingProject, TemporalProvenance
from procrun.evidence_retrieval_v2 import (
    LocalSentenceTransformersEmbedder,
    LocalSentenceTransformersReranker,
    SemanticRecallEngine,
)


def _canonical_sha(value: Any) -> str:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def _metrics(scores: dict[str, float], positives: set[str], negatives: set[str], threshold: float) -> dict[str, Any]:
    predicted = {code for code, score in scores.items() if score >= threshold}
    tp = len(predicted & positives)
    fp = len(predicted & negatives)
    fn = len(positives - predicted)
    tn = len(negatives - predicted)
    recall = tp / len(positives) if positives else 0.0
    precision = tp / (tp + fp) if tp + fp else 1.0
    fpr = fp / len(negatives) if negatives else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {
        "threshold": threshold,
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "tn": tn,
        "recall": round(recall, 6),
        "precision": round(precision, 6),
        "negative_case_fpr": round(fpr, 6),
        "f1": round(f1, 6),
        "false_negative_operation_codes": sorted(positives - predicted),
        "false_positive_operation_codes": sorted(predicted & negatives),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sample", type=Path, required=True)
    parser.add_argument("--labels", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    sample = json.loads(args.sample.read_text(encoding="utf-8"))
    labels = json.loads(args.labels.read_text(encoding="utf-8"))
    actual_sha = _canonical_sha(sample)
    expected_sha = labels["sample_canonical_sha256"]
    if actual_sha != expected_sha:
        raise RuntimeError(f"blind sample drift: expected {expected_sha}, got {actual_sha}")

    positives = set(labels["positive_operation_codes"])
    ambiguous = set(labels["ambiguous_operation_codes"])
    all_codes = {str(case["operation_code"]) for case in sample["cases"]}
    negatives = all_codes - positives - ambiguous
    if len(positives) != labels["positive_count"] or len(negatives) != labels["negative_count"]:
        raise RuntimeError("label counts do not match frozen blind adjudication")

    embedder = LocalSentenceTransformersEmbedder()
    reranker = LocalSentenceTransformersReranker()
    engine = SemanticRecallEngine(embedder, reranker)

    scores: dict[str, float] = {}
    span_failures = 0
    for case in sample["cases"]:
        project = FundingProject(
            operation_code=str(case["operation_code"]),
            first_seen_at=datetime(2026, 9, 12, tzinfo=timezone.utc),
            temporal_provenance=TemporalProvenance.RESOLVED,
            project_title=case.get("project_title"),
            project_scope_text=str(case["project_scope_text"]),
            region=case.get("region"),
            municipality=case.get("municipality"),
            nuts_code=case.get("nuts_code"),
            source_url=str(case["source_url"]),
        )
        candidates = engine.retrieve(
            project,
            candidate_limit=64,
            return_limit=12,
            minimum_semantic_score=-1.0,
        )
        for candidate in candidates:
            try:
                candidate.validate_against(project.project_scope_text)
            except ValueError:
                span_failures += 1
        scores[project.operation_code] = max((item.rerank_score for item in candidates), default=float("-inf"))

    finite_scores = sorted({score for score in scores.values() if score != float("-inf")})
    thresholds = [float("inf"), *finite_scores]
    evaluations = [_metrics(scores, positives, negatives, threshold) for threshold in thresholds]
    best_f1 = max(evaluations, key=lambda item: (item["f1"], item["precision"], item["recall"]))

    def best_at_precision(target: float) -> dict[str, Any] | None:
        eligible = [item for item in evaluations if item["precision"] >= target]
        if not eligible:
            return None
        return max(eligible, key=lambda item: (item["recall"], item["precision"], item["f1"]))

    report = {
        "schema_version": "engine-v2-clean-dev-benchmark-v1",
        "sample_canonical_sha256": actual_sha,
        "positive_cases": len(positives),
        "negative_cases": len(negatives),
        "ambiguous_cases_excluded": len(ambiguous),
        "embedding_model": embedder.model_name,
        "reranker_model": reranker.model_name,
        "exact_span_failures": span_failures,
        "best_f1": best_f1,
        "best_at_precision_0_90": best_at_precision(0.90),
        "best_at_precision_0_95": best_at_precision(0.95),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"ENGINE_V2_DEV_POSITIVES={len(positives)}")
    print(f"ENGINE_V2_DEV_NEGATIVES={len(negatives)}")
    print(f"ENGINE_V2_EXACT_SPAN_FAILURES={span_failures}")
    print(f"ENGINE_V2_BEST_F1_RECALL={best_f1['recall']}")
    print(f"ENGINE_V2_BEST_F1_PRECISION={best_f1['precision']}")
    p95 = report["best_at_precision_0_95"]
    print(f"ENGINE_V2_P95_RECALL={p95['recall'] if p95 else 'NONE'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
