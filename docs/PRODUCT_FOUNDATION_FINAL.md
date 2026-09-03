# ProcRun — final product foundation

Status: **READY FOR WEBSITE BUILD**
Date: 2026-09-03

This document is the canonical product definition for the first customer-facing ProcRun web application.

It supersedes earlier funded-project-first and TED-v2 product promises wherever they conflict with this document. Failed Phase 0B and Phase 0C results remain valid historical evidence and are not relabelled as PASS.

## 1. Product decision

ProcRun will be built as a **vertical infrastructure procurement intelligence product for suppliers**, using the production-safe TED Search API as the source foundation.

The product promise is deliberately narrower than the failed v2 hypothesis:

> **ProcRun turns public infrastructure procurement into a focused supplier intelligence feed: active opportunities, evidence-backed demand tags where they can be proven, and market context from the same procurement universe.**

ProcRun does not promise complete component decomposition of every notice. It does not promise hidden requirements, pre-tender runway, or comprehensive EU-funded-project discovery.

Canonical pipeline:

`TED notice -> infrastructure opportunity -> structured procurement fields -> evidence-backed demand tags where present -> supplier relevance -> market context -> customer feed`

## 2. Why this product is buildable now

The website is built only on capabilities already established by the source and validation work:

- TED is a production-usable source under ProcRun's field-bounded, pre-receipt zero-PII rules;
- Portugal has a substantial active infrastructure notice population;
- active infrastructure notice feed is supported;
- procurement market-intelligence dataset is supported;
- title and description are available in the approved source projection;
- structured CPV, geography, procedure/stage and estimated value are available with known completeness;
- the deterministic text layer repeatedly found evidence-backed normalized requirements in a material subset of notices;
- the CPV-blind signal reproduced across two disjoint 300-notice samples, but taxonomy breadth did not satisfy the stricter v2 gate.

Therefore demand tags are a **bounded enrichment**, not the sole commercial mechanism and not a completeness claim.

## 3. Commercial positioning

ProcRun is not positioned as a general tender portal, CRM or bid-writing suite.

The category is:

> **Infrastructure procurement intelligence for suppliers.**

Primary sales line:

> **From tenders to infrastructure demand.**

Supporting explanation:

> ProcRun gives suppliers one focused view of Portugal's public infrastructure procurement: what is active, which product or system categories are explicitly evidenced in the notice, and how that activity sits inside the wider market.

The strategic differentiation is the combination of four choices:

1. **Infrastructure-only focus.** ProcRun is not a universal public-sector tender inbox.
2. **Supplier-side view.** The product is designed for manufacturers, OEMs, distributors, technical wholesalers, systems suppliers and specialist subcontractors, including firms that may never be the prime bidder.
3. **Evidence-backed demand enrichment.** Product/system tags appear only when the source text supports them; every tag can be traced back to evidence.
4. **Opportunity + market context in one workflow.** The same approved procurement universe powers both the active feed and historical market-intelligence views.

This is the differentiation strategy to use in sales. Do not claim that no competitor can perform any of these individual functions. The product advantage is the narrow supplier workflow and infrastructure-specific combination.

## 4. Target customer

Primary ICP:

- manufacturers and OEMs supplying infrastructure equipment;
- distributors and technical wholesalers;
- systems and integration suppliers;
- specialist infrastructure subcontractors;
- commercial teams responsible for Portugal public-infrastructure demand.

The product is especially relevant when the customer's commercial opportunity exists inside a larger public contract and the customer may not be the entity bidding for the prime contract.

The MVP is not designed primarily for procurement lawyers, public buyers, generalist tender consultants, or bid-writing agencies.

## 5. Customer jobs

A customer should be able to answer these questions quickly:

- What relevant public infrastructure procurements are active now?
- Which of them fit the categories, CPVs, regions and value ranges I care about?
- Which product/system demand tags are explicitly evidenced in the notice?
- What exact source text supports that interpretation?
- Is current activity high or low relative to recent history?
- Which infrastructure domains, categories, regions and value bands are generating the most procurement activity?
- Which opportunities should I save, review or export for my own sales workflow?

## 6. MVP product surfaces

### 6.1 Public website

Routes:

- `/` — landing page;
- `/product` — product explanation;
- `/methodology` — source, evidence and limitations;
- `/pricing` — package and included features;
- `/login` — authentication entry point.

### 6.2 Authenticated application

Routes:

- `/app` — opportunity feed;
- `/app/opportunities/[id]` — opportunity detail;
- `/app/market` — market intelligence;
- `/app/profile` — supplier profile/preferences;
- `/app/saved` — saved opportunities;
- `/app/account` — account/billing shell.

## 7. Opportunity feed

Default feed:

- country: Portugal;
- active/current procurement stages only;
- infrastructure universe only;
- newest first;
- supplier relevance applied where profile exists;
- result/award notices excluded from the default active view;
- last-refresh and data-through timestamps visible.

Filters:

- infrastructure domain;
- demand tag/category where present;
- CPV;
- region/NUTS subdivision;
- estimated-value band where available;
- publication date;
- procedure/notice stage;
- saved/not saved.

Each feed card shows only fields supported by the customer-safe read model:

- notice title;
- publication date;
- stage;
- infrastructure domain;
- region where available;
- estimated value/currency where available;
- relevant CPV family;
- supplier relevance band/reason;
- evidence-backed demand tags where present;
- source/evidence link.

The absence of demand tags must be shown as neutral, not as evidence that no component demand exists.

## 8. Demand tags

Demand tags are a bounded enrichment layer.

Rules:

- a tag may be shown only when supported by accepted source text;
- exact evidence span is retained;
- extraction method/version is retained;
- no tag may be invented from unsupported inference;
- no customer-facing claim of complete component coverage;
- no claim that the tag was hidden from the notice title;
- no claim that every relevant supplier requirement has been identified;
- unmatched notices remain valid opportunities and remain in the feed.

Customer wording:

- use **"Demand identified"**, **"Product/system tags"** or **"Evidence-backed demand"**;
- do not use **"complete bill of materials"**, **"all components"**, **"hidden demand"** or equivalent completeness language.

## 9. Supplier relevance

Supplier profile is intentionally lightweight.

Customer selects:

- infrastructure domains;
- product/system categories from the supported taxonomy;
- optional CPV families;
- preferred Portuguese regions;
- optional value range.

Relevance bands:

- High;
- Medium;
- Low;
- Not relevant.

Relevance is explainable. A customer can see which selected domain/category/CPV/geography rule produced the match.

Demand tags strengthen relevance where present, but supplier relevance must not require a demand tag. CPV/domain/geography matches remain valid because the active-feed value proposition is broader than the failed complete-decomposition hypothesis.

Do not expose fake probabilistic scores.

## 10. Opportunity detail

The detail page contains:

- title and publication date;
- customer-readable stage;
- notice/procedure identifiers allowed by the safe source contract;
- CPV classification;
- infrastructure domain;
- geography where available;
- estimated value and currency where available;
- procedure type/contract nature where available;
- evidence-backed demand tags where present;
- exact supporting evidence for each tag;
- why this matched the supplier profile;
- source provenance and observation timestamp;
- save/export actions.

The page must clearly distinguish source facts from ProcRun classifications/enrichments.

## 11. Market intelligence

The market view is a first-class product surface, not a later add-on.

Initial views:

- notice count over time;
- estimated procurement value over time with completeness disclosure;
- activity by infrastructure domain;
- activity by CPV family;
- activity by region;
- activity by procedure/stage;
- activity by demand tag where evidence-backed tags exist;
- active vs historical/result activity.

All charts derive from the same approved TED infrastructure universe as the opportunity feed.

Missing estimated values are never treated as zero. Every value-based view exposes populated-record count/share.

## 12. Evidence contract

Every customer-visible ProcRun enrichment must be auditable.

Minimum evidence fields:

- TED publication identifier;
- publication date;
- observation/as-of timestamp;
- source field;
- exact source text/span for demand tags;
- extraction/classification method and version;
- immutable hash/version reference where implemented.

The UI should make evidence accessible without forcing the customer to read the entire raw notice.

## 13. Data and privacy boundary

Absolute rule:

> **No natural-person data may be collected, stored or processed in the ProcRun intelligence plane.**

This remains a pre-receipt requirement.

The customer intelligence plane excludes buyer contact people, supplier/winner people, personal email, phone, personal addresses, signatures and equivalent identifiers.

Account, authentication, billing and support data belong to a separate control plane and must not enter the intelligence ledger/model context.

The browser never receives raw TED responses.

## 14. Claims allowed on the website

Allowed:

- focused Portugal public-infrastructure procurement feed;
- infrastructure-specific supplier intelligence;
- evidence-backed demand tags where identified;
- filters by supported structured procurement fields;
- historical procurement market intelligence from the same source universe;
- evidence/provenance for ProcRun enrichments;
- supplier relevance based on explicit profile criteria.

Not allowed:

- complete component decomposition;
- guaranteed discovery of every commercial requirement;
- reliable months-before-tender lead discovery;
- comprehensive EU-funded-project coverage;
- complete coverage of all Portuguese public procurement outside the implemented TED source universe;
- contact-person intelligence;
- supplier/winner intelligence;
- win probability;
- bid eligibility guarantee;
- TED/EU endorsement;
- real-time claims unless scheduler latency actually supports them.

## 15. Landing-page message hierarchy

The first screen should communicate:

**Eyebrow:** `Infrastructure procurement intelligence for suppliers`

**Headline:** `From tenders to infrastructure demand.`

**Subheadline:** `See active public infrastructure procurement in Portugal, the product and system demand ProcRun can prove from the notice, and the market context behind it.`

Primary CTA before paid launch: `View sample` or `Join early access`.

After payment activation: `Start ProcRun Portugal`.

Second message:

> `Not another general tender inbox. ProcRun is built for companies that sell into infrastructure projects — including suppliers that may never bid for the prime contract themselves.`

Third message should demonstrate one opportunity card and one evidence-backed demand tag with the source evidence beside it.

Market-intelligence proof follows after the opportunity example.

## 16. Commercial package

Launch package:

> **ProcRun Portugal — €149/month**

Includes:

- one supplier workspace/profile;
- active Portugal infrastructure opportunity feed;
- evidence-backed demand tags where available;
- supplier relevance and filters;
- opportunity detail/evidence;
- saved opportunities;
- market-intelligence dashboard;
- customer-safe CSV export.

No permanent free tier.

Before checkout is activated, sample/demo content must be synthetic or explicitly approved for customer publication.

## 17. What not to build

Do not spend MVP time on:

- generic all-sector tender aggregation;
- CRM;
- bid writing;
- contact database;
- buyer-person discovery;
- supplier/winner database;
- procurement submission workflow;
- AI proposal generation;
- win probability;
- broad EU expansion;
- resurrecting funded-project source discovery;
- trying to force every notice through a complete component taxonomy.

## 18. Website implementation order

1. web application shell and design system;
2. customer-safe opportunity read model/API;
3. landing, product, methodology and pricing pages;
4. supplier profile/preferences;
5. active opportunity feed and filters;
6. opportunity detail and evidence view;
7. market-intelligence dashboard;
8. saved opportunities and CSV export;
9. account/billing shell;
10. paid-release hardening.

## 19. Definition of build-ready

The product-definition phase is complete when this document, aligned README and build gates are merged with green CI.

After that point:

- do not add another product-feasibility test before starting the web application;
- do not reopen Portugal/Italy/Poland funded-project discovery for the MVP;
- do not reinterpret Phase 0B or Phase 0C as PASS;
- implementation findings may refine UX and engineering details, but not silently broaden customer claims beyond this contract.

## 20. Final decision

**BUILD.**

ProcRun's first sellable form is not "complete tender decomposition" and not "pre-tender runway".

It is a focused supplier-side infrastructure procurement intelligence product that combines a validated active TED infrastructure feed, structured procurement data, bounded evidence-backed demand enrichment, supplier relevance and historical market context.

That is the product the web application should now implement.