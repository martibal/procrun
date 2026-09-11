# Phase R — structured coverage expansion

## Status

Phase R Tasks A–D established that the current coverage ceiling is structural rather than lexical.
The frozen 4,305-project corpus has 133 projects with an approved structured signal; after Task C
all 133 are classified under the Phase R confidence contract, and Task D cannot increase total
coverage without widening that structured-signal pool.

This phase therefore starts with a **diagnostic only**. It does not change classification semantics,
add source routes, widen privacy scope, or relax evidence requirements.

## Diagnostic objective

Measure, on the exact frozen OpenCoesione source snapshot, how much safe structured information is
already present in the two admitted publisher fields:

- `ObiettivoSpecifico_SpecificObjective` / `FundingProject.objective`
- `CategoriaOperazione_CategoryIntervention` / `FundingProject.theme`

The report must establish:

1. population and distinct-value coverage of both fields;
2. detected RSO/ISO objective codes and their project counts;
3. exact intervention-category values and any machine-readable code patterns;
4. how many projects the current mapping reaches through each source and domain;
5. whether the current intervention-category parser is failing because codes are absent, encoded in
   a different form, or simply outside the current map.

## Privacy and source boundary

Only fields already admitted by the frozen OpenCoesione collector may be read. The diagnostic emits
aggregate counts and classification values only; it emits no beneficiary data, project identifiers,
project titles, project summaries, or other row-level material. The source hash and 4,305-project
count must reproduce before measurement proceeds.

No human contact, registration, live row probing of a new source, or download-then-filter privacy
mechanism is introduced.

## Decision rule after measurement

The next implementation is selected from measured evidence, not intuition:

- If the existing `intervention_category` field contains usable structured codes/values at scale,
  expand the frozen deterministic mapping from official EU definitions and measure isolated uplift.
- If `specific_objective` contains additional objectives that unambiguously map to an existing
  ProcRun domain, add only those narrow mappings and measure isolated uplift.
- Broad objectives that span multiple ProcRun domains remain ineligible by objective alone.
- If the admitted fields cannot provide material additional coverage, qualify the next public
  structured source under RIGHTS / ACCESS / DATA SAFETY before receiving row data.

The 40% Phase R target remains unchanged and is a minimum gate, not a desired final uncertainty
rate.
