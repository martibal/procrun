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

**Status: WEB PRODUCT BUILD: GO. CORE PRODUCT DELIVERY AND PRE-WEB RELEASE HOUSEKEEPING ARE GREEN.**

Canonical specification: `docs/PRODUCT_FOUNDATION_FINAL.md`.
Authoritative build/release decision: `docs/BUILD_GATES.md`, gate A20.
Frozen pre-web baseline: `docs/PREWEB_RELEASE_BASELINE.md`.
Sequencing rule: `docs/DELIVERY_READINESS_GATE.md`.
Normative customer-data/commercialization contract: `docs/CUSTOMER_DATA_AND_COMMERCIALIZATION_CONTRACT.md`.
Authoritative web-phase requirements: `docs/WEB_CUSTOMER_APPLICATION_SPEC.md`.

The customer-data/commercialization contract is mandatory for all customer-facing code, exports, APIs, demos, samples, marketing, pricing, Terms/Privacy copy and source links. Public availability of upstream data does not widen ProcRun's approved source or customer-safe boundary, and customer payment is for the approved ProcRun service layer rather than exclusive access to underlying public source data.

The web-phase specification governs the customer application, navigation, demo, onboarding, opportunity surfaces, launch controls and acceptance criteria. It is subordinate to `docs/BUILD_GATES.md` and `docs/CUSTOMER_DATA_AND_COMMERCIALIZATION_CONTRACT.md` on source, privacy, rights, attribution and customer-safe data boundaries.

## Permanent sequencing rule

Web implementation is the final product-development phase. That phase is now authorized because the complete non-web intelligence delivery chain has passed production acceptance.

The existing fixture/shell under `web/` is non-authoritative and may be replaced. It does not constrain the visual implementation, but the frozen customer-safe data, source, coverage, privacy, evidence and commercialization contracts do constrain it.

## Approved sources

- **TED Search API:** APPROVED for field-projected procurement evidence and TED-scoped negative-search coverage.
- **OpenCoesione 2021-2027 operation-list ZIP/CSV:** APPROVED for the exact bounded publication family; the current live route is PR FESR Lombardia. The broad OpenCoesione API and project/entity surfaces are not approved.
- **Portugal PRR / Mais Transparência / PT2030 / Portal BASE current routes:** Category B / PERMANENTLY BLOCKED for intelligence ingestion.
- **Poland public EU-funds project surfaces reviewed:** Category B / REJECTED.

No approved source has any future human-contact dependency.

## MVP coverage contract

For the MVP, `OPEN` means exactly:

> **No relevant procurement found in TED as of DATE.**

This is not a guarantee that no procurement exists outside TED, including purely national or below-threshold procedures. Every customer-facing OPEN state must preserve that scope.

Phase 0B/0C remain FAIL for the retired TED-only demand-extraction hypothesis; those historical failures are not rewritten.

## Permanent validation constraint

Only already-public, independently inspectable evidence and machine-verifiable behaviour may close a source gate. Silence is never permission. ProcRun never uses `download then filter` as a privacy mechanism. Human-dependent approval is not a fallback path.

## Accepted production delivery path

`approved funded project -> source-evidenced purchasable components -> indexed procurement evidence -> conservative component state -> project aggregate state -> remaining procurement runway`

The dedicated production runtime has completed this path on live sources: 4,631 funded projects; complete Italy TED universe of 176,540 notices / 708 pages; 81 projects with components; 37 useful/resolved; 44 safely unresolved; customer-safe JSONL; PostgreSQL run manifest; verified backup/restore; active delivery/backup timers; PostgreSQL loopback-only.

The customer application may consume only `src/procrun/read_model.py` (`customer-runway-v1`) or an explicitly versioned successor approved under the same customer-safe boundary.

## Current engineering instruction

**CONTINUE WITH THE CUSTOMER-FACING WEB PRODUCT BUILD.**

The web phase includes GUI/UX, authentication/account handling, customer control-plane separation, Stripe/subscription integration if used, VAT/invoicing implementation, Terms/Privacy and merchant identity presentation, domain/TLS, customer-facing source attribution/methodology, security/access controls and final launch testing.

Those web/control-plane items are mandatory before public paid launch, but they are not pre-web blockers. No further OpenCoesione/TED production replay is required merely because documentation or web code changes.
