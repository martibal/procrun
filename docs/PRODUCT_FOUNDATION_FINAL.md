# ProcRun — final product foundation

Status: **READY FOR PRODUCT BUILD; LIVE RUNWAY INGEST SUBJECT TO A1**
Date: 2026-09-03

This document is the canonical product definition. It supersedes the TED-only v2/v2.1 product promise wherever they conflict. Phase 0B and Phase 0C remain valid failed tests of that retired TED-only mechanism.

## 1. Product definition

ProcRun is a supplier-side infrastructure procurement runway product.

Canonical pipeline:

`approved funded project -> source-evidenced purchasable components -> approved procurement evidence -> conservative matching -> component OPEN/CLOSED/UNRESOLVED -> project OPEN/PARTIAL/CLOSED/UNRESOLVED -> customer runway`

Primary customer promise:

> **See what an approved infrastructure project is expected to buy, what ProcRun can prove has already entered procurement, and what remains without a verified procurement match as of the stated date.**

ProcRun is not a general tender portal, CRM, bid writer, buyer-intelligence suite or AI GO/NO-GO scorer.

## 2. Core commercial differentiation

The product is differentiated by a combination that ordinary tender monitoring does not provide:

1. **Project-before-procurement unit of analysis.** The commercial object starts with the funded infrastructure project, not the tender.
2. **Component-level runway.** ProcRun decomposes explicit funded-project scope into separately purchasable product/system categories and tests each one against procurement evidence.
3. **Evidence-first positive claims.** Every accepted component and every accepted procurement match retains exact supporting source evidence, source identity, observation cutoff, method/version and immutable hash reference.
4. **Conservative abstention.** Ambiguous component boundaries, review-band matches or incomplete required source coverage produce `UNRESOLVED`, not a lead.
5. **Historical reproducibility.** A customer-visible state can be reconstructed for the exact historical cutoff and rule/model version.
6. **Narrow initial scope.** Portugal infrastructure is a deliberate evidence-quality boundary, not a claim that breadth is unimportant.

This is not positioned as "better AI tender matching". Competitors may cover more countries, buyer intelligence, qualification and bid workflows. ProcRun's contract is different: **remaining procurement runway with auditable evidence and explicit abstention**.

## 3. Trust / zero-unsupported-inference contract

Marketing may say:

> **No invented demand. Source evidence for every positive component and procurement match.**

The stronger phrase `100% source-verified` is allowed only when attached to a positive evidence object that satisfies the evidence contract. It must not be used as a blanket claim that every state is a source fact.

`OPEN` is a bounded negative-search conclusion. Customer wording is frozen as:

> **No relevant procurement found in approved indexed sources as of DATE.**

An OPEN component is permitted only when required source coverage is complete at that cutoff. If coverage is incomplete, the component is `UNRESOLVED`.

No probabilistic fit score, win probability or AI confidence score is part of the product contract.

## 4. State ontology

### Component states

- **CLOSED** — accepted Tier A/B procurement evidence shows that the specific component has entered procurement at/before cutoff.
- **OPEN** — no relevant procurement was found for the component in approved indexed sources as of cutoff and required source coverage is complete.
- **UNRESOLVED** — ambiguity, review-band evidence, source incompleteness or insufficient evidence prevents a safe OPEN/CLOSED decision.

### Project states

- **CLOSED** — all assessed components are CLOSED.
- **OPEN** — all assessed components are OPEN.
- **PARTIAL** — assessed component states differ, including OPEN/CLOSED or CLOSED/UNRESOLVED mixtures.
- **UNRESOLVED** — no components exist or all assessed components remain unresolved.

False OPEN is the highest-cost classification error. The system therefore sacrifices recall before it sacrifices this invariant.

## 5. Initial domains

The initial supported infrastructure domains remain:

- water and wastewater;
- rail/transport;
- ports/coastal;
- energy efficiency/electrical systems;
- resilience/fire.

The frozen component taxonomy and deterministic extraction rules are defined in `COMPONENT_ENGINE.md` and code. Expansion requires explicit versioning, evidence and regression tests.

## 6. Sources

### 6.1 Funded-project source

A funded-project source must satisfy A1 before live use: RIGHTS, ACCESS and DATA SAFETY all approved, including the absolute pre-receipt natural-person boundary for every retained structured/free-text field.

Current PRR/dados.gov.pt evidence is strong enough to keep the route as the preferred production candidate: official national open-data publisher, daily PRR project dataset, separate Projects and Entities resources, portal rule that datasets may not contain personal data, and default CC BY 4.0 for State datasets unless otherwise specified. ProcRun's stricter rule still requires exact source-specific machine-route/free-text safety proof before activation. Until that is frozen, the collector stays disabled.

The product definition does not change if the finally approved funded-project transport is PRR Projects or another authoritative route; the source must implement the same canonical `FundingProject` contract.

### 6.2 Procurement evidence

TED Search API remains APPROVED for field-bounded procurement evidence and market context. Its Phase 0 qualification supports active infrastructure procurement and historical market analysis; it does not independently support early-runway discovery or comprehensive EU-funding linkage.

Additional procurement sources may be activated only through the same source-contract registry and pre-receipt safety gates.

## 7. Canonical customer objects

### FundingProject

Required fields: stable source ID/operation code, project title, approved scope text, start/end dates where available, approved funding/value fields, programme/component/investment classification where available, source observation timestamp and immutable version/hash.

No beneficiary/contact/person identity is part of the analytical contract.

### PurchaseComponent

Required fields: deterministic component ID, domain, canonical category, display label, exact project-scope evidence span, extraction method/version, source cutoff and immutable version/hash.

### ProcurementEvidence

Required fields: approved source/publication identifier, publication date, accepted procurement scope evidence, approved CPV/category context, match tier/reasons, observation timestamp and immutable version/hash.

### ComponentAssessment

Required fields: component ID, historical cutoff, `OPEN|CLOSED|UNRESOLVED`, exact evidence references, required-source coverage status, rationale, rule/model versions and deterministic classification hash where implemented.

### ProjectAssessment

Required fields: operation code, historical cutoff, `OPEN|PARTIAL|CLOSED|UNRESOLVED`, component assessments and immutable version/hash where implemented.

## 8. Matching contract

The hierarchy in `MATCHING_RULES.md` is canonical.

- Tier A/B may close a component only with explicit evidence and required corroboration.
- Tier C is review-only and yields `UNRESOLVED`.
- semantic similarity alone never closes a component.
- a shared project identifier alone never closes every component of a multi-component project.
- post-cutoff procurement cannot rewrite an earlier historical state.

## 9. Model boundary

Deterministic extraction is primary. A local model may only inspect already-approved source text and propose a frozen category plus an exact source span. Deterministic validation must confirm that the returned span exists verbatim in the source input and that the label is permitted.

The model may not create source text, assign procurement state, manufacture a match, convert ambiguity to OPEN or bypass ledger/evidence validation. Production model activation remains benchmark-gated.

## 10. Customer workflow

The authenticated product centers on:

- `/app` — runway feed;
- `/app/projects/[id]` — funded-project and project-state detail;
- `/app/components/[id]` — component evidence/history;
- `/app/market` — procurement/funding market context;
- `/app/profile` — supplier category/domain profile;
- `/app/saved` — saved projects/components;
- `/app/account` — control-plane account/billing.

Public routes remain `/`, `/product`, `/methodology`, `/pricing`, `/login`, with `/terms` and `/privacy` required before paid release.

## 11. Runway feed

The default feed shows only customer-safe assessments. Each item communicates:

- funded project;
- project dates/value where approved;
- component/category;
- component state and historical cutoff;
- project state;
- exact project-scope evidence;
- accepted procurement evidence when CLOSED;
- bounded OPEN wording when OPEN;
- source coverage status;
- last observation and immutable version/hash.

`UNRESOLVED` components are visible in project detail/diagnostics but may be hidden from the commercial default feed.

## 12. Supplier relevance

Supplier relevance is deterministic and profile-based. It may use selected domains/categories, approved CPV families and geography/value preferences. Relevance is not a probability and cannot override component/project evidence state.

The product may prioritize source-evidenced OPEN components for a supplier, but every reason must be inspectable.

## 13. Market context

TED can power procurement activity/time/value/category views with missingness disclosures. Funded-project aggregates may be added only after the funded-project source is A1-approved. Market context is secondary to runway and must not become a substitute TED-only product.

## 14. Website claims

Allowed after A1 source activation:

- approved funded-project scope translated into source-evidenced purchasable components;
- exact evidence for every accepted component and positive procurement match;
- conservative component OPEN/CLOSED/UNRESOLVED semantics;
- conservative project OPEN/PARTIAL/CLOSED/UNRESOLVED semantics;
- historical cutoff/version reproducibility;
- supplier-side view of remaining procurement runway;
- Portugal infrastructure focus.

Not allowed:

- "we know no procurement exists";
- blanket `100% accurate` or `trust blindly` language;
- complete bill of materials;
- guaranteed discovery of every future purchase;
- probabilistic GO/NO-GO or win probability;
- unsupported months-ahead lead-time claims;
- person/contact intelligence;
- source/EU endorsement.

## 15. Landing-page hierarchy

Eyebrow: `Infrastructure procurement runway for suppliers`

Headline: `See what funded projects still have left to buy.`

Subheadline: `ProcRun turns explicit project scope into source-evidenced components, checks them against indexed procurement, and shows the remaining runway with the evidence beside every positive claim.`

Trust strip: `No invented demand · Exact source evidence · Ambiguity stays unresolved`

The product demonstration must show three layers together: project-scope span, procurement evidence where present, and the bounded component/project state that follows.

## 16. Packaging

Launch package remains **ProcRun Portugal — €149/month** unless later commercial evidence changes it.

MVP includes one workspace/profile, runway feed, project/component detail, evidence history, saved items, market context and customer-safe CSV export. No permanent free tier.

Checkout stays disabled until A19 and live source A1 are both green.

## 17. What not to build

Do not build generic all-sector tender aggregation, AI bid writing, CRM, buyer/contact-person databases, generic buyer intelligence, win probability, broad-EU expansion or a TED-only demand feed as the core product.

## 18. Phase 0B/0C treatment

Phase 0B and Phase 0C remain FAIL for the TED-only demand-extraction product hypothesis. Their reproducible CPV-blind signal may be used as bounded procurement-text enrichment, never as evidence that the failed TED-only product passed.

## 19. Production implementation order

1. lock this product/source contract and regression tests;
2. build the `FundingProject` ingress interface with fail-closed source activation;
3. wire the existing component engine and immutable ledger to the canonical project object;
4. wire approved TED procurement evidence and the conservative matching hierarchy;
5. expose the customer-safe runway read model/API;
6. build public pages and authenticated feed/detail/evidence UX;
7. add market context, saved/export and account shell;
8. activate a funded-project collector only after A1 is approved;
9. complete A19 paid-release controls;
10. enable checkout.

## 20. Authoritative build decision

Only `BUILD_GATES.md` A20 can declare build readiness. No README, historical product document or test result may independently override A20.

**Decision: BUILD the product now; keep live funded-project ingestion and paid production fail-closed until their explicit gates are green.**
