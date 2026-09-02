"""Fail-closed contract for the future local component-proposal model."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Literal

from pydantic import Field, computed_field

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
MODEL_CATEGORY_GUIDANCE_VERSION = "component-model-guidance-v1"
_SHA256_PATTERN = r"^[0-9a-f]{64}$"
_RULE_BY_KEY = {(rule.domain, rule.category): rule for rule in RULES}

_MODEL_CATEGORY_SELECTION_RULES: dict[tuple[ComponentDomain, str], str] = {
    (ComponentDomain.WATER_WASTEWATER, "civil_works"): (
        "Select for physical construction or structural works in water/wastewater assets. "
        "Do not use for treatment process equipment, pumps, valves, electrical systems, "
        "automation, monitoring, sludge handling, or design services."
    ),
    (ComponentDomain.WATER_WASTEWATER, "treatment_equipment"): (
        "Select for equipment or process units whose primary function is water or wastewater "
        "treatment, including disinfection, filtration, separation, or treatment reactors. "
        "Do not use for pumps, valves, generic civil works, monitoring-only instruments, "
        "or controls."
    ),
    (ComponentDomain.WATER_WASTEWATER, "pumps"): (
        "Select for pumps, pumping units, pumping systems, or equipment whose primary function is "
        "moving water or wastewater. Do not use for valves, treatment units, or generic machinery."
    ),
    (ComponentDomain.WATER_WASTEWATER, "valves"): (
        "Select for valves and flow-isolation or flow-regulation valve assemblies. "
        "Do not use for pumps, piping in general, or automation systems merely controlling a valve."
    ),
    (ComponentDomain.WATER_WASTEWATER, "electrical"): (
        "Select for electrical installations, switchboards, power distribution, cabling, or other "
        "electrical supply systems. Do not use for automation/control logic or monitoring "
        "instruments."
    ),
    (ComponentDomain.WATER_WASTEWATER, "automation_control"): (
        "Select for systems whose primary function is automatic or remote command and control, "
        "including PLC, SCADA, telemetry used for operation, and control logic. "
        "Prefer monitoring when the named item only measures, senses, observes, or records."
    ),
    (ComponentDomain.WATER_WASTEWATER, "monitoring"): (
        "Select for instruments or systems whose primary function is measurement, sensing, "
        "analysis, observation, or condition monitoring. Prefer automation_control when the named "
        "system actively commands or remotely controls process operation."
    ),
    (ComponentDomain.WATER_WASTEWATER, "sludge_handling"): (
        "Select for equipment or scoped systems dedicated to sludge treatment, dewatering, "
        "handling, storage, or transfer. Do not use for general wastewater treatment equipment "
        "without a sludge-specific function."
    ),
    (ComponentDomain.WATER_WASTEWATER, "engineering_design"): (
        "Select for engineering design, execution design, or technical design services as the "
        "purchasable scope. Do not use for the physical equipment or works that a design concerns."
    ),
    (ComponentDomain.RAIL_TRANSPORT, "civil_works"): (
        "Select for railway construction, structures, earthworks, or other physical rail civil "
        "works. Do not use for track-specific works, signalling, telecoms, traction power, "
        "stations, crossings, studies, or rolling equipment when those are explicitly named."
    ),
    (ComponentDomain.RAIL_TRANSPORT, "track"): (
        "Select for railway track, rails, sleepers, ballast, track renewal, or track-formation "
        "works. Do not use for signalling, traction power, stations, or generic civil works when "
        "track is not the named package."
    ),
    (ComponentDomain.RAIL_TRANSPORT, "signalling"): (
        "Select for train-control and railway-safety signalling systems, including interlocking, "
        "train detection, axle counters, signals, and signalling control equipment. "
        "Do not use for traction electrical supply, catenary, or general telecommunications."
    ),
    (ComponentDomain.RAIL_TRANSPORT, "telecoms"): (
        "Select for railway communications networks and telecom equipment such as operational "
        "radio or data communications. Do not use for signalling logic or traction power systems."
    ),
    (ComponentDomain.RAIL_TRANSPORT, "electrification_catenary"): (
        "Select for railway traction-power supply and electrification, including traction "
        "substations, traction transformers, overhead line, and catenary. Do not use for signalling "
        "or station building electrical services."
    ),
    (ComponentDomain.RAIL_TRANSPORT, "stations"): (
        "Select when the named purchasable scope is a railway station or station-specific "
        "construction. Do not use merely because other rail equipment is located at a station."
    ),
    (ComponentDomain.RAIL_TRANSPORT, "crossings"): (
        "Select for level crossings and their dedicated crossing works or systems. "
        "Do not use for generic road/rail civil works without an explicit crossing."
    ),
    (ComponentDomain.RAIL_TRANSPORT, "engineering_studies"): (
        "Select for railway engineering studies, feasibility/technical studies, or study services "
        "as the purchasable scope. Do not use for implementation works or equipment."
    ),
    (ComponentDomain.RAIL_TRANSPORT, "rolling_equipment"): (
        "Select for rolling stock or movable railway operational equipment. "
        "Do not use for fixed track, signalling, traction-power, or station infrastructure."
    ),
    (ComponentDomain.PORTS_COASTAL, "marine_works"): (
        "Select for structural marine or harbour works such as breakwaters, moles, quays, "
        "revetments, armour, and other works built in or directly against the marine environment. "
        "Prefer civil_works for general landside/support construction."
    ),
    (ComponentDomain.PORTS_COASTAL, "dredging"): (
        "Select for dredging, seabed excavation, sediment removal, or navigation-depth works. "
        "Do not use for breakwater/quay construction or generic marine works when dredging "
        "is not named."
    ),
    (ComponentDomain.PORTS_COASTAL, "coastal_protection"): (
        "Select for works whose primary purpose is shoreline or coastal defence/protection. "
        "Prefer marine_works for harbour structures whose primary role is port infrastructure."
    ),
    (ComponentDomain.PORTS_COASTAL, "shore_power"): (
        "Select for electrical shore-power or onshore power supply systems serving berthed "
        "vessels. Do not use for general port electrical installations or photovoltaic generation."
    ),
    (ComponentDomain.PORTS_COASTAL, "photovoltaic"): (
        "Select for photovoltaic generation systems or solar PV equipment in the port domain. "
        "Do not use for shore power or generic electrical infrastructure."
    ),
    (ComponentDomain.PORTS_COASTAL, "civil_works"): (
        "Select for general landside port construction or service infrastructure that is not a "
        "marine structure. Prefer marine_works for quays, breakwaters, moles, revetments, "
        "and similar marine structural works."
    ),
    (ComponentDomain.PORTS_COASTAL, "monitoring"): (
        "Select for port/coastal measurement, sensing, surveillance, or monitoring systems. "
        "Do not use for cargo-handling machinery or general port equipment without a "
        "monitoring role."
    ),
    (ComponentDomain.PORTS_COASTAL, "equipment"): (
        "Select for discrete port operational equipment such as cranes, lifting/cargo-handling "
        "machinery, fenders, and other non-structural harbour equipment. "
        "Do not use for breakwaters, quays, dredging, or other structural marine works."
    ),
    (ComponentDomain.ENERGY_EFFICIENCY, "building_works"): (
        "Select for general building rehabilitation or construction works undertaken for energy "
        "efficiency when no narrower frozen energy category is explicitly named. "
        "Prefer HVAC, envelope, lighting, photovoltaic, metering, or controls when those are named."
    ),
    (ComponentDomain.ENERGY_EFFICIENCY, "hvac"): (
        "Select for heating, ventilation, air-conditioning, heat pumps, heat recovery, and related "
        "thermal-conditioning equipment. Do not use for building envelope, lighting, metering, "
        "or BMS."
    ),
    (ComponentDomain.ENERGY_EFFICIENCY, "bms_control"): (
        "Select for building management, supervisory control, automation, or central technical "
        "management systems controlling building energy systems. "
        "Prefer metering when the named item only measures consumption."
    ),
    (ComponentDomain.ENERGY_EFFICIENCY, "metering"): (
        "Select for meters, sub-metering, or systems whose primary function is measuring "
        "energy use. Prefer bms_control when the named system actively supervises or controls "
        "building systems."
    ),
    (ComponentDomain.ENERGY_EFFICIENCY, "photovoltaic"): (
        "Select for photovoltaic panels, arrays, inverters, or solar PV generation systems. "
        "Do not use for generic electrical works or non-PV renewable equipment."
    ),
    (ComponentDomain.ENERGY_EFFICIENCY, "lighting"): (
        "Select for lighting systems, luminaires, LED retrofits, or lighting controls when "
        "lighting is the named purchasable package. Do not use for general electrical installations."
    ),
    (ComponentDomain.ENERGY_EFFICIENCY, "insulation_envelope"): (
        "Select for thermal envelope improvements such as insulation, windows, frames, glazing, "
        "facades, roofs, or doors where thermal performance is the component function. "
        "Do not use for HVAC equipment or general building works when envelope work is explicit."
    ),
    (ComponentDomain.ENERGY_EFFICIENCY, "engineering_audit"): (
        "Select for energy audits, energy-efficiency engineering studies, or specialist "
        "design/audit services. Do not use for the physical retrofit equipment or works identified "
        "by the audit."
    ),
    (ComponentDomain.RESILIENCE_FIRE, "sensors_cameras"): (
        "Select for sensing, detection, thermal-imaging, camera, or surveillance equipment. "
        "For remotely operated or aerial platforms, use this category when sensing/imaging is the "
        "defining named capability; use vehicles when the vehicle itself is the primary component."
    ),
    (ComponentDomain.RESILIENCE_FIRE, "communications"): (
        "Select for radio, voice/data communications, dispatch communications networks, or "
        "dedicated communications equipment. Do not use for incident-command software whose "
        "primary function is coordination rather than communications transport."
    ),
    (ComponentDomain.RESILIENCE_FIRE, "vehicles"): (
        "Select for response vehicles or mobile platforms when the vehicle itself is the primary "
        "purchasable component. Prefer sensors_cameras when a platform is named principally as a "
        "carrier for sensing, cameras, or thermal imaging."
    ),
    (ComponentDomain.RESILIENCE_FIRE, "ppe_equipment"): (
        "Select for personal protective equipment and physical firefighting/response equipment "
        "used by responders. Do not use for vehicles, communications, sensors, or command software."
    ),
    (ComponentDomain.RESILIENCE_FIRE, "civil_works"): (
        "Select for physical construction or structural works supporting resilience/fire "
        "capability. Do not use for operational equipment, vehicles, communications, sensors, or "
        "command systems."
    ),
    (ComponentDomain.RESILIENCE_FIRE, "command_control"): (
        "Select for command, dispatch, incident-management, operational coordination, or decision-"
        "support platforms/systems. Do not use for communications transport alone, sensors, "
        "or vehicles."
    ),
}


def _validate_model_category_selection_rules() -> None:
    taxonomy_keys = set(_RULE_BY_KEY)
    guidance_keys = set(_MODEL_CATEGORY_SELECTION_RULES)
    if taxonomy_keys != guidance_keys:
        missing = sorted(
            f"{domain.value}:{category}" for domain, category in taxonomy_keys - guidance_keys
        )
        extra = sorted(
            f"{domain.value}:{category}" for domain, category in guidance_keys - taxonomy_keys
        )
        raise RuntimeError(
            f"model category guidance must cover the exact frozen taxonomy; "
            f"missing={missing}, extra={extra}"
        )


_validate_model_category_selection_rules()


class ModelFallbackError(ValueError):
    """Raised when local-model input/output violates the frozen fallback contract."""


def model_category_selection_rule(domain: ComponentDomain, category: str) -> str:
    """Return the frozen model-facing selection rule for one taxonomy category."""

    guidance = _MODEL_CATEGORY_SELECTION_RULES.get((domain, category))
    if guidance is None:
        raise ModelFallbackError(
            f"model category guidance is outside the frozen taxonomy: {domain.value}:{category}"
        )
    return guidance


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

    @computed_field
    @property
    def selection_rule(self) -> str:
        """Frozen semantic boundary supplied to the local model with this category."""

        return model_category_selection_rule(self.domain, self.category)


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
