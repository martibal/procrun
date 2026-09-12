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
neste vei til godkjenning, er konklusjonen **avvis kilden**, ikke **send en henvendelse**.

## Permanent public-source reuse rule

**Offentlig tilgjengelig er ikke i seg selv tilstrekkelig. Den konkrete kommersielle bruken ProcRun gjør
av en produksjonskilde skal alltid kunne begrunnes utelukkende fra offentlig, uavhengig inspiserbart
regelverk, lisens-/vilkårssider eller offisiell kildemetadata. Individuell tillatelse, ekstern juridisk
godkjenning eller annen menneskelig vurdering er aldri en produksjonsavhengighet eller fallback.**

Hvis kommersiell republisering ikke kan dokumenteres offentlig, skal ProcRun enten begrense bruken til
strukturerte fakta/metadata, kildehenvisning og offisiell lenke uten å republisere beskyttet uttrykksform,
eller avvise kilden. Stillhet og uklarhet er aldri tillatelse.

Canonical governance: `docs/SOURCE_REUSE_GOVERNANCE.md`.
Readiness source packages enforce this through `COMMERCIAL_REUSE_CONFIRMED`,
`FACT_EXTRACTION_ONLY` and `BLOCKED`; reuse state and public basis are hash-bound into each immutable
source-package manifest.

# ProcRun

ProcRun is an evidence-first infrastructure procurement product for suppliers.

## Canonical decision

**Status: WEB PRODUCT BUILD: GO. CLASSIFICATION ENGINE PRODUCT VALIDATION: NOT YET GREEN.**

Canonical specification: `docs/PRODUCT_FOUNDATION_FINAL.md`.
Authoritative build/release decisions: `docs/BUILD_GATES.md`, gates A20 and A21.
Classification-engine release gate: `docs/CLASSIFICATION_ENGINE_VALIDATION_GATE.md`.
Frozen pre-web baseline: `docs/PREWEB_RELEASE_BASELINE.md`.
Sequencing rule: `docs/DELIVERY_READINESS_GATE.md`.

A20 authorizes the web build and records operational source/delivery readiness. A21 separately governs
whether the final classification engine has been empirically validated as the paid core product. Green
unit tests or successful production ingestion do not substitute for A21.

## Permanent sequencing rule

Web implementation is authorized because the complete non-web delivery chain has passed production
acceptance. This authorization does not itself close empirical classification validation.

The existing fixture/shell under `web/` is non-authoritative and may be replaced. It does not constrain
the visual implementation, but the frozen customer-safe data, source, coverage, privacy and evidence
contracts do constrain it.

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

## Classification-engine product validation

The implementation exists and is fail-closed, but the paid-core classification engine is not declared
empirically product-validated until A21 passes the frozen real-project benchmark. A21 requires an
independent gold standard, a general holdout, complete adjudication of the release-candidate OPEN
population, zero observed false OPEN, strict CLOSED/matching/cutoff/coverage thresholds, adversarial
testing and deterministic regression proof.

Until then the only valid engine-level product-validation status is:

**CLASSIFICATION ENGINE PRODUCT VALIDATION: NOT YET GREEN.**

## Current engineering instruction

Classification-engine validation work must follow `docs/CLASSIFICATION_ENGINE_VALIDATION_GATE.md`.
The benchmark/gold-standard package must be frozen before release-candidate scoring and must not be
silently weakened under launch pressure.
