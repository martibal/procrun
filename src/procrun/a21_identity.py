"""Fail-closed source identity normalization for A21 benchmark construction."""

from __future__ import annotations

from procrun.collectors.opencoesione import OpenCoesioneOperation
from procrun.domain import FundingProject


def a21_projects_by_local_operation_id(
    operations: tuple[OpenCoesioneOperation, ...],
    mapped_projects: tuple[FundingProject, ...],
) -> tuple[FundingProject, ...]:
    """Return one logical project per OpenCoesione OperationLocalIdentifier.

    Exact repeated source rows are collapsed. If the same local identifier ever
    carries different source content, the whole A21 universe fails closed.
    """
    if len(operations) != len(mapped_projects):
        raise RuntimeError("OpenCoesione operation/project mapping length mismatch")

    by_local_id: dict[str, tuple[OpenCoesioneOperation, FundingProject]] = {}

    for operation, project in zip(operations, mapped_projects, strict=True):
        existing = by_local_id.get(operation.operation_id)
        if existing is not None:
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
    return projects
