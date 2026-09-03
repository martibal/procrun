# PRR Projects — A1 source-owner clarification request

Status: **OPEN EXTERNAL DEPENDENCY**
Date: 2026-09-03

## Why this request exists

ProcRun has an absolute intelligence-plane rule: no natural-person data may be received, stored or processed. Filtering after download is not permitted. The funded-project source therefore cannot be activated from portal-level assumptions or sample inspection.

The preferred candidate is `Dataset Estrutura de Missão PRR - Projetos`, published by Estrutura de Missão Recuperar Portugal through dados.gov.pt.

Public evidence already supports that:

- the dataset is an official PRR project dataset and is maintained on an ongoing basis;
- dados.gov.pt provides machine-readable access infrastructure and State-data reuse terms;
- dados.gov.pt publication guidance requires anonymised/publication-safe data;
- PRR Projects is separated from PRR Entities in the catalogue.

However, dados.gov.pt terms also contemplate legally permitted publication of personal data. Portal-level policy therefore cannot by itself prove ProcRun's stronger source-specific invariant for every retained free-text field.

## Exact clarification required from the source owner

A1 can turn green only after an authoritative response answers all questions below for the **Projects** dataset specifically.

1. What is the stable machine-readable distribution/API route intended for automated reuse of `Dataset Estrutura de Missão PRR - Projetos`?
2. Is the output schema for that route documented or otherwise stable/versioned?
3. Before publication, is the Projects distribution guaranteed not to contain data identifying a natural person in any field ProcRun would retain?
4. Does that guarantee explicitly include free-text project fields such as project title/name and project description/scope/summary, not only structured identifiers?
5. Can the source owner confirm that the following intended analytical surface is safe under that guarantee: project code/identifier, project title, project scope/description, project dates, approved funding/value, programme/component/investment classification, and non-person geographic fields?
6. If any of those fields can contain natural-person data under any valid publication scenario, is there a documented server-side projection or separate Projects distribution that excludes such fields before transmission?
7. Please confirm the reuse licence applicable to this exact Projects dataset/distribution for commercial value-added reuse, because the catalogue currently displays the dataset licence as unspecified.

## Approval rule

A response is sufficient only if it establishes the exact route + rights + pre-receipt data-safety boundary. Statements such as "normally contains no personal data", sample inspection, or a recommendation to download and filter locally are insufficient.

On sufficient confirmation, one reviewed change must:

- freeze the exact route;
- freeze the exact schema and retained allowlist;
- record the authoritative response/citation;
- update `src/procrun/source_contracts.py` from CONDITIONAL to APPROVED;
- implement the fail-closed collector;
- add schema-drift and prohibited-field regression tests;
- update `SOURCE_STATUS.md` and A1/A20;
- pass CI before web work begins.

## Intended recipient

Estrutura de Missão Recuperar Portugal — official general contact published by the source owner.

The request should be sent without attaching or transmitting any dataset rows.
