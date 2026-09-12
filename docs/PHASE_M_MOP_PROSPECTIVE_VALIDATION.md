# Phase M — OpenBDAP MOP prospective validation

## Status

Prospective validation is conditionally approved after the safe runway measurement. Historical backtesting remains blocked because no qualifying immutable historical MOP row-state snapshot has been evidenced.

## Permanent constraints

**Ingen del av dette produktet, verken i nåværende eller planlagt tilstand, krever eller tillater
utgående kontakt med noe menneske, organ, kilde-eier eller myndighet — verken nå eller som en
fremtidig oppgave. Dette er ikke en midlertidig begrensning som venter på unntak. Det er en permanent
byggeforutsetning.**

**“Datasikkerheten følger ikke av at kilden er offentlig, den følger av hva vi faktisk lar systemet motta.”**

No identity fields or free text may be received in the MOP cohort freeze.

## Frozen source state

- OpenBDAP MOP resource: `bda1676b-62ab-44b7-8f9a-ca93b8534488@rgs`
- Source observation date: `2026-08-31`
- Safe runway measurement: 35,852 filtered rows; 34,988 unique CUPs; 339 CUPs with conflicting valid planned-start dates.
- Canonical planned-start rule: earliest valid planned execution start per CUP.
- 12-month prospective cohort count expected before freeze: 1,356 unique CUPs.

The freeze must fail closed if any of these control counts drift before snapshot creation.

## Cohort eligibility — frozen before outcome inspection

A CUP is eligible when, at the source observation date:

1. project status is `A`;
2. actual execution start is blank or the frozen sentinel `9999-12-31`;
3. planned execution start is within the valid interval `2000-01-01` through `2100-12-31`;
4. after deduplication by CUP, the earliest valid planned execution start is between `2026-08-31` and `2027-08-31`, inclusive.

Only CUP and planned execution start may be received. The frozen cohort file is canonical JSON Lines sorted by CUP. Its SHA-256 and a separate protocol SHA-256 are written to the manifest.

## Prospective outcome — preregistered

Primary future outcome: TED-observed procurement materialization linked to the frozen CUP.

A TED observation is evidence that procurement materialized in TED. No TED observation is **not** evidence that no procurement occurred; TED linkage is therefore a lower-bound outcome measure.

No TED outcome inspection is permitted until the TED Search API projection has separately passed RIGHTS, ACCESS and DATA SAFETY qualification with a server-side allowlist that excludes organisations, contact points, buyer/contact-person identity and other identity-bearing sections.

## Primary commercial measures

For each future TED-observed materialization, measure:

- materialization rate among the frozen CUP cohort;
- lead time from snapshot observation date to first qualifying TED observation;
- lead time from first qualifying TED observation relative to the canonical planned execution start;
- distribution of lead time, including median and lower quartile;
- cohort attrition or lifecycle drift separately from TED outcome.

The commercial question is not merely whether CUPs eventually match TED. The test is whether MOP creates enough **usable advance notice** to justify a product advantage over ordinary tender visibility.

## Interpretation gate

- High materialization + meaningful lead time: evidence for MOP as a core early-opportunity source.
- High materialization + little lead time: MOP is enrichment, not early discovery.
- Low materialization + meaningful lead time: preregister one narrowing test before any additional outcome inspection; failure is NO-GO for MOP as core.
- Low materialization + little lead time: NO-GO for MOP as core.

No threshold may be retrofitted after outcome inspection. Any quantitative threshold added later must be committed and hash-frozen before the corresponding outcome data are inspected.
