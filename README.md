# ProcRun

ProcRun is a private, evidence-first infrastructure procurement intelligence product for suppliers.

## Final product decision

**Status: READY FOR WEBSITE BUILD.**

Canonical product specification: [`docs/PRODUCT_FOUNDATION_FINAL.md`](docs/PRODUCT_FOUNDATION_FINAL.md).

ProcRun will be built as a focused supplier-side view of Portugal public-infrastructure procurement.

The locked customer promise is:

> **ProcRun turns public infrastructure procurement into a focused supplier intelligence feed: active opportunities, evidence-backed demand tags where they can be proven, and market context from the same procurement universe.**

Primary sales line:

> **From tenders to infrastructure demand.**

Canonical pipeline:

`TED notice -> infrastructure opportunity -> structured procurement fields -> evidence-backed demand tags where present -> supplier relevance -> market context -> customer feed`

## What is validated

The production-safe source foundation is the TED Search API.

Validated source capabilities include:

| Capability | Result |
| --- | --- |
| Active infrastructure notice feed | SUPPORTED |
| Procurement market-intelligence dataset | SUPPORTED |
| Early procurement runway from TED | NOT SUPPORTED |
| Comprehensive EU-funding subset | NOT SUPPORTED |

The final TED capability inventory established a substantial Portugal infrastructure universe and approved server-side field projection under ProcRun's absolute pre-receipt privacy boundary.

## What Phase 0B and 0C established

The failed tests are preserved and are not relabelled as PASS.

Phase 0B, 300 notices:

- any requirement: 26.0%;
- description-only value: 2.7% — FAIL against the frozen v2 gate;
- CPV-blind value: 20.7%;
- distinct categories: 20;
- domains represented: 5.

Phase 0C, disjoint 300-notice period:

- any normalized requirement: 20.3%;
- CPV-blind value: 18.7%;
- distinct categories: 13 — FAIL against the frozen 15-category gate;
- domains represented: 5.

Therefore ProcRun does **not** sell complete component decomposition, hidden-demand discovery or guaranteed requirement coverage.

The reproducible text/CPV signal is used only as a bounded enrichment: evidence-backed product/system demand tags are shown where source text proves them. Notices without tags remain valid opportunities.

See:

- [`docs/PHASE0B_TED_DEMAND_RESULT.md`](docs/PHASE0B_TED_DEMAND_RESULT.md)
- [`docs/PHASE0C_CPV_NORMALIZATION_RESULT.md`](docs/PHASE0C_CPV_NORMALIZATION_RESULT.md)

## Differentiation

ProcRun is not another general tender inbox.

It is deliberately built for manufacturers, OEMs, distributors, technical wholesalers, systems suppliers and specialist subcontractors selling into infrastructure projects, including firms that may never bid for the prime public contract themselves.

The product combines:

- infrastructure-only opportunity monitoring;
- supplier-profile relevance;
- evidence-backed product/system demand tags where present;
- exact evidence/provenance;
- historical infrastructure procurement market intelligence from the same approved data universe.

The product does not claim that no competitor can perform any individual function. The differentiation is the narrow infrastructure-supplier workflow and the combination above.

## MVP

The first web application includes:

- landing/product/methodology/pricing pages;
- supplier-profile onboarding;
- active opportunity feed;
- filters by supported domain, demand tag, CPV, region, value, stage and date;
- opportunity detail with evidence;
- market-intelligence dashboard;
- saved opportunities;
- customer-safe CSV export;
- account/billing shell.

Launch package:

> **ProcRun Portugal — €149/month**

No permanent free tier. Checkout remains disabled until paid-release legal/security/control-plane gates are complete.

## Absolute intelligence-data boundary

No natural-person data may be collected, stored or processed in the ProcRun intelligence plane.

This is a **pre-receipt** requirement. Receiving a broad response and deleting prohibited fields afterwards is not permitted.

Account, authentication, billing and support information belong to a separate control plane and may not enter the analytical ledger/model context.

See [`docs/SOURCE_STATUS.md`](docs/SOURCE_STATUS.md), [`docs/COMPLIANCE.md`](docs/COMPLIANCE.md) and [`docs/BUILD_GATES.md`](docs/BUILD_GATES.md).

## Build instruction

**BUILD.**

Do not add another product-feasibility test before starting the web application. Do not reopen funded-project source discovery for the MVP. Do not broaden website claims beyond `PRODUCT_FOUNDATION_FINAL.md` without new evidence.

Implementation starts with the web shell and customer-safe opportunity read model/API.