# ProcRun

ProcRun is a private, evidence-first procurement-intelligence product for suppliers to public infrastructure projects.

The locked v2 product definition is:

> **ProcRun turns public procurement notices into supplier-specific product demand.**

The customer does not receive a generic tender search result. ProcRun identifies the purchasable products, systems and specialist requirements inside active public infrastructure procurements, matches those requirements to what a supplier sells, and shows the result with dated source evidence.

Canonical product pipeline:

`TED notice -> procurement opportunity -> purchasable requirements -> supplier relevance -> evidence -> customer feed`

The canonical product and website specification is [`docs/PRODUCT_FOUNDATION_V2.md`](docs/PRODUCT_FOUNDATION_V2.md). It supersedes the original funded-project-first product promise wherever older documents conflict with it.

---

## Product position

ProcRun is not positioned as "better tender alerts".

The locked differentiation is:

> **Tender platforms tell you which contracts may be relevant. ProcRun tells you what those contracts actually create demand for.**

The primary customer is a manufacturer, OEM, distributor, technical wholesaler, systems supplier or specialist subcontractor whose commercial opportunity may sit inside a larger public contract even when the company is not the prime bidder.

Launch market: **Portugal**.

Initial infrastructure domains include water/wastewater, transport/rail, ports/coastal, energy/electrical infrastructure and efficiency, resilience/fire and adjacent supported infrastructure categories.

---

## Validated product foundation

The production source foundation is the **TED Search API**.

The final live capability inventory in CI #161 validated, for the tested preceding 12 months in Portugal:

- 18,776 notices;
- 4,893 infrastructure notices;
- 3,812 later/active-stage infrastructure notices;
- 58 early infrastructure notices;
- 100.0% title + description population for the early and later infrastructure slices;
- 98.2% procedure-identifier population overall;
- 71.9% estimated-value/currency population;
- 77.3% place-of-performance subdivision population;
- all retained qualification fields projectable through the approved field-bounded TED transport.

Product-hypothesis result:

| Hypothesis | Result |
| --- | --- |
| Active infrastructure opportunity feed | **SUPPORTED** |
| Procurement market intelligence | **SUPPORTED** |
| Early procurement runway | NOT SUPPORTED |
| Comprehensive EU-funding subset | NOT SUPPORTED |

Therefore ProcRun must not be marketed as a comprehensive EU-funded-project feed or as a reliably months-before-tender early-warning service on the present evidence.

Known Portugal funded-project discovery source families are closed by default and are no longer a dependency for the v2 product.

---

## MVP customer product

The website MVP contains:

- supplier-profile onboarding;
- ranked opportunity feed;
- opportunity detail with matched purchasable requirements;
- exact evidence/source presentation;
- relevance bands and reasons;
- filters by date, category, region, stage, CPV and available value;
- saved opportunities;
- procurement market-intelligence dashboard;
- customer-safe CSV export;
- account/billing shell.

The launch package is specified for implementation as **ProcRun Portugal — €149/month**, one supplier profile/workspace. Checkout remains disabled until the customer-control-plane release gates are complete.

No permanent free tier is part of the MVP. Demo/sample mode uses synthetic or explicitly approved publishable examples.

---

## What ProcRun is not

ProcRun MVP is not:

- a bid-writing tool;
- a CRM;
- a contact-person database;
- a supplier/winner database;
- a procurement submission portal;
- a win-probability model;
- an unrestricted TED browser;
- a comprehensive EU-funded-project database;
- a reliable pre-tender runway product.

---

## Absolute intelligence-data boundary

No natural-person data may be collected, stored or processed in the ProcRun intelligence plane.

This is a **pre-receipt** requirement. Receiving a broad response and deleting prohibited fields afterwards is not permitted.

Production collectors must pass the source contract before retrieval. Every source requires independent approval for:

1. RIGHTS — commercial/derivative reuse;
2. ACCESS — automated use through the exact route;
3. DATA SAFETY — prohibited fields excluded before receipt.

TED is used through explicit server-side field projection. Unexpected response fields fail closed. Raw response bodies are not stored for website use.

Account, billing and support information belong to a separate control plane and may not enter the analytical ledger/model context.

See [`docs/SOURCE_STATUS.md`](docs/SOURCE_STATUS.md), [`docs/COMPLIANCE.md`](docs/COMPLIANCE.md) and [`docs/BUILD_GATES.md`](docs/BUILD_GATES.md).

---

## Core technical assets

The repository already contains the core data-plane foundation, including:

- TED collector/source contract;
- deterministic component/requirement engine;
- exact evidence-span handling;
- local-model fallback boundary;
- procurement matching logic from the original research path;
- PostgreSQL 16 append-only/versioned evidence ledger;
- source/compliance registry;
- CI safety and regression controls.

Legacy funded-project OPEN/CLOSED/PARTIAL code and research evidence remain useful historical/regression assets but do not define the v2 customer-facing ontology.

The customer-facing ontology is:

`Opportunity -> Purchasable requirements -> Supplier match -> Relevance -> Evidence`

---

## Website build readiness

**Status: READY FOR WEBSITE BUILD.**

No additional source discovery, country-source research, market-size research or product-definition work is required before website implementation starts.

Implementation order:

1. web application shell + design system;
2. customer-safe opportunity read model/API;
3. landing/product/methodology/pricing pages;
4. supplier-profile onboarding;
5. opportunity feed;
6. opportunity detail + evidence view;
7. market-intelligence dashboard;
8. saved opportunities;
9. account/billing shell;
10. paid-release hardening.

The detailed field contracts, copy contract, routes, feed defaults, relevance semantics, onboarding and pricing are frozen in [`docs/PRODUCT_FOUNDATION_V2.md`](docs/PRODUCT_FOUNDATION_V2.md).

---

## Paid-release gate

Building the website may proceed immediately, but paid customer release remains gated on:

- final legal entity/merchant identity;
- Terms of Service;
- Privacy Notice;
- VAT/invoicing flow;
- payment-provider activation/approval;
- processor/subprocessor inventory and required DPAs;
- customer/control-plane separation verification;
- TLS, secrets, least privilege, backups and restore verification;
- then-current source attribution/rights review;
- short external legal review before paid launch.

These are release gates, not blockers for building the product.