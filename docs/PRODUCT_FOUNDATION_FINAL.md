# ProcRun — final product foundation

Status: **READY FOR PRODUCT BUILD; TED-SCOPED MVP PROCUREMENT PATH APPROVED; LIVE FUNDED-PROJECT INGEST SUBJECT TO A1**
Date: 2026-09-04

This document is the canonical product definition. Phase 0B and Phase 0C remain valid failed tests of the retired TED-only demand-extraction hypothesis; they do not invalidate TED as an approved procurement-evidence source.

## 1. Product definition

ProcRun is a supplier-side infrastructure procurement product. The long-term runway mechanism remains:

`approved funded project -> source-evidenced purchasable components -> approved procurement evidence -> conservative matching -> component state -> project state -> customer runway`

The MVP may ship TED procurement functionality before a funded-project source is approved. Funded-project features remain fixture-only until A1 passes.

ProcRun is not a general tender portal, CRM, bid writer, buyer-intelligence suite or AI GO/NO-GO scorer.

## 2. Trust contract and permanent MVP OPEN scope

Marketing may say:

> **No invented demand. Source evidence for every positive procurement match.**

`100% source-verified` is allowed only for a positive evidence object that actually satisfies its evidence contract.

For the MVP, `OPEN` is frozen as:

> **No relevant procurement found in TED as of DATE.**

Every customer surface that renders or exports `OPEN` must preserve that TED scope. ProcRun must state explicitly:

> **ProcRun's MVP shows absence of matching procurement in TED. This is not a guarantee that no procurement exists outside TED, including purely national or below-threshold procedures.**

The product must never shorten this into a complete-Portuguese-coverage claim.

## 3. State ontology

### Component states

- **CLOSED** — accepted Tier A/B procurement evidence shows the specific component has entered procurement at/before cutoff.
- **OPEN (TED-scoped)** — no relevant procurement was found in the complete approved TED search scope at cutoff.
- **UNRESOLVED** — ambiguity, review-band evidence, incomplete TED retrieval or insufficient evidence prevents a safe decision.

### Project states

When funded-project ingest is eventually approved, project states remain `OPEN`, `PARTIAL`, `CLOSED`, `UNRESOLVED`; any OPEN-derived aggregate inherits the same explicit TED coverage qualifier.

False or over-broad OPEN is the highest-cost classification error.

## 4. Source strategy

### 4.1 TED

TED Search API is APPROVED for field-bounded procurement evidence, market context and the MVP negative-search boundary. Server-side field projection, bounded pagination and schema validation remain mandatory.

### 4.2 Funded-project source

A live funded-project source must satisfy A1 before use. PRR Projects and Mais Transparência are Category B and permanently closed to the intelligence plane under the current zero-contact/zero-PII rules.

OpenCoesione is the leading Category A replacement candidate because official monitoring documentation explicitly constrains project title and summary against sensitive natural-person information and uses codified CUP-based monitoring structures. It still requires exact-route qualification before activation.

The `FundingProject` interface remains source-agnostic.

### 4.3 Portuguese national procurement sources

BASE/IMPIC and full Diário da República routes remain disabled because the publicly documented routes do not satisfy the pre-receipt zero-person contract. They are not required for the MVP because the MVP does not claim national completeness.

Part L RSS is a passive future enhancement only if INCM later publishes authoritative public documentation proving the exact safe schema and required completeness/reuse semantics. No contact may be made to obtain such assurance.

## 5. Canonical customer objects

### FundingProject

Required once a source is approved: stable source ID, project title, approved scope text, dates where available, approved funding/value fields, programme/classification where available, observation timestamp and immutable version/hash. No beneficiary/contact/person identity is part of the analytical contract.

### PurchaseComponent

Deterministic component ID, domain/category/display label, exact approved project-scope evidence span, extraction method/version, cutoff and immutable version/hash.

### ProcurementEvidence

Approved source/publication identifier, publication date, accepted procurement scope evidence, approved CPV/category context, match tier/reasons, observation timestamp and immutable version/hash.

### ComponentAssessment

Component ID, historical cutoff, `OPEN|CLOSED|UNRESOLVED`, evidence references, explicit coverage scope (`TED` for MVP OPEN), rationale, rule/model versions and deterministic classification hash.

## 6. Matching and model boundary

The hierarchy in `MATCHING_RULES.md` remains canonical. Tier A/B may close only with explicit evidence and required corroboration; Tier C is review-only; semantic similarity alone never closes a component; post-cutoff procurement cannot rewrite an earlier historical state.

Deterministic extraction is primary. A local model may inspect only already-approved text and propose a frozen category plus an exact source span. It cannot create evidence or state.

## 7. Customer workflow

Authenticated routes remain:

- `/app` — opportunities/runway feed;
- `/app/projects/[id]` — funded-project detail when that source is approved, fixture-only before then;
- `/app/components/[id]` — component evidence/history;
- `/app/market` — TED procurement market context;
- `/app/profile` — supplier profile;
- `/app/saved` — saved opportunities;
- `/app/account` — account/billing.

Public routes remain `/`, `/product`, `/methodology`, `/pricing`, `/login`, with `/terms` and `/privacy` required before paid release.

## 8. Customer-facing coverage copy

The methodology page, dashboard/feed, CSV export and any API representation of an OPEN state must include the semantic equivalent of:

> **Coverage: TED. No relevant procurement was found in TED as of DATE. This does not establish that no procurement exists outside TED, including national or below-threshold procedures.**

No customer-facing text may imply complete Portuguese procurement coverage.

## 9. Supplier relevance and market context

Supplier relevance remains deterministic/profile-based and explainable. TED may power procurement activity/time/value/category views with missingness disclosures. Saved opportunities, market intelligence and customer-safe CSV export may operate on the approved TED path independently of funded-project ingest.

## 10. Website claims

Allowed for the TED-scoped MVP:

- source-evidenced TED procurement matches;
- explicit TED-scoped absence conclusions;
- historical cutoff/version reproducibility;
- supplier relevance based on approved structured evidence;
- transparent coverage limitations.

Allowed only after a funded-project source passes A1:

- funded-project scope translated into source-evidenced purchasable components;
- funded-project/component runway claims.

Not allowed:

- `we know no procurement exists`;
- complete Portuguese procurement coverage;
- implying TED covers national/below-threshold procedures that are outside its publication universe;
- blanket `100% accurate` or `trust blindly` language;
- complete bill of materials;
- guaranteed discovery of every future purchase;
- probabilistic GO/NO-GO or win probability;
- person/contact intelligence;
- source/EU endorsement.

## 11. Packaging

Launch package remains **ProcRun Portugal — €149/month** unless later commercial evidence changes it. The release may expose only features whose source contracts are approved. Funded-project screens remain synthetic/fixture-only until A1 passes and must never be represented as live.

## 12. Phase 0B/0C treatment

Phase 0B and Phase 0C remain FAIL for the retired TED-only *demand-extraction product hypothesis*. Their results are not rewritten. TED's independently qualified role as procurement evidence, market context and bounded negative-search source remains valid.

## 13. Production implementation order

1. preserve TED source contract and TED-scoped OPEN regression tests;
2. build web shell/read model against deterministic fixtures;
3. wire approved TED ingest/evidence, market context, saved opportunities and CSV export;
4. expose TED scope explicitly in every OPEN customer surface;
5. continue OpenCoesione/external Category A funded-source qualification in parallel;
6. activate funded-project collector only after A1 + source-transfer/live acceptance pass;
7. complete A19 before checkout.

## 14. Authoritative build decision

Only `BUILD_GATES.md` A20 can declare build readiness.

**Decision: BUILD now. TED-scoped live procurement classification is an approved MVP path. Live funded-project ingestion remains fail-closed until a Category A source passes A1.**