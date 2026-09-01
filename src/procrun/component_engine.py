"""Deterministic Phase C component extraction and frozen taxonomy."""

from __future__ import annotations

import hashlib
import re
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from enum import StrEnum

from procrun.domain import FundingProject, PurchaseComponent

COMPONENT_RULE_VERSION = "component-taxonomy-v1"


class ComponentDomain(StrEnum):
    WATER_WASTEWATER = "water_wastewater"
    RAIL_TRANSPORT = "rail_transport"
    PORTS_COASTAL = "ports_coastal"
    ENERGY_EFFICIENCY = "energy_efficiency"
    RESILIENCE_FIRE = "resilience_fire"


@dataclass(frozen=True)
class ComponentRule:
    domain: ComponentDomain
    category: str
    label: str
    phrases: tuple[str, ...]
    cpv_prefixes: tuple[str, ...] = ()


@dataclass(frozen=True)
class EvidenceSpan:
    start: int
    end: int
    text: str
    matched_phrases: tuple[str, ...]


@dataclass(frozen=True)
class ExtractedComponent:
    component: PurchaseComponent
    domain: ComponentDomain
    evidence_spans: tuple[EvidenceSpan, ...]
    cpv_prefixes: tuple[str, ...]


@dataclass(frozen=True)
class ExtractionResult:
    operation_code: str
    domains: tuple[ComponentDomain, ...]
    components: tuple[ExtractedComponent, ...]
    unmatched_scope_spans: tuple[EvidenceSpan, ...]
    model_fallback_required: bool
    rule_version: str = COMPONENT_RULE_VERSION


RULES: tuple[ComponentRule, ...] = (
    ComponentRule(
        ComponentDomain.WATER_WASTEWATER,
        "civil_works",
        "Civil works",
        ("obras civis", "construção civil", "civil works"),
        ("45", "452"),
    ),
    ComponentRule(
        ComponentDomain.WATER_WASTEWATER,
        "treatment_equipment",
        "Treatment equipment",
        ("equipamento de tratamento", "equipamentos de tratamento", "treatment equipment"),
        ("429123",),
    ),
    ComponentRule(
        ComponentDomain.WATER_WASTEWATER,
        "pumps",
        "Pumps and pumping systems",
        ("bombas", "sistema de bombagem", "sistemas de bombagem", "pumps", "pumping system"),
        ("42122",),
    ),
    ComponentRule(
        ComponentDomain.WATER_WASTEWATER,
        "valves",
        "Valves",
        ("válvulas", "valvulas", "valves"),
        ("42131",),
    ),
    ComponentRule(
        ComponentDomain.WATER_WASTEWATER,
        "electrical",
        "Electrical systems",
        (
            "instalações elétricas",
            "instalações eléctricas",
            "instalacoes eletricas",
            "electrical installations",
            "quadros elétricos",
        ),
        ("31", "4531"),
    ),
    ComponentRule(
        ComponentDomain.WATER_WASTEWATER,
        "automation_control",
        "Automation and control",
        (
            "automação",
            "automacao",
            "automatização",
            "automatizacao",
            "sistema de controlo",
            "sistemas de controlo",
            "automation",
            "control system",
            "scada",
        ),
    ),
    ComponentRule(
        ComponentDomain.WATER_WASTEWATER,
        "monitoring",
        "Monitoring",
        ("monitorização", "monitorizacao", "monitoramento", "monitoring"),
        ("384", "389"),
    ),
    ComponentRule(
        ComponentDomain.WATER_WASTEWATER,
        "sludge_handling",
        "Sludge handling",
        ("tratamento de lamas", "gestão de lamas", "gestao de lamas", "sludge handling"),
        ("905136",),
    ),
    ComponentRule(
        ComponentDomain.WATER_WASTEWATER,
        "engineering_design",
        "Engineering and design",
        (
            "projeto de execução",
            "projecto de execução",
            "estudos e projetos",
            "estudos e projectos",
            "projeto de engenharia",
            "engineering design",
        ),
        ("7132",),
    ),
    ComponentRule(
        ComponentDomain.RAIL_TRANSPORT,
        "civil_works",
        "Rail civil works",
        ("obras ferroviárias", "obras ferroviarias", "railway works", "construção ferroviária"),
        ("452341",),
    ),
    ComponentRule(
        ComponentDomain.RAIL_TRANSPORT,
        "track",
        "Track works",
        ("via férrea", "via ferrea", "renovação de via", "renovacao de via", "railway track"),
        ("45234116",),
    ),
    ComponentRule(
        ComponentDomain.RAIL_TRANSPORT,
        "signalling",
        "Rail signalling",
        ("sinalização ferroviária", "sinalizacao ferroviaria", "sinalização", "signalling"),
        ("34942", "45234115"),
    ),
    ComponentRule(
        ComponentDomain.RAIL_TRANSPORT,
        "telecoms",
        "Rail telecommunications",
        ("telecomunicações", "telecomunicacoes", "telecommunications", "gsm-r"),
        ("325",),
    ),
    ComponentRule(
        ComponentDomain.RAIL_TRANSPORT,
        "electrification_catenary",
        "Electrification and catenary",
        ("catenária", "catenaria", "eletrificação", "eletrificacao", "electrification"),
        ("45234160",),
    ),
    ComponentRule(
        ComponentDomain.RAIL_TRANSPORT,
        "stations",
        "Stations",
        ("estação ferroviária", "estacao ferroviaria", "estações ferroviárias", "railway station"),
        ("452133",),
    ),
    ComponentRule(
        ComponentDomain.RAIL_TRANSPORT,
        "crossings",
        "Level crossings",
        ("passagem de nível", "passagens de nível", "passagem de nivel", "level crossing"),
        ("45234140",),
    ),
    ComponentRule(
        ComponentDomain.RAIL_TRANSPORT,
        "engineering_studies",
        "Engineering studies",
        ("estudo prévio", "estudo previo", "estudos de engenharia", "engineering study"),
        ("713",),
    ),
    ComponentRule(
        ComponentDomain.RAIL_TRANSPORT,
        "rolling_equipment",
        "Rail equipment and rolling stock",
        (
            "material circulante",
            "rolling stock",
            "equipamento ferroviário",
            "equipamento ferroviario",
        ),
        ("346",),
    ),
    ComponentRule(
        ComponentDomain.PORTS_COASTAL,
        "marine_works",
        "Marine works",
        ("obras marítimas", "obras maritimas", "marine works", "infraestruturas portuárias"),
        ("45244",),
    ),
    ComponentRule(
        ComponentDomain.PORTS_COASTAL,
        "dredging",
        "Dredging",
        ("dragagem", "dragagens", "dredging"),
        ("45244",),
    ),
    ComponentRule(
        ComponentDomain.PORTS_COASTAL,
        "coastal_protection",
        "Coastal protection",
        ("proteção costeira", "protecao costeira", "defesa costeira", "coastal protection"),
        ("45243",),
    ),
    ComponentRule(
        ComponentDomain.PORTS_COASTAL,
        "shore_power",
        "Electrical shore power",
        (
            "shore power",
            "onshore power supply",
            "alimentação elétrica em terra",
            "alimentacao eletrica em terra",
        ),
        ("31", "4531"),
    ),
    ComponentRule(
        ComponentDomain.PORTS_COASTAL,
        "photovoltaic",
        "Photovoltaic systems",
        (
            "fotovoltaico",
            "fotovoltaica",
            "painéis fotovoltaicos",
            "paineis fotovoltaicos",
            "photovoltaic",
        ),
        ("093312",),
    ),
    ComponentRule(
        ComponentDomain.PORTS_COASTAL,
        "civil_works",
        "Port civil works",
        ("obras civis", "civil works", "infraestruturas de serviço"),
        ("45", "452"),
    ),
    ComponentRule(
        ComponentDomain.PORTS_COASTAL,
        "monitoring",
        "Monitoring",
        ("monitorização", "monitorizacao", "monitoring"),
        ("384", "389"),
    ),
    ComponentRule(
        ComponentDomain.PORTS_COASTAL,
        "equipment",
        "Port equipment",
        ("equipamento portuário", "equipamento portuario", "port equipment"),
        ("3493",),
    ),
    ComponentRule(
        ComponentDomain.ENERGY_EFFICIENCY,
        "building_works",
        "Building works",
        (
            "reabilitação do edifício",
            "reabilitacao do edificio",
            "building works",
            "building rehabilitation",
        ),
        ("454",),
    ),
    ComponentRule(
        ComponentDomain.ENERGY_EFFICIENCY,
        "hvac",
        "HVAC",
        ("avac", "hvac", "climatização", "climatizacao"),
        ("45331",),
    ),
    ComponentRule(
        ComponentDomain.ENERGY_EFFICIENCY,
        "bms_control",
        "Building management and control",
        (
            "gestão técnica centralizada",
            "gestao tecnica centralizada",
            "building management system",
            "bms",
        ),
    ),
    ComponentRule(
        ComponentDomain.ENERGY_EFFICIENCY,
        "metering",
        "Metering",
        ("medição de energia", "medicao de energia", "contadores de energia", "energy metering"),
        ("3855",),
    ),
    ComponentRule(
        ComponentDomain.ENERGY_EFFICIENCY,
        "photovoltaic",
        "Photovoltaic systems",
        (
            "fotovoltaico",
            "fotovoltaica",
            "painéis fotovoltaicos",
            "paineis fotovoltaicos",
            "photovoltaic",
        ),
        ("093312",),
    ),
    ComponentRule(
        ComponentDomain.ENERGY_EFFICIENCY,
        "lighting",
        "Lighting",
        ("iluminação", "iluminacao", "lighting", "led"),
        ("315",),
    ),
    ComponentRule(
        ComponentDomain.ENERGY_EFFICIENCY,
        "insulation_envelope",
        "Insulation and envelope",
        ("isolamento térmico", "isolamento termico", "envolvente do edifício", "insulation"),
        ("4532",),
    ),
    ComponentRule(
        ComponentDomain.ENERGY_EFFICIENCY,
        "engineering_audit",
        "Engineering and energy audit",
        (
            "auditoria energética",
            "auditoria energetica",
            "energy audit",
            "projeto de eficiência energética",
        ),
        ("713143",),
    ),
    ComponentRule(
        ComponentDomain.RESILIENCE_FIRE,
        "sensors_cameras",
        "Sensors and cameras",
        ("sensores", "câmaras", "camaras", "deteção precoce", "detecao precoce", "cameras"),
        ("35125",),
    ),
    ComponentRule(
        ComponentDomain.RESILIENCE_FIRE,
        "communications",
        "Communications",
        ("comunicações", "comunicacoes", "communications", "rede rádio", "rede radio"),
        ("322", "325"),
    ),
    ComponentRule(
        ComponentDomain.RESILIENCE_FIRE,
        "vehicles",
        "Vehicles",
        ("veículos", "veiculos", "viaturas", "vehicles", "autotanques"),
        ("341442",),
    ),
    ComponentRule(
        ComponentDomain.RESILIENCE_FIRE,
        "ppe_equipment",
        "PPE and response equipment",
        (
            "equipamento de proteção individual",
            "equipamento de protecao individual",
            "ppe",
            "equipamentos de combate",
        ),
        ("351134",),
    ),
    ComponentRule(
        ComponentDomain.RESILIENCE_FIRE,
        "civil_works",
        "Civil works",
        ("obras civis", "civil works"),
        ("45", "452"),
    ),
    ComponentRule(
        ComponentDomain.RESILIENCE_FIRE,
        "command_control",
        "Command and control systems",
        ("comando e controlo", "command and control", "centro de comando"),
        (),
    ),
)

_SENTENCE_BOUNDARIES = ".;!?\n"


def _validate_rules() -> None:
    categories: set[tuple[ComponentDomain, str]] = set()
    for rule in RULES:
        key = (rule.domain, rule.category)
        if key in categories:
            raise RuntimeError(f"duplicate component rule: {rule.domain}:{rule.category}")
        categories.add(key)
        if not rule.phrases or any(not phrase.strip() for phrase in rule.phrases):
            raise RuntimeError(f"component rule has an empty phrase: {key}")
        for prefix in rule.cpv_prefixes:
            if not prefix.isdigit() or not 2 <= len(prefix) <= 8:
                raise RuntimeError(f"invalid CPV prefix {prefix!r} for {key}")


_validate_rules()


def rules_for(domains: Sequence[ComponentDomain]) -> tuple[ComponentRule, ...]:
    selected = frozenset(domains)
    return tuple(rule for rule in RULES if rule.domain in selected)


def _phrase_pattern(phrase: str) -> re.Pattern[str]:
    return re.compile(rf"(?<!\w){re.escape(phrase)}(?!\w)", flags=re.IGNORECASE)


def _supporting_span(text: str, match_start: int, match_end: int) -> tuple[int, int, str]:
    left = max(text.rfind(boundary, 0, match_start) for boundary in _SENTENCE_BOUNDARIES)
    right_positions = [
        position
        for boundary in _SENTENCE_BOUNDARIES
        if (position := text.find(boundary, match_end)) >= 0
    ]
    start = left + 1
    end = min(right_positions) + 1 if right_positions else len(text)

    while start < end and text[start].isspace():
        start += 1
    while end > start and text[end - 1].isspace():
        end -= 1
    return start, end, text[start:end]


def _scope_segments(text: str) -> tuple[EvidenceSpan, ...]:
    segments: list[EvidenceSpan] = []
    start = 0
    for index, character in enumerate(text):
        if character not in _SENTENCE_BOUNDARIES:
            continue
        end = index + 1
        raw_start = start
        while raw_start < end and text[raw_start].isspace():
            raw_start += 1
        raw_end = end
        while raw_end > raw_start and text[raw_end - 1].isspace():
            raw_end -= 1
        if raw_start < raw_end:
            segments.append(
                EvidenceSpan(
                    start=raw_start,
                    end=raw_end,
                    text=text[raw_start:raw_end],
                    matched_phrases=(),
                )
            )
        start = end

    raw_start = start
    while raw_start < len(text) and text[raw_start].isspace():
        raw_start += 1
    raw_end = len(text)
    while raw_end > raw_start and text[raw_end - 1].isspace():
        raw_end -= 1
    if raw_start < raw_end:
        segments.append(
            EvidenceSpan(
                start=raw_start,
                end=raw_end,
                text=text[raw_start:raw_end],
                matched_phrases=(),
            )
        )
    return tuple(segments)


def _component_id(operation_code: str, domain: ComponentDomain, category: str) -> str:
    identity = f"{COMPONENT_RULE_VERSION}|{operation_code}|{domain.value}|{category}"
    return f"cmp_{hashlib.sha256(identity.encode('utf-8')).hexdigest()[:20]}"


def _extract_rule(project: FundingProject, rule: ComponentRule) -> ExtractedComponent | None:
    text = project.project_scope_text
    spans: dict[tuple[int, int], set[str]] = {}

    for phrase in rule.phrases:
        for match in _phrase_pattern(phrase).finditer(text):
            start, end, _ = _supporting_span(text, match.start(), match.end())
            spans.setdefault((start, end), set()).add(phrase)

    if not spans:
        return None

    evidence_spans = tuple(
        EvidenceSpan(
            start=start,
            end=end,
            text=text[start:end],
            matched_phrases=tuple(sorted(matched_phrases, key=str.casefold)),
        )
        for (start, end), matched_phrases in sorted(spans.items())
    )
    primary_span = evidence_spans[0]
    category = f"{rule.domain.value}:{rule.category}"
    component = PurchaseComponent(
        component_id=_component_id(project.operation_code, rule.domain, rule.category),
        operation_code=project.operation_code,
        category=category,
        description=rule.label,
        scope_evidence=primary_span.text,
    )
    return ExtractedComponent(
        component=component,
        domain=rule.domain,
        evidence_spans=evidence_spans,
        cpv_prefixes=rule.cpv_prefixes,
    )


def extract_components(
    project: FundingProject,
    domains: Sequence[ComponentDomain],
) -> ExtractionResult:
    """Extract deterministic components from allowlisted project scope text.

    Empty deterministic output requests the later local-model fallback. This function never infers
    OPEN/CLOSED/PARTIAL state and does not make a completeness claim about the project scope.
    """

    unique_domains = tuple(dict.fromkeys(domains))
    if not unique_domains:
        raise ValueError("at least one component domain is required")

    extracted = tuple(
        component
        for rule in rules_for(unique_domains)
        if (component := _extract_rule(project, rule)) is not None
    )
    extracted = tuple(
        sorted(
            extracted,
            key=lambda item: (
                item.domain.value,
                item.component.category,
                item.component.component_id,
            ),
        )
    )
    covered_ranges = {
        (span.start, span.end)
        for item in extracted
        for span in item.evidence_spans
    }
    unmatched_scope_spans = tuple(
        segment
        for segment in _scope_segments(project.project_scope_text)
        if (segment.start, segment.end) not in covered_ranges
    )
    return ExtractionResult(
        operation_code=project.operation_code,
        domains=unique_domains,
        components=extracted,
        unmatched_scope_spans=unmatched_scope_spans,
        model_fallback_required=bool(unmatched_scope_spans) or not extracted,
    )


def cpv_matches_prefixes(cpv_code: str, prefixes: Iterable[str]) -> bool:
    """Return whether a CPV code belongs to one of the frozen taxonomy prefixes."""

    digits = "".join(character for character in cpv_code if character.isdigit())
    return bool(digits) and any(digits.startswith(prefix) for prefix in prefixes)
