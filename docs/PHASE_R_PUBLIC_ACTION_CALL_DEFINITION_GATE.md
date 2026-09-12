# Phase R — public action/call definition qualification

Status: **COMPLETE — TWO CANDIDATE DOMAINS, 40% GATE NOT YET MET**

Reviewed: 2026-09-12

## Purpose

The structured-refinement gate proved that the high-volume Lombardia intervention codes split into stable `azione` / `codice_bando` cohorts. This gate asks whether the official public definitions of those cohorts describe a procurement-relevant scope narrowly enough to justify a later component-domain design.

This is a documentation/semantic qualification only. It does **not** change `ComponentDomain`, mappings, phrase rules, CPV rules, OPEN/CLOSED semantics or customer output.

## Source boundary

Only public official Regione Lombardia / PR FESR programme, action and call pages and public call-rule documents were reviewed. No beneficiary list, application list, award list, person/contact record or project row was used as evidence.

The following previously qualified aggregate counts remain frozen:

- frozen corpus: 4,305 projects;
- existing deterministic mapped coverage: 142 / 4,305 = 3.2985%;
- safe Lombardia intervention-code population: 4,178 / 4,305 = 97.0499%.

## Decision standard

A cohort may proceed to component-domain design only when its official definition establishes a stable family of goods/services/works likely to be purchased. A funding purpose, beneficiary type or policy objective by itself is insufficient.

A **GO TO DESIGN** result is not production approval. A later gate must define deterministic component categories and CPV/phrase evidence and must measure incremental coverage before production activation.

## High-value cohort review

### 1. Code 013 / Action 1.2.3 / RLO12024039683 — 573 projects

**Official scope:** `Transizione digitale delle imprese lombarde` supports acceleration of SME digital transformation. The official call rules state that eligible expenditure includes purchase of IT services and/or technologies directly connected to the implementation, plus bounded planning and training services. The rules also explicitly contemplate electrical/electronic equipment, cloud/licence services and technology implementation.

**Finding:** this is not merely a policy label. The call establishes a coherent technology-purchase family.

**Decision:** **GO TO DESIGN — candidate domain `digital_transformation`.**

The later component-design gate must remain narrower than the programme label and define concrete purchase families such as software/licensing, cloud/IT services, digital equipment, implementation/integration and related training. It must not infer a specific component from the action code alone.

Official sources:

- Regione Lombardia, `Transizione digitale delle imprese lombarde`, code RLO12024039683: https://www.bandi.regione.lombardia.it/servizi/servizio/catalogo/dettaglio/RLO12024039683
- Official call rules, Allegato A Decreto 11468/2024, especially B.3 eligible expenditure: linked from the official call page above.

### 2. Code 067 / Action 2.6.2 / RLT12024038383 + RLT12024040123 — 142 projects

**Official scope:** both calls are explicitly about circular economy / waste prevention, reuse, recycling and material recovery.

The SME plastics/textile call permits interventions including production-line modifications to reduce waste or use end-of-waste materials, dedicated waste collection, preparation for reuse and recycling processes.

The local-authority call is even more concrete: reuse centres, food-surplus hubs, professional reusable-serving equipment, preservation/transport equipment, community/local composting plants and civil works, floating-waste collection systems, dedicated waste-collection systems and mobile environmental/recycling centres.

**Finding:** the two calls share a coherent waste/circular-economy procurement family with explicit infrastructure, equipment and process categories.

**Decision:** **GO TO DESIGN — candidate domain `waste_circular_economy`.**

A later component-design gate should distinguish at least reuse infrastructure, waste-collection equipment/systems, composting/recycling equipment/processes, production-line modifications and supporting civil works where the official call scope supports them.

Official sources:

- Regione Lombardia, RLT12024038383: https://bandi.regione.lombardia.it/servizi/servizio/catalogo/dettaglio/ambiente-territorio/gestione-rifiuti/ri-circo-risorse-circolari-lombardia-sostegno-pmi-lombarde-sviluppo-azioni-economia-circolare-edizione-dedicata-filiere-plastica-tessile-RLT12024038383
- Regione Lombardia, RLT12024040123: https://www.bandi.regione.lombardia.it/servizi/servizio/catalogo/dettaglio/ambiente-energia/rifiuti-economia-circolare/ri-circo-risorse-circolare-enti-locali-RLT12024040123

### 3. Code 010 / Action 1.1.4 / RLF12023035064 — 277 projects

**Official scope:** `Brevetti 2023` supports obtaining or extending European/international patents for industrial inventions.

**Finding:** the call can generate expenditure on patent-related professional/filing activity, but this is an IP-support grant and is outside the current ProcRun procurement-component product scope. Treating `patent_services` as a Phase R coverage domain would broaden the commercial taxonomy rather than resolve the current evidence gap.

**Decision:** **NO-GO for current Phase R taxonomy.**

Official source: https://www.bandi.regione.lombardia.it/servizi/servizio/bandi/ricerca-innovazione/ricerca-sviluppo-innovazione/brevetti-2023-RLF12023035064

### 4. Code 023 / Action 1.4.1 — 560 projects

The dominant calls are training/skills instruments. RLO12023033524 provides company training vouchers; RLO12025044083 supports specialist training and accompanying activities for SME groups.

**Finding:** training services are real purchases, but creating a generic `training_services` domain would materially broaden ProcRun away from the current concrete project/procurement taxonomy. The programme/action definition also does not identify a stable technical component family relevant to the existing product thesis.

**Decision:** **NO-GO for current Phase R taxonomy.**

Official sources:

- https://ue.regione.lombardia.it/bando/RLO12023033524
- https://ue.regione.lombardia.it/bando/RLO12025044083

### 5. Code 021 / Action 1.3.1 — dominant call RLO12024039843

The dominant 1.3.1 cohort supports SME participation at international trade fairs in Lombardia through grants.

**Finding:** the call purpose is commercial promotion/internationalisation, not one stable technical procurement family.

**Decision:** **NO-GO for current Phase R taxonomy.**

Official source: https://www.bandi.regione.lombardia.it/servizi/servizio/bandi/dettaglio/attivita-produttive-commercio/fiere/pr-fesr-2021-2027-azione-1-3-1-bando-contributi-partecipazione-mpmi-fiere-internazionali-lombardia-RLO12024039843

### 6. Code 021 / Action 1.3.3 — dominant call RLO12024040384

`Investimenti – Linea Microimprese` supports technological innovation of plants/equipment, environmental-impact reduction and lower energy consumption. Public programme material shows a broad expenditure mix including machinery, production equipment/plants, renewable-energy systems, software/licences, training and technical consultancy.

**Finding:** this is clearly procurement-generating but is too cross-domain to map the action/call identifier itself to one ProcRun domain. It mixes industrial machinery, energy, software and professional services.

**Decision:** **NO DIRECT DOMAIN MAPPING. CONDITIONAL GO only to a later subcomponent-design study if the two approved candidate domains are insufficient.**

Official sources:

- https://www.unioncamerelombardia.it/bandi-e-incentivi-alle-imprese/dettaglio-bando/bando-investimenti-linea-microimprese
- Regione Lombardia official call page, code RLO12024040384.

## Coverage implication

The two cohorts approved only for **component-domain design** contain:

- digital transformation: 573 projects;
- waste/circular economy: 142 projects.

Even under an optimistic upper-bound assumption that every project in both cohorts later passes a deterministic component rule and that none is already counted in the 142-project baseline, the maximum combined coverage would be:

`(142 + 573 + 142) / 4,305 = 19.9071%`.

This is well below the Phase R 40% target.

Therefore these two candidate domains are worth designing because they are semantically legitimate, but **they cannot by themselves close the commercial coverage gate**. The product must not claim the 97.0499% structured-data ceiling as procurement classification coverage.

## Decision

1. **GO** to a component-design gate for `digital_transformation` and `waste_circular_economy`.
2. **NO-GO** on patent, generic training and trade-fair domains for the current ProcRun product thesis.
3. **NO direct mapping** of Action 1.3.3 / Microimprese because its procurement scope is multi-domain.
4. Before any production activation, the component-design gate must define deterministic subcategories, evidence rules and candidate CPV prefixes, then measure isolated uplift against the frozen 4,305-project corpus.
5. Because the optimistic two-domain ceiling is only 19.9071%, the next design gate must also state explicitly that another safe signal/refinement route will still be required to reach 40%.

No human contact, PII processing, beneficiary/application-list intake or semantic fallback is authorized by this decision.
