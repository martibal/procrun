"""Customer-delivery service contracts used before any web implementation.

This module consumes only the frozen customer-safe read model. It never accepts collector payloads or
internal evidence envelopes. Supplier profile identifiers are opaque control-plane identifiers; no
natural-person identity is part of this contract.
"""

from __future__ import annotations

import csv
import io
from dataclasses import dataclass
from enum import StrEnum
from typing import Final

from pydantic import BaseModel, ConfigDict, Field, field_validator

from procrun.domain import ComponentState, ProjectState
from procrun.read_model import RunwayProject

DELIVERY_CONTRACT_VERSION: Final = "customer-delivery-v1"


class DeliveryInvariantError(ValueError):
    """Raised when customer delivery would broaden evidence or coverage claims."""


class EntitlementStatus(StrEnum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"


class SupplierProfile(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    account_subject: str = Field(min_length=1)
    organization_name: str = Field(min_length=1)
    country_code: str = Field(min_length=3, max_length=3)
    component_categories: tuple[str, ...] = ()
    cpv_prefixes: tuple[str, ...] = ()

    @field_validator("country_code")
    @classmethod
    def normalize_country(cls, value: str) -> str:
        normalized = value.strip().upper()
        if len(normalized) != 3 or not normalized.isalpha():
            raise ValueError("country_code must be a three-letter alphabetic code")
        return normalized

    @field_validator("component_categories", "cpv_prefixes")
    @classmethod
    def nonblank_unique(cls, values: tuple[str, ...]) -> tuple[str, ...]:
        normalized = tuple(value.strip() for value in values)
        if any(not value for value in normalized):
            raise ValueError("profile filters must not contain blank values")
        if len(set(normalized)) != len(normalized):
            raise ValueError("profile filters must be unique")
        return normalized


class OpportunityFeedItem(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    operation_code: str
    project_title: str | None
    state: ProjectState
    cutoff_date: str
    matched_categories: tuple[str, ...]
    matching_component_count: int = Field(ge=0)
    total_component_count: int = Field(ge=1)
    source_url: str
    content_hash: str
    delivery_contract_version: str = DELIVERY_CONTRACT_VERSION


def _matching_categories(project: RunwayProject, profile: SupplierProfile) -> tuple[str, ...]:
    wanted_categories = frozenset(profile.component_categories)
    wanted_cpv = profile.cpv_prefixes
    matched: set[str] = set()
    for component in project.components:
        if not wanted_categories and not wanted_cpv:
            matched.add(component.category)
            continue
        if component.category in wanted_categories:
            matched.add(component.category)
            continue
        for procurement in component.procurement_matches:
            if any(
                code.startswith(prefix)
                for code in procurement.cpv_codes
                for prefix in wanted_cpv
            ):
                matched.add(component.category)
                break
    return tuple(sorted(matched))


def _validate_ted_open_scope(project: RunwayProject) -> None:
    for component in project.components:
        if component.state is not ComponentState.OPEN:
            continue
        expected = f"No relevant procurement found in TED as of {component.cutoff_date.isoformat()}."
        if component.state_explanation != expected:
            raise DeliveryInvariantError(
                f"OPEN component {component.component_id} lacks exact TED-scoped explanation"
            )


def build_opportunity_feed(
    projects: tuple[RunwayProject, ...], profile: SupplierProfile
) -> tuple[OpportunityFeedItem, ...]:
    """Build deterministic supplier relevance without changing evidence state."""

    items: list[OpportunityFeedItem] = []
    for project in projects:
        _validate_ted_open_scope(project)
        matched = _matching_categories(project, profile)
        if not matched:
            continue
        items.append(
            OpportunityFeedItem(
                operation_code=project.operation_code,
                project_title=project.project_title,
                state=project.state,
                cutoff_date=project.cutoff_date.isoformat(),
                matched_categories=matched,
                matching_component_count=len(matched),
                total_component_count=len(project.components),
                source_url=project.source_url,
                content_hash=project.content_hash,
            )
        )
    state_order = {
        ProjectState.OPEN: 0,
        ProjectState.PARTIAL: 1,
        ProjectState.UNRESOLVED: 2,
        ProjectState.CLOSED: 3,
    }
    return tuple(
        sorted(
            items,
            key=lambda item: (
                state_order[item.state],
                -item.matching_component_count,
                item.operation_code,
            ),
        )
    )


def export_runway_csv(projects: tuple[RunwayProject, ...]) -> str:
    """Export only customer-safe component rows with explicit evidence/coverage semantics."""

    output = io.StringIO(newline="")
    writer = csv.writer(output, lineterminator="\n")
    writer.writerow(
        (
            "operation_code",
            "project_title",
            "project_state",
            "component_id",
            "component_category",
            "component_state",
            "cutoff_date",
            "state_explanation",
            "coverage_note",
            "source_url",
            "content_hash",
        )
    )
    for project in sorted(projects, key=lambda item: item.operation_code):
        _validate_ted_open_scope(project)
        for component in sorted(project.components, key=lambda item: item.component_id):
            writer.writerow(
                (
                    project.operation_code,
                    project.project_title or "",
                    project.state.value,
                    component.component_id,
                    component.category,
                    component.state.value,
                    component.cutoff_date.isoformat(),
                    component.state_explanation,
                    component.coverage_note,
                    project.source_url,
                    project.content_hash,
                )
            )
    return output.getvalue()
