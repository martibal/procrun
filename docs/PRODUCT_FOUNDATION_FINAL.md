# ProcRun — final product foundation

Status: **DELIVERY HARDENING ONLY; WEB BUILD BLOCKED UNTIL FULL NON-WEB DELIVERY-READINESS IS GREEN**
Date: 2026-09-04

This document is the canonical product definition. Phase 0B and Phase 0C remain valid failed tests of the retired TED-only demand-extraction hypothesis; they do not invalidate TED as an approved procurement-evidence source.

## 1. Product definition

ProcRun is a supplier-side infrastructure procurement product. The canonical runway mechanism remains:

`approved funded project -> source-evidenced purchasable components -> approved procurement evidence -> conservative matching -> component state -> project state -> customer runway`

The product must not enter customer-facing web implementation until all non-web launch dependencies are production-ready. The web interface is the final build phase, not a parallel workstream.

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

When live funded-project ingest is active, project states remain `OPEN`, `PARTIAL`, `CLOSED`, `UNRESOLVED`; any OPEN-derived aggregate inherits the same explicit TED coverage qualifier.

False or over-broad OPEN is the highest-cost classification error.

## 4. Source strategy

### 4.1 TED

TED Search API is APPROVED for field-bounded procurement evidence, market context and the MVP negative-search boundary. Server-side field projection, bounded pagination and schema validation remain mandatory.

### 4.2 Funded-project source

OpenCoesione is APPROVED only for the exact bounded 2021-2027 EU-cohesion operation-list publication family. PRR Projects and Mais Transparência remain Category B and permanently closed to the intelligence plane.

The exact OpenCoesione collector is implemented fail-closed, but live source-transfer from the current GitHub-hosted runtime is not accepted because the source returns HTTP 403 before ZIP/schema validation. This runtime transport problem must be solved through another automated no-contact execution path while preserving the same source contract and zero-PII rules.

The `FundingProject` interface remains source-agnostic.

### 4.3 Portuguese national procurement sources

BASE/IMPIC and full Diário da República routes remain disabled because the publicly documented routes do not satisfy the pre-receipt zero-person contract. They are not required for the MVP because the MVP does not claim national completeness.

Part L RSS is a passive future enhancement only if INCM later publishes authoritative public documentation proving the exact safe schema and required completeness/reuse semantics. No contact may be made to obtain such assurance.

## 5. Canonical customer objects

### FundingProject

Stable source ID, project title, approved scope text, dates where available, approved funding/value fields, programme/classification where available, observation timestamp and immutable version/hash. No beneficiary/contact/person identity is part of the analytical contract.

### PurchaseComponent

Deterministic component ID, domain/category/display label, exact approved project-scope evidence span, extraction method/version, cutoff and immutable version/hash.

### ProcurementEvidence

Approved source/publication identifier, publication date, accepted procurement scope evidence, approved CPV/category context, match tier/reasons, observation timestamp and immutable version/hash.

### ComponentAssessment

Component ID, historical cutoff, `OPEN|CLOSED|UNRESOLVED`, evidence references, explicit coverage scope (`TED` for MVP OPEN), rationale, rule/model versions and deterministic classification hash.

## 6. Matching and model boundary

The hierarchy in `MATCHING_RULES.md` remains canonical. Tier A/B may close only with explicit evidence and required corroboration; Tier C is review-only; semantic similarity alone never closes a component; post-cutoff procurement cannot rewrite an earlier historical state.

Deterministic extraction is primary. A local model may inspect only already-approved text and propose a frozen category plus an exact source span. It cannot create evidence or state.

## 7. Final customer workflow target

After the delivery-readiness gate is fully green, authenticated routes may be implemented as:

- `/app` — opportunities/runway feed;
- `/app/projects/[id]` — funded-project detail;
- `/app/components/[id]` — component evidence/history;
- `/app/market` — TED procurement market context;
- `/app/profile` — supplier profile;
- `/app/saved` — saved opportunities;
- `/app/account` — account/billing.

Public routes remain `/`, `/product`, `/methodology`, `/pricing`, `/login`, with `/terms` and `/privacy` required for launch.

Any earlier fixture/shell web implementation is frozen and non-authoritative until the full delivery gate is green.

## 8. Customer-facing coverage copy

The methodology page, dashboard/feed, CSV export and any API representation of an OPEN state must include the semantic equivalent of:

> **Coverage: TED. No relevant procurement was found in TED as of DATE. This does not establish that no procurement exists outside TED, including national or below-threshold procedures.**

No customer-facing text may imply complete Portuguese procurement coverage.

## 9. Supplier relevance and market context

Supplier relevance remains deterministic/profile-based and explainable. TED may power procurement activity/time/value/category views with missingness disclosures. Saved opportunities, market intelligence and customer-safe CSV export must be production-ready at the non-web service/read-model layer before web development begins.

## 10. Website claims

Allowed once the final web phase begins:

- source-evidenced TED procurement matches;
- explicit TED-scoped absence conclusions;
- historical cutoff/version reproducibility;
- supplier relevance based on approved structured evidence;
- transparent coverage limitations;
- funded-project scope and runway only after live OpenCoesione delivery acceptance is green.

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

Launch package remains **ProcRun Portugal — €149/month** unless later commercial evidence changes it. Packaging does not override source or delivery gates.

## 12. Phase 0B/0C treatment

Phase 0B and Phase 0C remain FAIL for the retired TED-only *demand-extraction product hypothesis*. Their results are not rewritten. TED's independently qualified role as procurement evidence, market context and bounded negative-search source remains valid.

## 13. Production implementation order

1. preserve TED source contract and TED-scoped OPEN regression tests;
2. complete OpenCoesione live transport from an approved automated no-contact runtime;
3. prove live OpenCoesione -> canonical FundingProject -> component -> procurement evidence -> assessment -> customer-safe read-model end-to-end flow;
4. complete persistence, saved/export, drift detection and operational runbooks;
5. complete all non-web A19 launch controls, billing/control-plane contracts, attribution and legal-content requirements;
6. run repo-wide consistency/no-contact/regression/CI acceptance until all non-web gates are green;
7. only then set `A20 WEB BUILD: GO` and start/resume customer-facing web implementation;
8. after the web is finished, perform only final interface/presentation validation and launch. No unresolved backend/source/delivery dependency may remain at that point.

## 14. Authoritative build decision

Only `BUILD_GATES.md` A20 can declare build readiness.

**Decision: DO NOT BUILD WEB YET. Complete the entire non-web launch delivery chain first. Web becomes the final implementation phase only after A20 can truthfully state that the product is otherwise launch-ready.**
