# Phase R — candidate promotion closure

Status: **CLOSED — NO PRODUCTION PROMOTION AUTHORIZED**

Reviewed: 2026-09-12

## Decision

The Phase R candidate-domain expansion path is closed for production under the current evidence-bounded source and matching contract.

No new `ComponentDomain`, intervention-code mapping, CPV production rule, OPEN/CLOSED rule, read-model field or customer-output behavior is authorized by the completed Phase R diagnostics.

## What was established

### Structured source availability

The qualified Lombardia Socrata route provides safe structured intervention data for 4,178 of the frozen 4,305 OpenCoesione projects, a structured-data ceiling of 97.0499%.

This is source-data availability only. It is **not** ProcRun classified coverage.

### Existing production taxonomy

The current five-domain production taxonomy safely maps 142 of 4,305 frozen projects = 3.2985%.

The only observed intervention codes admitted by the frozen production mapping remain `040`, `042`, `044` and `045`, all mapped to `energy_efficiency`.

### Candidate domains

Two additional domains passed the public-definition and deterministic cohort-design gates:

- `digital_transformation`: intervention code `013` + action `1.2.3`, 573 projects;
- `waste_circular_economy`: intervention code `067` + action `2.6.2`, 142 projects.

If these cohorts were counted merely as structured taxonomy coverage, the combined candidate ceiling would be 857 / 4,305 = 19.9071%.

That figure is **not production coverage** and must never be represented as such.

### TED procurement prevalence

The conservative candidate CPV families are materially present in the complete qualified TED Italy universe through 2026-09-12:

- `digital_transformation`: 10,501 candidate-CPV notices;
- `waste_circular_economy`: 559 candidate-CPV notices.

These counts establish procurement-family prevalence only. They do not establish linkage from a funded project to a procurement notice.

### Project-level linkage

Two deterministic project-linkage paths were tested across the complete qualified TED Italy universe of 177,294 notices / 718 pages:

1. projected `eu-funds-identifier` exact CUP reference + matching candidate CPV;
2. exact CUP token in already-qualified `notice-title` or `description-proc` + matching candidate CPV.

Result for both candidate domains and both linkage paths:

- `digital_transformation`: 0 / 573 linked projects;
- `waste_circular_economy`: 0 / 142 linked projects.

The zero result is a strict result under these exact evidence rules. It is not evidence that no procurement occurred; it is evidence that the current admitted TED projection does not provide a deterministic project-level linkage for these cohorts.

## Phase R conclusion

The 40% Phase R target is **not met**.

It may not be reached by:

- counting safe structured source rows as classified coverage;
- treating CPV prevalence as project linkage;
- broadening intervention mappings semantically;
- fuzzy title/description matching;
- inferring project identity from geography, timing, buyer, value or generic similarity;
- adding domains solely to increase the numerator.

## Reopening conditions

Candidate production promotion may be reconsidered only if a future gate provides all of the following:

1. a public source or already-admitted field that deterministically links the funded project to procurement evidence;
2. zero-PII before receipt under the permanent product constraint;
3. no human contact, registration-by-contact or source-owner approval requirement;
4. exact reproducible linkage rules with fail-closed ambiguity handling;
5. regression tests proving that OPEN/CLOSED/UNRESOLVED semantics are unchanged except for explicitly admitted evidence;
6. measured project-level coverage on the frozen corpus, reported separately from source-data availability and market prevalence.

Until those conditions are met, the candidate domains remain diagnostic only and must not enter `ComponentDomain` or production mapping.
