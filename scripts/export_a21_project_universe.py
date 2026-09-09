from __future__ import annotations

import argparse
import json
from pathlib import Path

from procrun.a21_identity import a21_projects_by_local_operation_id
from procrun.collectors.opencoesione import to_funding_projects
from procrun.collectors.opencoesione_live import collect_open_coesione_live
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


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    batch = collect_open_coesione_live()
    mapped_projects = to_funding_projects(batch)
    projects = a21_projects_by_local_operation_id(batch.operations, mapped_projects)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    payloads = [project.model_dump(mode="json") for project in projects]
    with args.output.open("w", encoding="utf-8", newline="\n") as handle:
        for payload in payloads:
            handle.write(json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str))
            handle.write("\n")

    print(f"raw_operations={len(batch.operations)}")
    print(f"logical_operations={len(projects)}")
    print(f"collapsed_duplicate_rows={len(batch.operations) - len(projects)}")
    print(f"funding_projects={len(projects)}")
    print(f"source_sha256={batch.source_sha256}")
    print(f"universe_sha256={content_sha256(payloads)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
