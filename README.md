**Ingen del av dette produktet, verken i nåværende eller planlagt tilstand, krever eller tillater
utgående kontakt med noe menneske, organ, kilde-eier eller myndighet — verken nå eller som en
fremtidig oppgave. Dette er ikke en midlertidig begrensning som venter på unntak. Det er en permanent
byggeforutsetning.**

Alt som er godkjent i dag er godkjent utelukkende fra offentlig publiserte dokumenter, lisenssider og tekniske spesifikasjoner — aldri fra et svar, en bekreftelse, en tillatelse eller en vurdering innhentet fra et menneske. Der denne standarden ikke kunne innfris, er kilden formelt lukket eller avvist — ikke satt på vent.

Hvis en fremtidig kildevurdering lander på at menneskelig kontakt er eneste vei til godkjenning, er konklusjonen **avvis kilden**, aldri å sende en henvendelse.

# ProcRun

ProcRun is an evidence-first infrastructure procurement product for suppliers.

## Canonical decision

**Status: WEB BUILD ACTIVE. TED-SCOPED LIVE PROCUREMENT CLASSIFICATION APPROVED. OPENCOESIONE 2021-2027 EXACT OPERATION-LIST SOURCE CONTRACT APPROVED; COLLECTOR/LIVE ACCEPTANCE IS CODE-GATED.**

Canonical specification: [`docs/PRODUCT_FOUNDATION_FINAL.md`](docs/PRODUCT_FOUNDATION_FINAL.md).
Authoritative build/release decision: [`docs/BUILD_GATES.md`](docs/BUILD_GATES.md), gate **A20**.

## Approved sources

- **TED Search API:** APPROVED from public API documentation, server-side field projection, legal notice and Commission Decision 2011/833/EU.
- **OpenCoesione 2021-2027 operation-list ZIP/CSV:** APPROVED for the exact bounded operation-list publication from public OpenCoesione/RGS documentation and CC BY 4.0 terms. The broad OpenCoesione API and project/entity surfaces are not approved.
- **Portugal PRR / Mais Transparência / PT2030 / Portal BASE current routes:** Category B / PERMANENTLY BLOCKED for intelligence ingestion.
- **Poland public EU-funds project surfaces reviewed:** Category B / REJECTED.

No approved source has any future human-contact dependency. Remaining activation work is code, schema validation, drift detection, source-transfer/live acceptance and CI.

## MVP coverage contract

TED Search API is APPROVED for field-bounded procurement evidence, market context and the MVP negative-search boundary.

For the MVP, `OPEN` means exactly:

> **No relevant procurement found in TED as of DATE.**

This is not a guarantee that no procurement exists outside TED, including purely national or below-threshold procedures. Every customer-facing OPEN state must preserve that scope.

Phase 0B/0C remain FAIL for the retired TED-only demand-extraction hypothesis; those failures are not rewritten.

## Permanent validation constraint

Only already-public, independently inspectable evidence and machine-verifiable behaviour may close a source gate. Silence is never permission. ProcRun never uses `download then filter` as a privacy mechanism. Human-dependent approval is not a fallback path.

## Funded-project expansion

The long-term mechanism remains:

`approved funded project -> source-evidenced purchasable components -> indexed procurement evidence -> conservative component state -> project aggregate state -> remaining procurement runway`

OpenCoesione is the approved Category A funded-project source contract for the exact 2021-2027 operation-list route. Its collector is fail-closed and must pass source-transfer/live acceptance before customer-facing Italian funded-project data is represented as live.

## Current engineering instruction

**CONTINUE THE WEB BUILD AND COMPLETE OPENCOESIONE LIVE ACCEPTANCE.**

The Next.js application shell lives under `web/` and consumes only the customer-safe fixture/read-model adapter. TED-scoped OPEN wording is frozen in Python (`procrun.coverage`) and in the web read model. Raw collector responses are not browser/API inputs.

Checkout remains subject to A19 and green CI. No customer-facing text may imply complete Portuguese procurement coverage.