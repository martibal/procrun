**Ingen del av dette produktet, verken i nåværende eller planlagt tilstand, krever eller tillater
utgående kontakt med noe menneske, organ, kilde-eier eller myndighet — verken nå eller som en
fremtidig oppgave. Dette er ikke en midlertidig begrensning som venter på unntak. Det er en permanent
byggeforutsetning.**

Alt som er godkjent i dag er godkjent utelukkende fra offentlig publiserte dokumenter, lisenssider og
tekniske spesifikasjoner — aldri fra et svar, en bekreftelse, en tillatelse eller en vurdering innhentet fra
et menneske. Der denne standarden ikke kunne innfris (Portugal PRR og tilknyttede kilder), er kilden
formelt og permanent lukket — ikke satt på vent.

Ingen fremtidig oppgave i dette prosjektet skal noensinne innebære: e-post, skjema, kontaktside,
telefon, intervju, betalt konsulent-/juristvurdering rettet mot en kildeeier, eller noen annen kanal der et
menneske må svare før arbeidet kan fortsette. Hvis en fremtidig kildevurdering lander på at kontakt er
eneste vei til godkjenning, er konklusjonen **avvis kilden**, ikke **send en henvendelse**.

# ProcRun

ProcRun is an evidence-first infrastructure procurement product for suppliers.

## Canonical decision

**Status: WEB BUILD BLOCKED UNTIL FULL DELIVERY-READINESS IS GREEN. TED-SCOPED LIVE PROCUREMENT CLASSIFICATION APPROVED. OPENCOESIONE 2021-2027 EXACT OPERATION-LIST SOURCE CONTRACT APPROVED, BUT LIVE SOURCE-TRANSFER IS NOT YET GREEN.**

Canonical specification: [`docs/PRODUCT_FOUNDATION_FINAL.md`](docs/PRODUCT_FOUNDATION_FINAL.md).
Authoritative build/release decision: [`docs/BUILD_GATES.md`](docs/BUILD_GATES.md), gate **A20**.
Sequencing rule: [`docs/DELIVERY_READINESS_GATE.md`](docs/DELIVERY_READINESS_GATE.md).

## Permanent sequencing rule

**Web implementation is the final build phase. It must not start or continue until the complete non-web delivery chain is launch-ready.**

At the moment web build receives `GO`, the product must already be ready for launch except for the web interface itself. There may be no unresolved source, live-ingest, pipeline, coverage, persistence/export, operational, billing/control-plane or release-control dependency waiting behind the web build.

Any fixture-based or shell web work created before this rule was restored is non-authoritative and frozen. It does not satisfy the web-build gate and is not permission to continue web development.

## Approved sources

- **TED Search API:** APPROVED from public API documentation, server-side field projection, legal notice and Commission Decision 2011/833/EU.
- **OpenCoesione 2021-2027 operation-list ZIP/CSV:** APPROVED for the exact bounded publication from public OpenCoesione/RGS documentation and CC BY 4.0 terms. The broad OpenCoesione API and project/entity surfaces are not approved.
- **Portugal PRR / Mais Transparência / PT2030 / Portal BASE current routes:** Category B / PERMANENTLY BLOCKED for intelligence ingestion.
- **Poland public EU-funds project surfaces reviewed:** Category B / REJECTED.

No approved source has any future human-contact dependency.

## MVP coverage contract

TED Search API is APPROVED for field-bounded procurement evidence, market context and the MVP negative-search boundary.

For the MVP, `OPEN` means exactly:

> **No relevant procurement found in TED as of DATE.**

This is not a guarantee that no procurement exists outside TED, including purely national or below-threshold procedures. Every customer-facing OPEN state must preserve that scope.

Phase 0B/0C remain FAIL for the retired TED-only demand-extraction hypothesis; those failures are not rewritten.

## Permanent validation constraint

Only already-public, independently inspectable evidence and machine-verifiable behaviour may close a source gate. Silence is never permission. ProcRun never uses `download then filter` as a privacy mechanism. Human-dependent approval is not a fallback path.

## Funded-project delivery path

The canonical mechanism remains:

`approved funded project -> source-evidenced purchasable components -> indexed procurement evidence -> conservative component state -> project aggregate state -> remaining procurement runway`

OpenCoesione is the approved Category A funded-project source contract for the exact 2021-2027 operation-list publication family. The currently pinned PR FESR Lombardia route is **not live-accepted** because the current GitHub-hosted runtime receives HTTP 403 before ZIP/schema validation. This is a delivery blocker until an automated no-contact runtime successfully performs the exact same frozen-route source-transfer and the canonical live end-to-end chain passes.

## Current engineering instruction

**DO NOT CONTINUE WEB DEVELOPMENT. COMPLETE THE FULL NON-WEB DELIVERY CHAIN FIRST.**

Required before `A20 WEB BUILD` may change to GO:

1. OpenCoesione live source-transfer succeeds from an approved automated runtime without weakening the frozen route/schema/zero-PII contract;
2. funded-project canonical end-to-end processing succeeds on live data through the customer-safe read boundary;
3. TED-scoped OPEN remains enforced in production code and all relevant exports/read contracts;
4. persistence, saved/export and operational delivery paths are launch-ready;
5. billing/control-plane and A19 release controls that do not depend on final web presentation are launch-ready;
6. drift/schema/compliance/no-contact/regression/CI gates are green;
7. repo status documents agree that the only remaining launch work is the web interface.

Only after all seven conditions are green may customer-facing web implementation resume.