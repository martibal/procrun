from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path

from procrun.classification_gold import (
    GoldTemplate,
    build_benchmark_manifest,
    empty_gold_template,
    freeze_gold_package,
    load_funding_projects_jsonl,
)


def _write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    encoded = json.dumps(value, indent=2, ensure_ascii=False, default=str) + "\n"
    path.write_text(encoded, encoding="utf-8")


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Prepare or freeze the blind A21 gold-standard package"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    prepare = sub.add_parser("prepare")
    prepare.add_argument("--projects-jsonl", required=True, type=Path)
    prepare.add_argument("--cutoff", required=True, type=date.fromisoformat)
    prepare.add_argument("--seed", required=True)
    prepare.add_argument("--manifest", required=True, type=Path)
    prepare.add_argument("--template", required=True, type=Path)
    prepare.add_argument("--size", type=int, default=200)

    freeze = sub.add_parser("freeze")
    freeze.add_argument("--manifest", required=True, type=Path)
    freeze.add_argument("--completed-gold", required=True, type=Path)
    freeze.add_argument("--output", required=True, type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if args.command == "prepare":
        projects = load_funding_projects_jsonl(args.projects_jsonl)
        manifest = build_benchmark_manifest(
            projects,
            cutoff_date=args.cutoff,
            selection_seed=args.seed,
            target_benchmark_size=args.size,
        )
        _write_json(args.manifest, manifest.model_dump(mode="json"))
        _write_json(args.template, empty_gold_template(manifest))
        print(f"benchmark_projects={len(manifest.projects)}")
        print(f"holdout_projects={len(manifest.holdout_operation_codes)}")
        print(f"manifest_sha256={manifest.manifest_sha256}")
        return 0

    from procrun.classification_gold import BenchmarkManifest

    manifest = BenchmarkManifest.model_validate_json(args.manifest.read_text(encoding="utf-8"))
    template = GoldTemplate.model_validate_json(args.completed_gold.read_text(encoding="utf-8"))
    package = freeze_gold_package(manifest, template)
    _write_json(args.output, package.model_dump(mode="json"))
    print(f"package_sha256={package.package_sha256}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
