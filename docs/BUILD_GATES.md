# ProcRun final build and release gates

Status: **PRE-WEB TECHNICAL HARDENING IN PROGRESS; WEB BUILD BLOCKED UNTIL A20 IS GREEN**
Canonical product spec: `docs/PRODUCT_FOUNDATION_FINAL.md`

These gates are authoritative. Historical product files cannot override them.

## A0 — Pre-web technical completion rule

The web build must not start merely because the product concept is stable. ProcRun starts web implementation only when all technical foundations that could force a later product/data redesign are green.

Before A20 may become `WEB BUILD: GO`, all of the following must be complete:

- A1 funded-project source is production-approved for the exact route and retained field surface;
- A2/A3 source and zero-PII boundaries are enforced in code;
- canonical FundingProject -> component -> procurement -> state orchestration exists and is covered by end-to-end fixture tests;
- customer-safe read models are frozen and tested so the web layer never needs raw source/ledger objects;
- component/project state ontology is internally consistent across domain models, ledger constraints, read models and docs;
- deterministic hashes/version identifiers needed by the trust UX are available at the read boundary;
- database migrations can be applied from an empty PostgreSQL database and append-only invariants are tested;
- live collectors fail closed on unknown fields, incomplete pagination, stale source review, unapproved source or schema drift;
- CI runs lint, typing, unit/integration tests and the pre-web readiness regression gate;
- no unresolved technical issue is known that would require changing the web-facing contract after UI implementation begins.

A legal/commercial release item that does not change the technical product contract may remain in A19, but data-source, state, read-model, persistence or pipeline uncertainty may not be deferred into the web build.

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

## A2 — Procurement source safety

TED Search API remains APPROVED for field-bounded procurement evidence and market context. Every network collector must call `require_live_source()` before retrieval. Unknown fields, incomplete pagination, stale compliance review or prohibited field expansion fail closed.

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

## A10 — Ledger/reproducibility

Source observations, component extraction, candidate matching and state classifications are append-only/versioned. Historical outputs retain cutoff, rule/model versions and SHA-256-linked evidence so results can be reconstructed.

## A11 — Customer-safe read model

Browser/API surfaces consume only the post-validation read model. No raw source response, beneficiary/contact/person field or unvalidated model output reaches the browser.

A11 is not green until the read-model schema exists in code and has regression tests that prove only approved customer fields are emitted.

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

Before checkout: legal entity/merchant identity, terms, privacy notice, VAT/invoicing, processor inventory/DPAs, source attribution, TLS/secrets/least privilege, backup/restore, control-plane separation and short external legal review must be green. A1 must also be green.

A19 is a paid-release gate, not permission to defer data/pipeline/read-model uncertainty into the web build.

## A20 — Authoritative web-build readiness

A20 is the only authoritative `GO` source for starting the web build.

**A20 WEB BUILD: BLOCKED.**

Current blockers:

1. A1 funded-project source remains CONDITIONAL pending source-specific pre-receipt safety proof for the exact PRR Projects machine route and retained free-text fields.
2. The repository does not yet contain the complete canonical end-to-end runway orchestration layer from `FundingProject` through extraction/matching/project aggregation to a frozen customer-safe read model.
3. A11 customer-safe read-model schema is documented but not yet implemented as the sole browser/API contract.
4. A0 pre-web regression coverage has not yet proven the full pipeline/read boundary in one integrated fixture path.

**A20 LIVE FUNDED-PROJECT INGEST: BLOCKED BY A1.**

**A20 PAID PRODUCTION: BLOCKED until A1 + A19 are green.**

The next work is technical hardening only. Do not start the web application until the four A20 web-build blockers above are removed, CI is green, and this section is explicitly changed to `A20 WEB BUILD: GO` in a reviewed change.

No other README/spec/history file may claim stronger readiness than A20.
