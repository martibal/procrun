# ProcRun final build and release gates

Status: **PRODUCT BUILD APPROVED; LIVE FUNDED-PROJECT INGEST FAIL-CLOSED UNTIL A1**
Canonical product spec: `docs/PRODUCT_FOUNDATION_FINAL.md`

These gates are authoritative. Historical product files cannot override them.

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

Current PRR Projects/dados.gov.pt evidence is promising but not sufficient to mark A1 green under ProcRun's stricter absolute rule: portal policy says datasets may not contain personal data and State datasets default to CC BY 4.0 unless otherwise specified, but the exact machine route/free-text safety guarantee is not yet frozen source-specifically. The collector therefore remains disabled.

## A2 — Procurement source safety

TED Search API remains APPROVED for field-bounded procurement evidence and market context. Every network collector must call `require_live_source()` before retrieval. Unknown fields, incomplete pagination, stale compliance review or prohibited field expansion fail closed.

## A3 — Absolute zero-PII intelligence boundary

No natural-person data may be collected, stored or processed in the intelligence plane. Account, billing and support data live in a separate control plane and may not enter analytical ledger/model context.

## A4 — Canonical product object

`funded project -> source-evidenced component -> procurement evidence -> conservative match -> OPEN/PARTIAL/CLOSED/UNRESOLVED -> supplier runway`

A TED-only opportunity feed is not the canonical product.

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

Source observations, component extraction, candidate matching and state classifications are append-only/versioned where implemented. Historical outputs retain cutoff, rule/model versions and SHA-256-linked evidence so results can be reconstructed.

## A11 — Customer-safe read model

Browser/API surfaces consume only the post-validation read model. No raw source response, beneficiary/contact/person field or unvalidated model output reaches the browser.

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

## A20 — Authoritative build readiness

A20 is the only authoritative `GO` source.

**A20 PRODUCT BUILD: GO.**

The product mechanism, differentiation, evidence contract, matching semantics, source interfaces and customer surfaces are sufficiently frozen to build now. No further TED-v2 feasibility testing is required.

**A20 LIVE FUNDED-PROJECT INGEST: BLOCKED BY A1.**

This does not block implementation. Build against the canonical `FundingProject` contract and safe fixtures; source activation is a controlled switch after A1, not a product redesign.

**A20 PAID PRODUCTION: BLOCKED until A1 + A19 are green.**

No other README/spec/history file may claim stronger readiness than these three A20 states.
