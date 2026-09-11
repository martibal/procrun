# ProcRun — frozen EU structured-classification mapping v1

Status: Phase R Task A frozen mapping
Date: 2026-09-11
Runtime mapping version: `eu-structured-mapping-v1`

## Purpose

This table converts only already-approved structured OpenCoesione fields into ProcRun domain suggestions. It is deliberately separate from phrase matching. A mapping hit by itself is **structured-only** evidence and must never be presented as an OPEN/CLOSED finding or as proof that the project text explicitly names a purchasing need.

The source fields are already admitted as `FundingProject.objective` (`ObiettivoSpecifico_SpecificObjective`) and `FundingProject.theme` (`CategoriaOperazione_CategoryIntervention`). No new source retrieval is introduced by Task A.

## Legal/codebook basis

- Regulation (EU) 2021/1058, Article 3 defines ERDF/Cohesion Fund specific objectives.
- Regulation (EU) 2021/1060, Annex I, Table 1 defines intervention-field codes.
- OpenCoesione's 2021-2027 beneficiary/operations publication documents Specific Objective and Category of Intervention as part of the published operation data.

## Specific-objective mapping

Only objectives that unambiguously identify one existing ProcRun domain are mapped. Broader objectives are intentionally omitted.

| Code | Meaning used for mapping | ProcRun domain | Decision |
| --- | --- | --- | --- |
| `RSO2.1` | energy efficiency / greenhouse-gas reduction | `energy_efficiency` | structured-only eligible |
| `RSO2.5` | water access / sustainable water management | `water_wastewater` | structured-only eligible |

Not mapped by objective alone:

- `RSO2.4`: disaster-risk/resilience spans fire, flood, landslide and other risks; it is too broad for the existing fire-resilience domain without a narrower intervention code.
- transport-specific objectives: they can span road, rail, ports and multimodal transport; objective alone is too broad.

## Intervention-field mapping

These Annex I codes are narrow enough to map to one existing ProcRun domain without reading project free text.

| Codes | Official intervention family | ProcRun domain |
| --- | --- | --- |
| `038`–`045` | energy-efficiency measures/buildings/public infrastructure | `energy_efficiency` |
| `059` | climate-related risk: fires | `resilience_fire` |
| `062`–`066` | drinking-water, water management and wastewater | `water_wastewater` |
| `096`–`107` | rail construction/modernisation/digitalisation/ERTMS/rolling assets | `rail_transport` |
| `110`–`115` | seaports and inland ports | `ports_coastal` |

Codes outside this allowlist are not inferred into a ProcRun domain in v1.

## Runtime contract

1. Extract an explicit RSO code from `objective` and/or a three-digit Annex I code from `theme`.
2. Match only exact allowlisted codes above.
3. Retain the exact source-field value alongside the suggestion.
4. Do not create `PurchaseComponent` from structured-only evidence.
5. Do not run TED OPEN/CLOSED matching from structured-only evidence.
6. If phrase evidence later confirms a compatible component, the phrase evidence remains the full-evidence basis; the structured signal is corroboration, not a replacement.

## Precision rationale

The mapping is intentionally sparse. Phase R's 40% target does not permit broad semantic inference merely to increase recall. Any later expansion requires a new frozen mapping version and evidence that the added code maps unambiguously to an existing ProcRun domain.
