# ProcRun — final product foundation

Status: **WEB PRODUCT BUILD: GO. CORE PRODUCT DELIVERY AND PRE-WEB RELEASE HOUSEKEEPING ARE GREEN.**
Date: 2026-09-06

This document is the canonical product definition. Authoritative readiness remains `docs/BUILD_GATES.md` A20. Customer-facing data, commercialization, attribution and source-consistency are additionally governed by the normative `docs/CUSTOMER_DATA_AND_COMMERCIALIZATION_CONTRACT.md`.

Phase 0B and Phase 0C remain valid failed tests of the retired TED-only demand-extraction hypothesis; they do not invalidate TED as an approved procurement-evidence source.

## 1. Product definition

ProcRun is a supplier-side infrastructure procurement product. The canonical runway mechanism is:

`approved funded project -> source-evidenced purchasable components -> approved procurement evidence -> conservative matching -> component state -> project state -> customer runway`

The complete non-web intelligence delivery chain has passed production acceptance. Customer-facing web implementation is now the authorized final product-development phase.

ProcRun is not a general tender portal, CRM, bid writer, buyer-intelligence suite or AI GO/NO-GO scorer.

## 2. Commercial premise

ProcRun does not sell exclusive access to public OpenCoesione or TED source data. Customer payment is for the approved ProcRun service layer built on approved sources: evidence-bounded processing, component extraction, procurement matching, conservative state assessment, supplier relevance, filtering, monitoring, history, workflow, exports and other explicitly approved derived functionality.

Public availability of an upstream source or field does not widen ProcRun's source, privacy or customer-safe boundary. A customer may independently follow an official source link and see information that ProcRun intentionally does not ingest or expose.

All pricing, marketing, Terms/Privacy, demos, samples, APIs, exports and customer UI must comply with `docs/CUSTOMER_DATA_AND_COMMERCIALIZATION_CONTRACT.md`.

## 3. Trust contract and permanent MVP OPEN scope

Marketing may say:

> **No invented demand. Source evidence for every positive procurement match.**

`100% source-verified` is allowed only for a positive evidence object that actually satisfies its evidence contract.

For the MVP, `OPEN` is frozen as:

> **No relevant procurement found in TED as of DATE.**

Every customer surface that renders or exports `OPEN` must preserve that TED scope. ProcRun must state explicitly:

> **ProcRun's MVP shows absence of matching procurement in TED. This is not a guarantee that no procurement exists outside TED, including purely national or below-threshold procedures.**

False or over-broad OPEN is the highest-cost classification error.

## 4. State ontology

### Component states

- **CLOSED** — accepted Tier A/B procurement evidence shows the specific component has entered procurement at/before cutoff.
- **OPEN (TED-scoped)** — no relevant procurement was found in the complete approved TED search scope at cutoff.
- **UNRESOLVED** — ambiguity, review-band evidence, incomplete TED retrieval or insufficient evidence prevents a safe decision.

### Project states

Project states are `OPEN`, `PARTIAL`, `CLOSED`, `UNRESOLVED`; any OPEN-derived aggregate inherits the same explicit TED coverage qualifier.

## 5. Source strategy

### 5.1 TED

TED Search API is APPROVED for field-bounded procurement evidence, market context and the MVP negative-search boundary. Server-side field projection, bounded pagination and schema validation remain mandatory.

### 5.2 Funded-project source

OpenCoesione is APPROVED only for the exact bounded 2021-2027 EU-cohesion operation-list publication family. The current live production route is **PR FESR Lombardia 2021-2027**. The broad OpenCoesione API, Projects/Soggetti surfaces and arbitrary additional source fields are not approved.

The dedicated production runtime has passed live source transfer and the complete OpenCoesione -> TED -> runway -> persistence -> customer-safe delivery path.

Portugal PRR, Mais Transparência, PT2030 and Portal BASE current routes remain blocked/rejected under the source-safety rules and are not part of the active product.

Any new source — including one used only for geography, enrichment, evidence or UI copy — must pass the full applicable RIGHTS / ACCESS / DATA SAFETY / schema / attribution / customer-mapping gate before use. Accidental or temporary prior use creates no presumption of approval.

## 6. Canonical customer objects

### FundingProject

Stable source ID, project title, approved scope text, dates where available, approved funding/value fields, programme/classification where available, observation timestamp and immutable version/hash. No beneficiary/contact/person identity is part of the analytical contract.

### PurchaseComponent

Deterministic component ID, domain/category/display label, exact approved project-scope evidence span, extraction method/version, cutoff and immutable version/hash.

### ProcurementEvidence

Approved source/publication identifier, publication date, accepted procurement scope evidence, approved CPV/category context, match tier/reasons, observation timestamp and immutable version/hash.

### ComponentAssessment

Component ID, historical cutoff, `OPEN|CLOSED|UNRESOLVED`, evidence references, explicit coverage scope (`TED` for MVP OPEN), rationale, rule/model versions and deterministic classification hash.

## 7. Customer-safe delivery boundary

`src/procrun/read_model.py`, version `customer-runway-v1`, is the sole approved intelligence contract intended for browser/API/customer delivery, unless an explicitly versioned successor is approved under the same boundary.

No customer-facing web component, demo, sample, API, CSV/JSON export or marketing surface may bypass this contract by reading raw source payloads, collector objects or ad hoc enrichment directly.

Public availability of a source field does not make it customer-safe. Identity/contact/person fields excluded from the intelligence plane remain excluded even if an upstream publisher makes them public.

## 8. Matching and model boundary

The hierarchy in `MATCHING_RULES.md` remains canonical. Tier A/B may close only with explicit evidence and required corroboration; Tier C is review-only; semantic similarity alone never closes a component; post-cutoff procurement cannot rewrite an earlier historical state.

Deterministic extraction is primary. A local model may inspect only already-approved text and propose a frozen category plus an exact source span. It cannot create evidence or state.

## 9. Customer workflow target

Authenticated routes may be implemented as:

- `/app` — opportunities/runway feed;
- `/app/projects/[id]` — funded-project detail;
- `/app/components/[id]` — component evidence/history;
- `/app/market` — TED procurement market context;
- `/app/profile` — supplier profile;
- `/app/saved` — saved opportunities;
- `/app/account` — account/billing.

Public routes include `/`, `/app` demo, `/methodology`, `/pricing`, `/login`, with `/terms` and `/privacy` required for launch.

The earlier fixture/shell is non-authoritative and may be replaced. Frozen source, evidence, privacy, customer-safe and commercialization contracts do constrain the web implementation.

## 10. Customer-facing coverage and source/analysis distinction

The methodology page, dashboard/feed, CSV export and any API representation of an OPEN state must include the semantic equivalent of:

> **Coverage: TED. No relevant procurement was found in TED as of DATE. This does not establish that no procurement exists outside TED, including national or below-threshold procedures.**

Customer surfaces must distinguish:

- upstream source facts/evidence;
- ProcRun-derived analysis;
- the coverage limitation applying to the conclusion.

A derived ProcRun statement must not be presented as though the upstream publisher asserted it.

## 11. Website and commercial claims

Allowed:

- source-evidenced TED procurement matches;
- explicit TED-scoped absence conclusions;
- historical cutoff/version reproducibility;
- supplier relevance based on approved structured evidence;
- transparent coverage limitations;
- funded-project scope and runway from the approved live Lombardia delivery chain;
- clear statements that the subscription pays for ProcRun's analysis/workflow layer over approved public sources.

Not allowed:

- `we know no procurement exists`;
- complete national procurement coverage;
- complete Italian public-investment coverage;
- implying TED covers national/below-threshold procedures outside its publication universe;
- blanket `100% accurate` or `trust blindly` language;
- complete bill of materials;
- guaranteed discovery of every future purchase;
- probabilistic GO/NO-GO or win probability;
- person/contact intelligence;
- source/EU endorsement;
- claiming ownership of or exclusive/privileged access to underlying public source data;
- introducing a new source or source field through UI/evidence/enrichment before qualification.

## 12. Attribution, source links and branding

Customer-facing source attribution must satisfy the applicable approved source contract. Official source links may be provided for provenance and navigation.

A source link does not expand ProcRun's rights or customer-safe field boundary. ProcRun must not use third-party logos, marks or protected assets merely because data reuse is permitted, and must not imply endorsement, partnership or certification by OpenCoesione, TED, the EU or another source owner.

## 13. Packaging

Current web package: **ProcRun Lombardia — €149/month**, subject to final billing, VAT/invoicing, merchant-identity and launch controls.

Packaging does not override source, privacy, customer-safe, coverage or commercialization gates. A higher-paying tier may provide more approved ProcRun functionality, but never a wider legal/privacy/source boundary.

## 14. Phase 0B/0C treatment

Phase 0B and Phase 0C remain FAIL for the retired TED-only *demand-extraction product hypothesis*. Their results are not rewritten. TED's independently qualified role as procurement evidence, market context and bounded negative-search source remains valid.

## 15. Web-phase launch controls

Before public paid launch, the customer application must close at least:

1. authentication/authorization and account separation;
2. Stripe/subscription implementation if used;
3. VAT/invoicing and merchant identity;
4. Terms and Privacy presentation;
5. customer-control-plane privacy/processors/cookies/logging;
6. domain/TLS and security/access controls;
7. rendered source attribution and methodology;
8. customer-data/commercialization consistency across landing, pricing, demo, Terms, Privacy, methodology, API/export and checkout;
9. verification that customer delivery uses only the approved read model;
10. final end-to-end checkout/access/release testing.

Any unknown or conflict affecting source rights, privacy, customer-visible fields, attribution, geography, coverage, pricing claims or commercialization semantics is fail-closed for release.

## 16. Authoritative build decision

Only `BUILD_GATES.md` A20 can declare readiness.

**Decision: WEB PRODUCT BUILD IS AUTHORIZED. Public/paid launch remains blocked until the mandatory web-phase launch controls are green.**
