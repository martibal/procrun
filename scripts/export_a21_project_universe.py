from __future__ import annotations

import argparse
import json
from pathlib import Path

from procrun.collectors.opencoesione import OpenCoesioneOperation, to_funding_projects
from procrun.collectors.opencoesione_live import collect_open_coesione_live
from procrun.domain import FundingProject
from procrun.ledger import content_sha256


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Export the approved raw FundingProject universe for blind A21 sampling. "
            "No component extraction, matching or classification is executed."
        )
    )
    parser.add_argument("--output", required=True, type=Path)
    return parser


def _a21_projects(
    operations: tuple[OpenCoesioneOperation, ...],
    mapped_projects: tuple[FundingProject, ...],
) -> tuple[FundingProject, ...]:
    if len(operations) != len(mapped_projects):
        raise RuntimeError("OpenCoesione operation/project mapping length mismatch")

    by_local_id: dict[str, tuple[OpenCoesioneOperation, FundingProject]] = {}
    duplicate_rows = 0

    for operation, project in zip(operations, mapped_projects, strict=True):
        existing = by_local_id.get(operation.operation_id)
        if existing is not None:
            duplicate_rows += 1
            if existing[0] != operation:
                raise RuntimeError(
                    "conflicting OpenCoesione rows share OperationLocalIdentifier: "
                    f"{operation.operation_id}"
                )
            continue

        by_local_id[operation.operation_id] = (
            operation,
            project.model_copy(update={"operation_code": operation.operation_id}),
        )

    projects = tuple(
        sorted(
            (project for _, project in by_local_id.values()),
            key=lambda item: item.operation_code,
        )
    )
    if not projects:
        raise RuntimeError("approved OpenCoesione route produced zero logical operations")

    print(f"raw_operations={len(operations)}")
    print(f"logical_operations={len(projects)}")
    print(f"collapsed_duplicate_rows={duplicate_rows}")
    return projects


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    batch = collect_open_coesione_live()
    mapped_projects = to_funding_projects(batch)
    projects = _a21_projects(batch.operations, mapped_projects)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    payloads = [project.model_dump(mode="json") for project in projects]
    with args.output.open("w", encoding="utf-8", newline="\n") as handle:
        for payload in payloads:
            handle.write(json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str))
            handle.write("\n")

    print(f"funding_projects={len(projects)}")
    print(f"source_sha256={batch.source_sha256}")
    print(f"universe_sha256={content_sha256(payloads)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
