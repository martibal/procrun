# ProcRun

ProcRun is an evidence-first infrastructure procurement product for suppliers.

## Canonical decision

**Status: WEB BUILD APPROVED. TED-SCOPED LIVE PROCUREMENT CLASSIFICATION APPROVED. LIVE FUNDED-PROJECT INGEST REMAINS FAIL-CLOSED UNTIL A CATEGORY-A SOURCE PASSES A1.**

Canonical specification: [`docs/PRODUCT_FOUNDATION_FINAL.md`](docs/PRODUCT_FOUNDATION_FINAL.md).
Authoritative build/release decision: [`docs/BUILD_GATES.md`](docs/BUILD_GATES.md), gate **A20**.

## MVP coverage contract

TED Search API is APPROVED for field-bounded procurement evidence, market context and the MVP negative-search boundary.

For the MVP, `OPEN` means exactly:

> **No relevant procurement found in TED as of DATE.**

This is not a guarantee that no procurement exists outside TED, including purely national or below-threshold Portuguese procedures. Every customer-facing OPEN state must preserve that scope.

Phase 0B/0C remain FAIL for the retired TED-only demand-extraction hypothesis; those failures are not rewritten.

## Non-negotiable validation constraint

ProcRun is developed and validated without interviews, surveys, outreach, requests for clarification, authority/source-owner contact, customer contact, paid expert/legal consultation, or any other human-dependent approval path.

Only already-public, independently inspectable evidence and machine-verifiable behaviour may close a source gate. Silence is never permission. ProcRun never uses `download then filter` as a privacy mechanism.

## Funded-project expansion

The long-term mechanism remains:

`approved funded project -> source-evidenced purchasable components -> indexed procurement evidence -> conservative component state -> project aggregate state -> remaining procurement runway`

PRR Projects and Mais Transparência are now Category B and permanently closed to the intelligence plane under current rules; they are not waiting for clarification.

OpenCoesione is the leading Category A replacement candidate. Official monitoring documentation constrains project title and summary against sensitive natural-person information, but the exact machine route still requires A1/source-transfer qualification before live ingest.

## Current engineering instruction

**START THE WEB BUILD AND TED-SCOPED MVP IMPLEMENTATION.**

Build the web shell against the frozen customer-safe read model. TED ingest/evidence, market context, saved opportunities and customer-safe CSV export may use the approved TED contract. Funded-project screens remain fixtures only and must be clearly non-live until A1 passes.

Checkout remains subject to A19 and green CI. No customer-facing text may imply complete Portuguese procurement coverage.