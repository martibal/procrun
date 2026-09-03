# ProcRun final build and release gates

Status: **LOCKED FOR WEBSITE BUILD**
Canonical product spec: `docs/PRODUCT_FOUNDATION_FINAL.md`

These gates supersede earlier funded-project-first and TED-v2 build gates where they conflict with the final product foundation. Failed Phase 0B/0C results remain preserved as evidence and must not be rewritten as PASS.

## A1 — Source safety

A production source is usable only when RIGHTS, ACCESS and DATA SAFETY are all approved.

For every live retrieval:

- `require_live_source()` runs before network access;
- prohibited natural-person/supplier/contact fields are excluded before receipt;
- server-side projection is mandatory where the source contract depends on projection;
- schema drift outside the frozen allowlist fails closed;
- raw HTTP response bodies are not persisted for customer use;
- public availability never overrides these rules.

For MVP, TED Search API is the production source foundation.

## A2 — Absolute zero-PII intelligence boundary

No natural-person data may be collected, stored or processed in the intelligence plane.

Prohibited classes include natural-person names, contact people, personal email, phone, personal/postal addresses, tax identifiers, signatures and equivalent identifying fields.

Supplier/winner/contact records are not part of the MVP intelligence model.

Account, billing and support PII belongs to a separate control plane and may not enter the analytical ledger or model context.

The application must not intentionally persist client IP in ProcRun application-level intelligence logs.

## A3 — Canonical product object

The customer object is:

`TED notice -> infrastructure opportunity -> structured procurement fields -> evidence-backed demand tags where present -> supplier relevance -> market context -> customer feed`

The website must not be built around the retired funded-project `OPEN/CLOSED/PARTIAL` ontology.

Demand-tag absence must never be interpreted as evidence that no product/component demand exists.

## A4 — Evidence integrity

Every customer-visible ProcRun enrichment must retain source evidence.

For evidence-backed demand tags, the evidence contract contains at minimum:

- source/publication identifier;
- publication date;
- exact supporting source text/span;
- extraction method/version;
- observation/as-of timestamp;
- immutable version/hash reference where implemented.

No model or rule may invent a demand tag without accepted source support.

## A5 — Bounded demand enrichment

Demand tags are an enrichment layer, not the sole commercial product mechanism.

Allowed behavior:

- show a product/system tag where accepted source text supports it;
- retain exact evidence;
- use the tag to strengthen supplier relevance;
- aggregate tagged demand in market-intelligence views with appropriate coverage disclosure.

Prohibited claims:

- complete component decomposition;
- all requirements identified;
- hidden demand discovered;
- absence of a tag means absence of demand;
- every notice must contain a tag.

Phase 0B and Phase 0C remain failed tests of the broader v2 mechanism and must not be represented otherwise.

## A6 — Supplier relevance

Customer-facing relevance is explainable and bounded.

Allowed bands:

- High;
- Medium;
- Low;
- Not relevant.

Relevance may use supported profile criteria including infrastructure domain, demand tag where present, CPV, geography and value band.

Demand tags may strengthen a match but are not mandatory for a valid opportunity match.

Do not expose fake probabilistic precision such as `93% chance` unless a later validated probabilistic model explicitly supports that claim.

## A7 — Procurement stage

Raw TED notice types are mapped to tested customer-readable stage groups:

- planning / early notice;
- competition open / active;
- result / awarded;
- other / special procedure.

The exact mapping is frozen in code and unit-tested before launch.

The UI must not infer that a procurement is currently open beyond what the published source fields and implemented mapping support.

## A8 — TED transport

TED collection uses the approved field-bounded Search API route.

Requirements:

- explicit requested-field allowlist;
- no arbitrary customer-supplied field selection;
- ITERATION mode for complete walks where required;
- bounded page size/field-cell budget;
- duplicate detection;
- timeout/incomplete pagination fails closed;
- no raw response persistence;
- no buyer/contact/supplier-person fields in the customer intelligence contract.

The capability inventory in CI #161 remains the source-foundation baseline.

## A9 — Source-discovery closure

Known Portugal funded-project discovery source families are CLOSED BY DEFAULT for the MVP and are not website dependencies.

Do not resume source-family research merely to recreate the old funded-project product.

A route may be reopened only if genuinely new authoritative evidence satisfies all source gates without weakening the zero-PII boundary.

## A10 — PostgreSQL/history

PostgreSQL 16 remains the canonical historical intelligence store.

- source observations and transformed intelligence are versioned;
- corrections append new versions rather than rewriting historical evidence;
- immutable-ledger tables reject mutation where currently enforced;
- run/manifests and content hashes retain reproducibility;
- customer-specific saved/profile/control-plane state is kept separate from immutable source intelligence.

## A11 — Local-model boundary

Deterministic extraction remains primary for demand tags.

Any local-model fallback:

- receives only already-approved allowlisted text;
- can propose frozen category labels and exact evidence locations only;
- cannot invent source text;
- cannot determine unsupported procurement state;
- cannot bypass evidence validation;
- remains subject to explicit benchmark/production approval.

The current benchmark-candidate status does not by itself authorize unbounded production inference.

## A12 — Customer-safe read model

The website may consume only a customer-safe application contract produced after source validation and normalization.

Required separation:

1. source collection;
2. canonical notice normalization;
3. optional demand-tag extraction/evidence binding;
4. supplier relevance;
5. immutable intelligence storage;
6. customer-safe read model/API;
7. web/control plane.

The browser must not query raw TED payloads directly.

## A13 — Website definition of done

The first website build includes:

- public landing page;
- product/how-it-works page;
- methodology/source page;
- pricing page;
- supplier-profile onboarding;
- opportunity feed;
- opportunity detail with evidence;
- market-intelligence dashboard;
- saved opportunities;
- customer-safe CSV export;
- account/billing shell;
- responsive mobile/desktop behavior;
- explicit loading/empty/error/stale-data states.

No CRM, bid writer, contact database, supplier/winner database or procurement-submission workflow is required.

## A14 — Feed behavior

Default feed behavior follows `PRODUCT_FOUNDATION_FINAL.md`:

- Portugal;
- active/current opportunity stages;
- infrastructure universe only;
- newest first;
- supplier relevance applied where a profile exists;
- award/result records excluded from default active view;
- clear last-refresh/data-through timestamp.

Every feed item must link to an evidence-capable detail page.

A notice remains eligible for the feed even when no demand tag is present.

## A15 — Market-intelligence integrity

Charts and aggregates must expose data completeness where missing fields matter.

Value-based charts must disclose the share/count of records with populated estimated value. Missing values must not silently be treated as zero.

Demand-tag charts must clearly represent only tagged/evidence-backed records and must not imply complete taxonomy coverage.

Market-intelligence outputs derive from the same approved infrastructure procurement universe as the feed.

## A16 — Commercial packaging

Implementation package is locked as:

**ProcRun Portugal — €149/month**

MVP includes one supplier profile/workspace, Portugal infrastructure feed, evidence detail, evidence-backed demand tags where available, saved opportunities, market intelligence and customer-safe CSV export.

No permanent free tier.

A sample/demo mode is permitted using synthetic or explicitly approved publishable examples.

Checkout/payment activation remains blocked until A19 is green.

## A17 — No unsupported product claims

The website must not claim:

- comprehensive EU-funded-project coverage;
- reliable months-before-tender lead discovery;
- complete component decomposition;
- guaranteed discovery of every commercial requirement;
- complete procurement coverage beyond the implemented TED source boundary;
- guaranteed direct bid eligibility;
- win probability;
- EU/TED endorsement;
- real-time monitoring unless the actual scheduler/latency supports it.

## A18 — Cost ceiling

Projected trailing-30-day recurring core infrastructure spend:

- target: <= NOK 400/month;
- warning above NOK 400/month;
- no recurring architecture change above NOK 500/month without explicit architecture review.

Customer-volume-driven payment fees are tracked separately.

## A19 — Paid customer release gate

Before enabling paid customer release:

- legal entity/merchant identity is final;
- Terms of Service/subscription terms are published;
- Privacy Notice is published;
- account/billing/support PII is separated from intelligence data;
- payment-provider account and VAT/invoicing flow are approved;
- processor/subprocessor inventory and required DPAs are complete;
- current source attribution/methodology obligations are reflected;
- no analytics/session-replay/advertising SDK is enabled by default;
- reverse-proxy/application logging is configured so ProcRun does not intentionally retain client IP in the intelligence data plane;
- TLS, secrets, least privilege, encrypted backup and restore procedure are verified;
- then-current source rights/attribution and customer terms receive a short external legal review.

These are release gates, not blockers for building stages before payment activation.

## A20 — Website-build readiness

Once `docs/PRODUCT_FOUNDATION_FINAL.md`, this file and the aligned README are merged with green CI, product-definition work is complete for the first website implementation.

**Do not create another product-feasibility test before beginning the web build.**

Do not reopen funded-project source discovery for the MVP. Implementation may expose engineering defects that require fixes, but those are implementation work, not a reason to return to product-hypothesis testing unless an absolute source/privacy contradiction appears.