# ProcRun final build and release gates

Status: **WEB BUILD APPROVED; LIVE FUNDED-PROJECT INGEST REMAINS FAIL-CLOSED UNTIL SOURCE ACTIVATION GATES ARE GREEN**
Canonical product spec: `docs/PRODUCT_FOUNDATION_FINAL.md`

These gates are authoritative. Historical product files cannot override them.

## A0 — Pre-web technical completion rule

The web build may start only when the browser-facing technical contract is frozen strongly enough that unresolved live-source activation cannot force a later UI/data-contract redesign.

Before A20 may become `WEB BUILD: GO`, all of the following must be complete:

- A2/A3 source and zero-PII boundaries are enforced in code;
- canonical FundingProject -> component -> procurement -> state orchestration exists and is covered by end-to-end fixture tests;
- customer-safe read models are frozen and tested so the web layer never needs raw source/ledger objects;
- component/project state ontology is internally consistent across domain models, ledger constraints, read models and docs;
- deterministic hashes/version identifiers needed by the trust UX are available at the read boundary;
- database migrations can be applied from an empty PostgreSQL database and append-only invariants are tested;
- live collectors fail closed on unknown fields, incomplete pagination, stale compliance review, unapproved source or schema drift;
- incomplete required procurement coverage cannot produce `OPEN`;
- CI runs lint, typing, unit/integration tests and the pre-web readiness regression gate;
- unresolved source-activation work is isolated behind frozen interfaces and cannot change the web-facing read model.

A1 and national procurement-source approval remain mandatory before the corresponding live data paths are enabled. They do not block web implementation once the fail-closed interfaces and customer-safe read boundary are frozen.

A legal/commercial release item that does not change the technical product contract remains in A19.

## A1 — Funded-project source activation

A funded-project source may go live only when RIGHTS, ACCESS and DATA SAFETY are all APPROVED for the exact machine route and retained field surface.

Required:

- commercial reuse/derivative use explicitly supported;
- automated retrieval permitted;
- no natural-person data can enter the intelligence plane before receipt;
- every retained free-text field is covered by the same pre-receipt safety guarantee;
- no `download then filter` workaround;
- route/schema drift fails closed;
- source review has an expiry date.

Current PRR Projects/dados.gov.pt evidence remains promising but is not sufficient to mark A1 green under ProcRun's absolute rule. The current official dados.gov.pt terms state that datasets on the portal cannot contain personal data, but the same terms also permit publication where explicit consent or another legal basis exists. The current help page says only anonymised data may be published. Because those portal-level statements do not remove the source-specific/free-text ambiguity for the PRR Projects distribution, the route remains CONDITIONAL until the exact machine route and retained text fields receive an authoritative source-specific safety guarantee. The collector therefore remains disabled.

This blocks live funded-project ingestion, not web implementation.

## A2 — Procurement source safety

TED Search API remains APPROVED for field-bounded procurement evidence and market context. Every network collector must call `require_live_source()` before retrieval. Unknown fields, incomplete pagination, stale compliance review or prohibited field expansion fail closed.

A Portuguese national procurement source must independently pass `docs/NATIONAL_PROCUREMENT_SOURCE_GATE.md` before it may satisfy national coverage for live `OPEN` classification. Until then, required-source coverage remains incomplete and the classifier must abstain as `UNRESOLVED`.

## A3 — Absolute zero-PII intelligence boundary

No natural-person data may be collected, stored or processed in the intelligence plane. Account, billing and support data live in a separate control plane and may not enter analytical ledger/model context.

## A4 — Canonical product object and state ontology

`funded project -> source-evidenced component -> procurement evidence -> conservative component state -> project aggregate state -> supplier runway`

Component states are exactly `OPEN`, `CLOSED`, `UNRESOLVED`.

Project states are exactly `OPEN`, `PARTIAL`, `CLOSED`, `UNRESOLVED`.

`PARTIAL` is a project-level aggregate state under the current implementation, not a component state. A TED-only opportunity feed is not the canonical product.

## A5 — Evidence integrity / zero unsupported inference

Every accepted positive component and procurement match must retain exact source evidence, source identifier, observation cutoff, method/version and immutable hash/version reference.

No model/rule may invent source text, demand, procurement evidence or state.

Blanket claims such as `100% accurate`, `trust blindly` or `zero inference` across all states are prohibited. `100% source-verified` may describe only a positive evidence object that actually satisfies this contract.

## A6 — OPEN invariant

OPEN is not a source fact. It means only:

`No relevant procurement found in approved indexed sources as of DATE.`

OPEN requires complete required-source coverage. Incomplete coverage, review-band evidence or ambiguous component scope yields `UNRESOLVED`.

False OPEN is treated as the highest-cost error.

## A7 — Matching hierarchy

Tier A/B evidence may close a component only under `MATCHING_RULES.md`. Tier C remains review-only. Semantic similarity alone never closes a component. Post-cutoff evidence never rewrites an earlier historical state.

## A8 — Component extraction

Deterministic extraction is primary. Supported domains/categories are frozen and versioned. Unmatched scope is retained for bounded fallback; it is never interpreted as no demand.

## A9 — Local model boundary

A production-approved local model may propose only a frozen category plus exact source span from already-approved text. Deterministic validation must prove the span exists verbatim. The model cannot set component state or procurement match state.

The initial web build does not depend on an active local-model fallback; deterministic incompleteness abstains.

## A10 — Ledger/reproducibility

Source observations, component extraction, candidate matching and state classifications are append-only/versioned. Historical outputs retain cutoff, rule/model versions and SHA-256-linked evidence so results can be reconstructed.

## A11 — Customer-safe read model

Browser/API surfaces consume only the post-validation read model. No raw source response, beneficiary/contact/person field or unvalidated model output reaches the browser.

The read-model schema is implemented in code and regression-tested. The canonical orchestration produces a deterministic content hash/version at this boundary. This is the sole data contract the web implementation may consume.

## A12 — Supplier relevance

Relevance is deterministic/profile-based and explainable. It may prioritize domain/category/CPV/geography/value preferences but cannot override evidence state and is never presented as win probability.

## A13 — Product UX

The customer-facing app centers on runway, not tender search:

- project/component feed;
- funded-project detail;
- component evidence/history;
- procurement evidence;
- saved items;
- market context;
- profile;
- customer-safe export;
- account shell.

## A14 — Trust UX

Every commercial runway item exposes project-scope evidence, procurement evidence where present, state wording, coverage status, observed/as-of timestamp and immutable version reference. Source facts and ProcRun conclusions are visually distinct.

## A15 — Market context integrity

TED market views disclose missingness. Funding aggregates remain disabled until A1 is green. Market context may not silently become the primary TED-only product.

## A16 — Commercial packaging

Launch package: **ProcRun Portugal — €149/month**. No permanent free tier. Sample/demo content must be synthetic or explicitly approved for publication.

## A17 — Unsupported claims

Do not claim complete bill of materials, every future purchase, guaranteed months-ahead lead time, complete procurement coverage, probabilistic GO/NO-GO, win probability, buyer-person intelligence or EU/source endorsement.

## A18 — Cost ceiling

Target recurring core infrastructure spend <= NOK 400/month; warning above NOK 400; architecture review required above NOK 500/month excluding volume-linked payment fees.

## A19 — Paid release

Before checkout: legal entity/merchant identity, terms, privacy notice, VAT/invoicing, processor inventory/DPAs, source attribution, TLS/secrets/least privilege, backup/restore, control-plane separation and short external legal review must be green. A1 must also be green, and every source required for live `OPEN` coverage must be production-approved.

A19 is a paid-release gate and does not block implementation of the web application against safe fixtures/read models.

## A20 — Authoritative web-build readiness

A20 is the only authoritative `GO` source for starting the web build.

**A20 WEB BUILD: GO.**

Basis for GO:

1. The canonical funded-project -> component -> procurement -> component state -> project state orchestration is implemented and covered by integrated fixture regression tests.
2. A11 customer-safe read models are implemented and regression-tested as the sole browser/API data contract.
3. Exact evidence provenance, deterministic hashes/version identifiers, empty-database migrations and append-only persistence invariants are implemented and tested.
4. False-OPEN protection is fail-closed: incomplete required-source coverage yields `UNRESOLVED`; TED-only absence cannot satisfy national coverage where national coverage is required.
5. Live collectors remain gated by source approval, field allowlists, schema/compliance checks and pagination completeness.
6. The latest PR #50 CI run before this readiness change was green. This readiness change must itself pass CI before merge.
7. Remaining uncertainty is confined to external live-source activation and paid-release gates; neither requires changing the frozen browser read model.

**A20 LIVE FUNDED-PROJECT INGEST: BLOCKED BY A1.**

**A20 LIVE PORTUGAL OPEN CLASSIFICATION: BLOCKED until required national procurement coverage is approved and completed.**

**A20 PAID PRODUCTION: BLOCKED until A1 + required live procurement-source gates + A19 are green.**

Web implementation must use safe fixtures or approved post-validation read-model data until those live gates are green. No UI code may bypass the read boundary to access raw source responses or unvalidated ledger objects.

No other README/spec/history file may claim stronger readiness than A20.
