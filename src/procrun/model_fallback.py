"""Fail-closed contract for the future local component-proposal model."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Literal

from pydantic import Field

from procrun.component_engine import (
    COMPONENT_RULE_VERSION,
    RULES,
    ComponentDomain,
    ComponentRule,
    EvidenceSpan,
    ExtractedComponent,
    ExtractionResult,
)
from procrun.domain import FundingProject, PurchaseComponent, StrictModel

MODEL_FALLBACK_CONTRACT_VERSION = "local-component-proposal-v1"
_SHA256_PATTERN = r"^[0-9a-f]{64}$"
_RULE_BY_KEY = {(rule.domain, rule.category): rule for rule in RULES}


class ModelFallbackError(ValueError):
    """Raised when local-model input/output violates the frozen fallback contract."""


class LocalModelIdentity(StrictModel):
    model_id: str = Field(min_length=1)
    artifact_sha256: str = Field(pattern=_SHA256_PATTERN)
    runtime: Literal["llama.cpp"] = "llama.cpp"


class ModelPromptSpan(StrictModel):
    start: int = Field(ge=0)
    end: int = Field(ge=0)
    text: str = Field(min_length=1)


class AllowedComponentCategory(StrictModel):
    domain: ComponentDomain
    category: str = Field(min_length=1)
    label: str = Field(min_length=1)


class LocalModelRequest(StrictModel):
    contract_version: Literal["local-component-proposal-v1"] = "local-component-proposal-v1"
    operation_code: str
    source_sha256: str = Field(pattern=_SHA256_PATTERN)
    domains: tuple[ComponentDomain, ...]
    unmatched_scope_spans: tuple[ModelPromptSpan, ...]
    allowed_categories: tuple[AllowedComponentCategory, ...]


class ModelComponentProposal(StrictModel):
    domain: ComponentDomain
    category: str = Field(min_length=1)
    start: int = Field(ge=0)
    end: int = Field(ge=0)
    source_text: str = Field(min_length=1)


class ModelProposalBatch(StrictModel):
    contract_version: Literal["local-component-proposal-v1"] = "local-component-proposal-v1"
    operation_code: str
    source_sha256: str = Field(pattern=_SHA256_PATTERN)
    model_identity: LocalModelIdentity
    proposals: tuple[ModelComponentProposal, ...] = ()


@dataclass(frozen=True)
class ModelFallbackResult:
    extraction: ExtractionResult
    accepted_proposals: tuple[ModelComponentProposal, ...]
    model_identity: LocalModelIdentity
    extractor_version: str


def _scope_sha256(project: FundingProject) -> str:
    return hashlib.sha256(project.project_scope_text.encode("utf-8")).hexdigest()


def _require_same_project(project: FundingProject, extraction: ExtractionResult) -> None:
    if project.operation_code != extraction.operation_code:
        raise ModelFallbackError("extraction operation_code does not match the funding project")


def _component_id(operation_code: str, domain: ComponentDomain, category: str) -> str:
    identity = f"{COMPONENT_RULE_VERSION}|{operation_code}|{domain.value}|{category}"
    digest = hashlib.sha256(identity.encode("utf-8")).hexdigest()
    return f"cmp_{digest[:20]}"


def _rule_for(domain: ComponentDomain, category: str) -> ComponentRule:
    rule = _RULE_BY_KEY.get((domain, category))
    if rule is None:
        raise ModelFallbackError(
            f"model proposal category is outside the frozen taxonomy: {domain.value}:{category}"
        )
    return rule


def _bare_category(component: ExtractedComponent) -> str:
    expected_prefix = f"{component.domain.value}:"
    if not component.component.category.startswith(expected_prefix):
        raise ModelFallbackError("existing component category is not namespaced to its domain")
    return component.component.category[len(expected_prefix) :]


def build_local_model_request(
    project: FundingProject,
    extraction: ExtractionResult,
) -> LocalModelRequest:
    """Build the minimal local-only model context from unmatched allowlisted scope spans."""

    _require_same_project(project, extraction)
    if not extraction.model_fallback_required or not extraction.unmatched_scope_spans:
        raise ModelFallbackError("local model fallback is not required for this extraction")

    selected_domains = frozenset(extraction.domains)
    allowed_categories = tuple(
        AllowedComponentCategory(
            domain=rule.domain,
            category=rule.category,
            label=rule.label,
        )
        for rule in sorted(RULES, key=lambda item: (item.domain.value, item.category))
        if rule.domain in selected_domains
    )
    prompt_spans = tuple(
        ModelPromptSpan(start=span.start, end=span.end, text=span.text)
        for span in extraction.unmatched_scope_spans
    )
    return LocalModelRequest(
        operation_code=project.operation_code,
        source_sha256=_scope_sha256(project),
        domains=extraction.domains,
        unmatched_scope_spans=prompt_spans,
        allowed_categories=allowed_categories,
    )


def validate_model_proposals(
    project: FundingProject,
    extraction: ExtractionResult,
    batch: ModelProposalBatch,
    *,
    expected_model: LocalModelIdentity,
) -> tuple[ModelComponentProposal, ...]:
    """Validate model output before it can become component evidence."""

    _require_same_project(project, extraction)
    if batch.operation_code != project.operation_code:
        raise ModelFallbackError("model batch operation_code does not match the funding project")
    if batch.source_sha256 != _scope_sha256(project):
        raise ModelFallbackError("model batch is not bound to the current project scope hash")
    if batch.model_identity != expected_model:
        raise ModelFallbackError("model identity or artifact SHA-256 does not match configuration")

    allowed_domains = frozenset(extraction.domains)
    unmatched = extraction.unmatched_scope_spans
    text = project.project_scope_text
    accepted: dict[
        tuple[ComponentDomain, str, int, int, str],
        ModelComponentProposal,
    ] = {}

    for proposal in batch.proposals:
        if proposal.domain not in allowed_domains:
            raise ModelFallbackError("model proposal uses a domain outside the extraction scope")
        _rule_for(proposal.domain, proposal.category)
        if proposal.start >= proposal.end or proposal.end > len(text):
            raise ModelFallbackError("model proposal span offsets are outside the project scope")
        if not proposal.source_text.strip():
            raise ModelFallbackError("model proposal source_text cannot be blank")
        if text[proposal.start : proposal.end] != proposal.source_text:
            raise ModelFallbackError(
                "model proposal source_text is not the exact cited source span"
            )
        if not any(
            proposal.start >= span.start and proposal.end <= span.end for span in unmatched
        ):
            raise ModelFallbackError(
                "model proposal must be contained inside a deterministic unmatched scope span"
            )

        key = (
            proposal.domain,
            proposal.category,
            proposal.start,
            proposal.end,
            proposal.source_text,
        )
        accepted[key] = proposal

    return tuple(
        accepted[key]
        for key in sorted(
            accepted,
            key=lambda item: (item[2], item[3], item[0].value, item[1], item[4]),
        )
    )


def _merge_proposal(
    components: dict[tuple[ComponentDomain, str], ExtractedComponent],
    operation_code: str,
    proposal: ModelComponentProposal,
) -> None:
    rule = _rule_for(proposal.domain, proposal.category)
    key = (proposal.domain, proposal.category)
    span = EvidenceSpan(
        start=proposal.start,
        end=proposal.end,
        text=proposal.source_text,
        matched_phrases=(),
    )
    current = components.get(key)

    if current is None:
        component = PurchaseComponent(
            component_id=_component_id(operation_code, proposal.domain, proposal.category),
            operation_code=operation_code,
            category=f"{proposal.domain.value}:{proposal.category}",
            description=rule.label,
            scope_evidence=proposal.source_text,
        )
        components[key] = ExtractedComponent(
            component=component,
            domain=proposal.domain,
            evidence_spans=(span,),
            cpv_prefixes=rule.cpv_prefixes,
        )
        return

    spans = {
        (item.start, item.end, item.text): item
        for item in current.evidence_spans
    }
    spans[(span.start, span.end, span.text)] = span
    components[key] = ExtractedComponent(
        component=current.component,
        domain=current.domain,
        evidence_spans=tuple(
            spans[key] for key in sorted(spans, key=lambda item: (item[0], item[1], item[2]))
        ),
        cpv_prefixes=current.cpv_prefixes,
    )


def apply_model_proposals(
    project: FundingProject,
    extraction: ExtractionResult,
    batch: ModelProposalBatch,
    *,
    expected_model: LocalModelIdentity,
) -> ModelFallbackResult:
    """Merge validated proposals without allowing the model to assign procurement state."""

    accepted = validate_model_proposals(
        project,
        extraction,
        batch,
        expected_model=expected_model,
    )
    components = {
        (item.domain, _bare_category(item)): item for item in extraction.components
    }
    for proposal in accepted:
        _merge_proposal(components, project.operation_code, proposal)

    handled_ranges = {
        (span.start, span.end)
        for span in extraction.unmatched_scope_spans
        if any(
            proposal.start >= span.start and proposal.end <= span.end for proposal in accepted
        )
    }
    remaining = tuple(
        span
        for span in extraction.unmatched_scope_spans
        if (span.start, span.end) not in handled_ranges
    )
    merged_components = tuple(
        components[key]
        for key in sorted(components, key=lambda item: (item[0].value, item[1]))
    )
    merged = ExtractionResult(
        operation_code=extraction.operation_code,
        domains=extraction.domains,
        components=merged_components,
        unmatched_scope_spans=remaining,
        model_fallback_required=bool(remaining),
        rule_version=extraction.rule_version,
    )
    extractor_version = (
        f"{extraction.rule_version}+{MODEL_FALLBACK_CONTRACT_VERSION}+"
        f"{expected_model.model_id}@sha256:{expected_model.artifact_sha256}"
    )
    return ModelFallbackResult(
        extraction=merged,
        accepted_proposals=accepted,
        model_identity=expected_model,
        extractor_version=extractor_version,
    )
