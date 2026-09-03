# ProcRun

ProcRun is an evidence-first infrastructure procurement runway product for suppliers.

## Canonical decision

**Status: READY FOR PRODUCT BUILD; LIVE FUNDED-PROJECT INGEST REMAINS FAIL-CLOSED UNTIL A1 IS APPROVED.**

Canonical specification: [`docs/PRODUCT_FOUNDATION_FINAL.md`](docs/PRODUCT_FOUNDATION_FINAL.md).
Authoritative build/release decision: [`docs/BUILD_GATES.md`](docs/BUILD_GATES.md), gate **A20**.

The canonical mechanism is again funded-project first:

`approved funded project -> source-evidenced purchasable components -> indexed procurement evidence -> component state -> remaining procurement runway`

TED remains an approved procurement-evidence and market-context source. The TED-only v2 pivot is retired as the primary product mechanism; its Phase 0B/0C failures remain preserved and must never be relabelled as PASS.

## Product contract

Primary promise:

> **See what an approved infrastructure project is expected to buy, what ProcRun can prove has already entered procurement, and what remains without a verified procurement match as of the stated date.**

Trust promise:

> **No invented demand. Every positive component and procurement match is tied to exact source evidence. Ambiguity abstains.**

This is deliberately different from AI-ranked tender products. ProcRun does not provide a GO/NO-GO probability, win score or generated commercial recommendation. It preserves source evidence, version, cutoff and hashes so a customer can inspect why a component exists and why a procurement record did or did not suppress it.

The phrase `100% source-verified` may be used only for positive evidence objects that actually satisfy the evidence contract. It must never imply that an `OPEN` state is a source fact. `OPEN` means only: **No relevant procurement found in approved indexed sources as of DATE, with required source coverage complete.**

## Differentiation

ProcRun's defensible combination is:

- **funded-project-to-procurement gap**, rather than another tender inbox;
- **supplier/component view**, including suppliers that may never bid for the prime contract;
- **exact source evidence** for every accepted component and procurement match;
- **conservative abstention**: ambiguity becomes `UNRESOLVED`, never a manufactured lead;
- **historical reproducibility** through append-only evidence, model/rule versions and SHA-256-linked classifications;
- **Portugal infrastructure focus** so evidence standards are not traded away for breadth.

Competitor breadth is not treated as a defect. ProcRun competes on a different customer contract: narrower scope, explicit evidence, remaining-runway state and reproducibility.

## Source status

- **TED Search API:** APPROVED for field-bounded procurement evidence and market context.
- **PRR Projects / dados.gov.pt:** promising official funded-project source, but **not yet APPROVED for live intelligence ingestion** under ProcRun's stricter zero-natural-person pre-receipt rule. The portal's publication policy and default CC BY 4.0 basis are strong evidence, but the exact machine route/free-text boundary still lacks a source-specific guarantee sufficient for A1.
- Broad PT2030/beneficiary/BASE routes remain blocked unless an exact safe route is independently approved.

ProcRun never uses `download then filter` as a privacy mechanism.

## Existing engineering that is canonical again

The component engine, local-model contract, matching hierarchy and immutable ledger were built for the funded-project-first mechanism and are now first-class production architecture again. They are not evidence for the failed TED-only v2 hypothesis; they serve the restored runway mechanism.

See:

- [`docs/COMPONENT_ENGINE.md`](docs/COMPONENT_ENGINE.md)
- [`docs/MATCHING_RULES.md`](docs/MATCHING_RULES.md)
- [`docs/LOCAL_MODEL_CONTRACT.md`](docs/LOCAL_MODEL_CONTRACT.md)
- [`docs/LEDGER.md`](docs/LEDGER.md)
- [`docs/MODEL_BENCHMARK.md`](docs/MODEL_BENCHMARK.md)

## Build instruction

**BUILD the application and production-safe interfaces now.**

Do not re-pivot to a TED-only supplier-demand feed, do not weaken Phase 0B/0C results, and do not weaken the zero-PII boundary to activate a funded-project source. The live runway collector remains disabled until A1 is green; everything downstream must be built against the frozen source contract and fixtures so source activation is a controlled switch, not another product redesign.
