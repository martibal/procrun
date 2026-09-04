# ProcRun

ProcRun is an evidence-first infrastructure procurement runway product for suppliers.

## Canonical decision

**Status: WEB BUILD APPROVED. LIVE FUNDED-PROJECT INGEST AND NATIONAL OPEN CLASSIFICATION REMAIN FAIL-CLOSED UNTIL THEIR PUBLIC-EVIDENCE SOURCE CONTRACTS PASS.**

Canonical specification: [`docs/PRODUCT_FOUNDATION_FINAL.md`](docs/PRODUCT_FOUNDATION_FINAL.md).
Authoritative build/release decision: [`docs/BUILD_GATES.md`](docs/BUILD_GATES.md), gate **A20**.

The canonical mechanism is funded-project first:

`approved funded project -> source-evidenced purchasable components -> indexed procurement evidence -> conservative component state -> project aggregate state -> remaining procurement runway`

TED remains an approved procurement-evidence and market-context source. The TED-only v2 pivot is retired as the primary product mechanism; its Phase 0B/0C failures remain preserved and must never be relabelled as PASS.

## Product contract

Primary promise:

> **See what an approved infrastructure project is expected to buy, what ProcRun can prove has already entered procurement, and what remains without a verified procurement match as of the stated date.**

Trust promise:

> **No invented demand. Every positive component and procurement match is tied to exact source evidence. Ambiguity abstains.**

`OPEN` is never treated as a source fact. It means only that no relevant procurement was found in every required approved source as of the stated cutoff.

## Non-negotiable validation constraint

ProcRun is developed and validated without interviews, surveys, outreach, requests for clarification, authority/source-owner contact, customer contact, paid expert/legal consultation, or any other human-dependent approval path.

Only already-public, independently inspectable evidence and machine-verifiable behaviour may close a product/data gate. Silence is never permission.

## Source status

- **TED Search API:** APPROVED for field-bounded procurement evidence and market context.
- **PRR Projects / dados.gov.pt:** CONDITIONAL. Current public evidence does not close exact-route rights plus pre-receipt free-text safety; no human clarification may be requested.
- **Portuguese national procurement coverage:** still requires an approved pre-receipt-safe, complete-enough public source before original national `OPEN` can be trusted.
- **OpenCoesione:** useful public evidence establishes CC BY 4.0 reuse, machine access, natural-person beneficiary anonymisation in the monitored operation-list contract, and a no-natural-person-name rule for operation titles; it does not yet supply a public zero-person guarantee for every free-text field required by the full ProcRun extraction route.
- Broad PT2030/beneficiary/BASE routes remain blocked unless an exact safe public route is independently approved.

ProcRun never uses `download then filter` as a privacy mechanism.

## Existing engineering

The component engine, matching hierarchy, exact-evidence provenance, append-only ledger, canonical runway orchestration and customer-safe read model are implemented and regression-tested.

See:

- [`docs/COMPONENT_ENGINE.md`](docs/COMPONENT_ENGINE.md)
- [`docs/MATCHING_RULES.md`](docs/MATCHING_RULES.md)
- [`docs/LOCAL_MODEL_CONTRACT.md`](docs/LOCAL_MODEL_CONTRACT.md)
- [`docs/LEDGER.md`](docs/LEDGER.md)
- [`docs/PREWEB_SHOWSTOPPER_STATUS.md`](docs/PREWEB_SHOWSTOPPER_STATUS.md)

## Current engineering instruction

**START THE WEB BUILD.**

Web implementation is now explicitly decoupled from live-source activation. Build only against fixtures and the frozen customer-safe read model until production sources are approved. No raw or conditional source may be connected to the browser-facing path merely to make the UI look live.

The remaining source work continues in parallel and remains release-blocking:

1. qualify one funded-project source entirely from public evidence;
2. qualify one complete-enough Portuguese national procurement source entirely from public evidence;
3. run the required source-transfer/live acceptance validation;
4. require green CI and A19 before paid production.

Do not re-pivot to a TED-only supplier-demand feed, do not weaken Phase 0B/0C results, and do not weaken the zero-PII or no-contact boundaries to obtain a source.
