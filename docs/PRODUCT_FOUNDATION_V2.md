# ProcRun Product Foundation v2.0

Status: LOCKED FOR WEBSITE BUILD
Date: 2026-09-03
Supersedes: the funded-project-first product promise in Product Requirements v1.0 and the original README positioning.

## 1. Product definition

ProcRun is a supplier-facing opportunity-intelligence product for active public infrastructure procurement.

The locked one-sentence definition is:

> **ProcRun turns public procurement notices into supplier-specific product demand.**

The customer does not primarily receive a tender search result. ProcRun takes a public procurement notice, identifies the purchasable requirements inside it, maps those requirements to a supplier's product profile, and presents the commercially relevant opportunities with dated source evidence.

The canonical product pipeline is:

`TED notice -> procurement opportunity -> purchasable requirements -> supplier relevance -> evidence -> customer feed`

The primary product object is therefore a **supplier-specific procurement opportunity**, not a funded project and not a generic tender.

## 2. Why the product exists

Public procurement platforms are good at publishing tenders. Tender-intelligence products are good at helping companies search for tenders that may match their business. That still leaves a supplier with a difficult commercial question:

> What is actually being bought inside these procurements, and which of those requirements match what we sell?

ProcRun answers that question.

A supplier of pumps, valves, instrumentation, electrical systems, rail equipment, construction products or other infrastructure inputs may never bid for the main public contract. Its commercial opportunity can sit inside a much larger contract won by a general contractor, EPC contractor, installer or systems integrator.

ProcRun therefore treats the demand embedded in a procurement as the valuable unit.

## 3. Locked differentiation

The market position is not "better tender alerts" and not "AI tender search".

The locked differentiation is:

> **Tender platforms tell you which contracts may be relevant. ProcRun tells you what those contracts actually create demand for.**

The product must preserve this distinction in UX, copy and feature prioritisation.

ProcRun wins when a customer can see, faster than through ordinary tender monitoring:

- what the procurement is for;
- which separately purchasable products, equipment, systems or specialist services are implied by the published scope;
- which of those requirements match the customer's own offer;
- why the match was made;
- where the evidence came from;
- how commercially important the opportunity appears.

ProcRun does not attempt to win by having the largest database, by replacing a CRM, or by automating bid writing.

## 4. Validated source foundation

The production foundation is TED Search API.

The final live capability inventory in CI #161 validated the current Portugal launch universe over the preceding 12 months:

- 18,776 Portugal notices;
- 4,893 infrastructure notices;
- 3,812 later/active-stage infrastructure notices;
- 58 early infrastructure notices;
- 100.0% title + description population for both early and later infrastructure slices;
- 98.2% procedure-identifier population overall;
- 98.1% contract-nature population;
- 87.4% procedure-type population;
- 71.9% estimated-value + currency population;
- 77.3% place-of-performance subdivision population;
- 7.9% infrastructure EU-funding marker coverage;
- zero validated early-to-later procedure links in the tested early slice.

All retained qualification fields passed field-bounded server-side projection in the live test.

Product hypotheses from the live inventory:

| Hypothesis | Result |
| --- | --- |
| Active infrastructure opportunity feed | SUPPORTED |
| Procurement market intelligence | SUPPORTED |
| Early procurement runway | NOT SUPPORTED |
| Comprehensive EU-funding subset | NOT SUPPORTED |

The website and customer claims must follow these results. ProcRun must not claim comprehensive EU-funded-project coverage or reliable pre-tender lead-time discovery from the current evidence.

## 5. Launch market and expansion

Launch geography: **Portugal**.

The product architecture must be country-extensible because TED is the data foundation, but the website MVP must not imply that countries not yet activated are covered.

Expansion is now driven by the same TED qualification method and commercial demand, not by a locked Italy-then-Poland project-discovery sequence. The old country sequence is retired.

## 6. Ideal customer profile

Primary ICP:

- manufacturers of infrastructure components and equipment;
- OEMs;
- distributors and technical wholesalers;
- systems suppliers;
- specialist subcontractors;
- engineering suppliers whose products/services are embedded in larger public-infrastructure contracts.

Initial infrastructure domains:

- water and wastewater;
- transport and rail;
- ports and coastal infrastructure;
- energy/electrical infrastructure and efficiency;
- resilience, fire and related specialist systems;
- adjacent civil-infrastructure categories supported by the frozen CPV and component taxonomies.

The product is especially valuable when the customer is not necessarily the prime bidder.

Secondary ICP:

- business-development teams at direct public-sector contractors;
- market-intelligence teams;
- commercial teams assessing public infrastructure demand by geography/category/value.

## 7. Customer job to be done

Primary job:

> **Show me the public infrastructure procurements that create demand for the products I sell, and show me why they are relevant.**

Secondary jobs:

- understand current demand by product category;
- identify geographic demand concentration;
- understand typical procurement values and procedure types;
- monitor changes/new opportunities without repeatedly searching TED;
- inspect source evidence before deciding whether to pursue an opportunity.

## 8. MVP customer workflow

### Step 1 — Supplier profile

The customer defines what the company sells. MVP accepts a deliberately bounded commercial product profile rather than free-form CRM data.

Required profile inputs:

- company display name;
- target market: Portugal for MVP;
- product categories selected from ProcRun taxonomy;
- optional product keywords/phrases;
- optional CPV inclusions;
- optional CPV exclusions;
- optional regions;
- optional minimum/maximum procurement value;
- optional requirement categories to exclude.

The intelligence plane must not require named employees, contact people, personal email addresses or personal phone numbers.

### Step 2 — Opportunity feed

ProcRun continuously evaluates qualifying TED notices and produces a ranked feed.

The customer sees opportunities, not raw notices.

Each feed card shows:

- opportunity title;
- location/region when present;
- publication date;
- procurement stage;
- estimated procurement value when present;
- top matched purchasable requirements;
- relevance band;
- short evidence-backed explanation;
- number of matching requirements;
- source freshness/as-of date.

### Step 3 — Opportunity detail

The detail page explains the commercial interpretation without hiding the source.

It shows:

- procurement summary;
- procedure/publication identifiers;
- publication date;
- procedure/contract type where present;
- estimated value and currency where present;
- place of performance where present;
- all extracted purchasable requirements;
- customer-match state for each requirement;
- exact source evidence span for each accepted requirement;
- source reference to TED;
- methodology note;
- confidence/relevance explanation;
- source-as-of timestamp;
- immutable evidence/version identifier.

### Step 4 — Market intelligence

The customer can aggregate the same opportunity universe by:

- time;
- region;
- product/requirement category;
- CPV family;
- procurement stage/type;
- estimated value bands.

MVP market-intelligence outputs:

- opportunity count trend;
- estimated-value trend for records where value exists;
- top requirement categories;
- top regions;
- stage/type distribution;
- category-by-region table;
- share of records with value/location data so missingness is visible.

## 9. Canonical customer-facing data model

### Opportunity

Required fields:

- `opportunity_id` — stable ProcRun ID;
- `publication_number`;
- `publication_date`;
- `title`;
- `scope_summary` — evidence-grounded normalized summary;
- `notice_type`;
- `procurement_stage`;
- `procedure_identifier` — nullable;
- `contract_nature` — nullable;
- `procedure_type` — nullable;
- `estimated_value` — nullable;
- `estimated_value_currency` — nullable;
- `region` — nullable;
- `cpv_codes`;
- `requirements[]`;
- `overall_relevance`;
- `relevance_reasons[]`;
- `source_name` = TED;
- `source_reference`;
- `observed_at`;
- `content_hash` / immutable version reference.

### PurchasableRequirement

Required fields:

- `requirement_id`;
- `canonical_category`;
- `label`;
- `evidence_text`;
- `evidence_start`;
- `evidence_end`;
- `extraction_method`;
- `supplier_match`;
- `match_reasons[]`;
- `relevance_score` or deterministic ordinal band;
- `version_id`.

### SupplierProfile

Required fields:

- `supplier_profile_id`;
- `display_name`;
- `target_country`;
- `included_categories[]`;
- `included_terms[]`;
- `included_cpv[]`;
- `excluded_cpv[]`;
- `regions[]`;
- optional value bounds;
- created/updated timestamps in the control plane.

No natural-person identity is part of the analytical profile contract.

## 10. Relevance semantics

Customer-facing relevance bands are:

- **High** — one or more strong requirement matches supported by exact evidence and no material conflict with the supplier profile;
- **Medium** — plausible commercial match with sufficient evidence but weaker category/term specificity;
- **Low** — weak but non-zero relationship; hidden by default in the main feed;
- **Not relevant** — excluded from customer feed.

The initial web implementation must display relevance as an explainable band, not as fake precision such as "93% chance".

Every High/Medium match must be explainable from stored evidence and deterministic/profile-match reasons.

A generative model may not invent unsupported requirements or set customer-facing relevance without validation against source evidence and frozen categories.

## 11. Procurement stage semantics

The web product should collapse raw TED notice types into customer-readable stage groups while retaining the raw type on detail pages.

Locked stage groups:

- **Planning / early notice** — planning-type notices where present; informative but not marketed as a reliable pre-tender runway;
- **Competition open / active** — contract/competition notices indicating a live or recently published opportunity;
- **Result / awarded** — result/award-type notices; primarily useful for market intelligence/history and normally excluded from the default "Active" feed;
- **Other / special procedure** — supported TED notice types that do not map cleanly; visible with explicit raw type and no invented state.

The exact notice-type mapping must be frozen in code before launch and unit-tested.

## 12. Feed defaults

Default customer feed:

- target country = Portugal;
- stages = active competition plus supported current opportunity types;
- relevance = High + Medium;
- sort = newest first, with relevance as secondary ordering;
- result/award notices = excluded by default;
- Low relevance = excluded by default;
- no hidden inference that an opportunity is still open beyond what published source fields support.

Filters:

- date range;
- relevance;
- product/requirement category;
- region;
- procurement stage;
- CPV;
- value range where value exists;
- has estimated value;
- newly detected since last visit.

## 13. Website information architecture

Public routes:

- `/` — landing page;
- `/product` — how ProcRun works;
- `/market-intelligence` — secondary capability;
- `/methodology` — evidence, source and matching methodology;
- `/pricing` — price and included features;
- `/about` — concise company/product context;
- `/login` — account entry;
- `/terms` and `/privacy` — required before paid release.

Authenticated routes:

- `/app` — opportunity feed;
- `/app/opportunities/[id]` — opportunity detail;
- `/app/market` — market intelligence;
- `/app/profile` — supplier profile;
- `/app/saved` — saved opportunities;
- `/app/account` — subscription/account settings.

No CRM, contact database, bid writer or messaging centre is part of MVP navigation.

## 14. Landing-page content contract

The landing page must answer these questions in order:

1. What is ProcRun?
2. What problem does it solve?
3. How is it different from tender alerts?
4. What does an actual opportunity look like?
5. How does matching work?
6. Who is it for?
7. What data/source does it use?
8. What does it cost?
9. Why should the customer trust the result?
10. What should the visitor do next?

Locked hero direction:

**Headline:**

> Find the public procurements that create demand for what you sell.

**Subheadline:**

> ProcRun reads active infrastructure procurements, identifies the products and systems being bought, and matches those requirements to your supplier profile — with source evidence for every match.

**Primary CTA:** `See relevant opportunities`

**Secondary CTA:** `See how ProcRun works`

Do not lead with AI, CPV, APIs, vector search, embeddings, LLMs or other implementation terminology.

## 15. Product-page content contract

The product page should explain the transformation visually:

`Public procurement notice`

-> `Purchasable requirements identified`

-> `Matched to what your company sells`

-> `Ranked opportunity with evidence`

The key comparison copy is:

> Tender monitoring finds contracts. ProcRun identifies the product demand inside them.

The example must be clearly illustrative unless based on an approved publishable source example.

## 16. Opportunity-card copy contract

Cards must communicate value in under ten seconds.

Recommended hierarchy:

1. title;
2. relevance band;
3. matched requirements;
4. value + region + publication date;
5. procurement stage;
6. one-sentence reason;
7. open-detail action.

No card should be dominated by raw procurement jargon or unexplained identifiers.

## 17. Trust and evidence

Trust is part of the product, not a legal footer.

Every opportunity detail must expose:

- source = TED;
- publication identifier/date;
- source link/reference;
- the source text supporting extracted requirements;
- an as-of/observed timestamp;
- clear distinction between source facts and ProcRun transformation;
- methodology link.

The website must never imply EU/TED endorsement.

## 18. Data-safety boundary

The intelligence plane retains the existing absolute rule:

> **No natural-person data may be collected, stored or processed in the ProcRun intelligence pipeline.**

Pre-receipt exclusion remains mandatory. "Receive then delete/filter" is prohibited.

For TED, only approved field-projected requests may be used. Contact person, personal email, phone, personal/postal address, supplier/winner person data, tax identifiers and equivalent personal fields are prohibited.

Account, billing and support data belong to a physically/logically separate control plane and must not enter the analytical ledger/model context.

The public application must not intentionally persist client IP in ProcRun application logs.

## 19. Source policy

TED Search API is the MVP production source.

Known Portugal funded-project discovery source families are closed by default and are not website blockers.

They may only be reopened if genuinely new authoritative evidence establishes all required source gates. The product no longer depends on a funded-project discovery source.

No website feature may silently introduce a blocked source.

## 20. MVP pricing and commercial packaging

The website build requires a stable commercial object, so the launch package is locked for implementation as follows:

### ProcRun Portugal — €149/month

Includes:

- one supplier profile;
- Portugal opportunity feed;
- High + Medium relevance matching;
- full opportunity details and evidence;
- saved opportunities;
- market-intelligence dashboard;
- CSV export of the customer's matched opportunity list;
- one account workspace.

Launch billing cadence: monthly.

Annual billing and multi-seat/team plans are deferred until there is real customer evidence.

Public pricing copy may say `€149/month` but checkout cannot go live until the customer-control-plane release gates are complete.

The product should support a **sample/demo mode** before paid launch. Demo mode must use either frozen synthetic examples or explicitly approved publishable examples; it must not require creating fake live customer data.

No permanent free tier is part of MVP.

## 21. Onboarding contract

The onboarding flow is short and commercial, not technical.

Screen 1: `What do you sell?`
- category selector;
- optional plain-language product terms.

Screen 2: `Where do you want opportunities?`
- Portugal selected/locked for MVP;
- optional region filters.

Screen 3: `Refine the feed`
- optional CPV/value exclusions;
- can be skipped.

Screen 4: `Your first matched opportunities`
- immediately opens the feed.

Do not ask users to understand CPV to use the product.

## 22. Saved opportunity behavior

MVP allows a customer to save/bookmark an opportunity.

Saved state belongs to the customer control plane, separate from the canonical intelligence object.

No notes, assignment, CRM workflow or collaboration comments in v1 website unless later explicitly approved.

## 23. Delivery cadence

The web product is designed for at least daily refresh. More frequent refresh may be enabled if operational cost and source limits remain comfortably within the architecture gate.

The UI must always show a clear data-through/last-refresh timestamp.

Do not promise real-time monitoring unless the implemented scheduler and observed end-to-end latency support it.

## 24. Notification scope

Email alerts are not required to begin the website build and are not part of the first implementation milestone.

The core product must work as a pull-based web application first.

If alerts are added later, they must reuse the same server-side customer relevance result and never include prohibited intelligence-plane personal data.

## 25. Search scope

MVP search is search/filter across already-approved ProcRun opportunity objects.

It is not an unrestricted proxy to TED and must not permit arbitrary field retrieval that bypasses the source allowlist.

## 26. Customer-facing terminology

Use:

- Opportunity
- Matched requirements
- Product demand
- Relevance
- Evidence
- Procurement stage
- Source
- Published
- Estimated value
- Region

Avoid as primary customer language:

- embedding;
- vector similarity;
- LLM;
- inference graph;
- component-state ledger;
- funding-to-procurement coverage;
- `OPEN/CLOSED/PARTIAL` from the retired product promise.

Internal legacy engine states may remain in code where still needed for historical tests, but they are not the v2 website ontology.

## 27. Non-goals

The website MVP is not:

- a bid-writing tool;
- a CRM;
- a contact-person database;
- a supplier/winner database;
- a procurement submission portal;
- a guarantee that the customer can bid directly;
- a prediction of who will win;
- a probability-of-win engine;
- a comprehensive EU-funded-project database;
- a reliable months-before-tender early-warning product;
- an unrestricted TED browser.

## 28. Implementation architecture boundary

The website must consume a published/customer-safe application data contract, not query arbitrary raw source payloads directly.

Required separation:

1. source collection and validation;
2. canonical notice normalization;
3. requirement extraction/evidence binding;
4. supplier relevance computation;
5. immutable intelligence storage/versioning;
6. customer-safe read model/API;
7. web UI/control plane.

No raw TED response body is persisted for website use.

## 29. Definition of ready for website build

Website implementation may begin when this document is merged and CI is green.

The web team does **not** need additional source discovery, country research, market-size research or product-definition work before starting.

The remaining pre-paid-launch obligations are release obligations, not blockers for building:

- final merchant/legal identity;
- Terms of Service;
- Privacy Notice;
- VAT/invoicing flow;
- payment-provider approval/configuration;
- processor/subprocessor inventory and DPAs;
- production TLS/secrets/least-privilege/backups;
- customer-control-plane privacy verification;
- external legal review of then-current terms/source attribution.

## 30. Website build order

The implementation order is locked as:

1. web application shell + design system;
2. customer-safe opportunity read model/API contract;
3. public landing/product/methodology/pricing pages;
4. supplier-profile onboarding;
5. opportunity feed;
6. opportunity detail + evidence view;
7. market-intelligence dashboard;
8. saved opportunities;
9. account/billing shell;
10. release hardening and legal/control-plane activation.

Do not block stages 1–8 on payment activation.

## 31. Product decision authority

This document is the canonical v2 product foundation.

If older documents conflict with it on product promise, source dependency, country expansion order, customer ontology or website scope, **this document wins**.

The following remain absolute and are not weakened by v2:

- no natural-person data in the intelligence plane;
- pre-receipt field safety;
- source rights/access/data-safety gates;
- exact evidence provenance;
- fail-closed schema behavior;
- append-only historical intelligence where applicable;
- no unsupported customer claims.

Any future change to these boundaries requires an explicit Product Foundation review.