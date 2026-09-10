# A21a existing-context fallback probe

Status: **DEVELOPMENT DIAGNOSTIC — NOT A RELEASE GATE**

## Question

The frozen 60-case A21a title-utility development review found that some exact project titles are not useful enough on their own to explain the funded intervention. Before qualifying a new source, ProcRun must first determine whether the already-approved OpenCoesione operation-list route contains additional non-person project metadata that could provide useful context for those weak-title cases.

## Scope

This probe is deliberately narrower than an evidence qualification.

It measures only the availability and distinctness of two fields already admitted by the production OpenCoesione collector:

- specific objective;
- intervention category.

The probe reports aggregate counts only for development cases whose title was already judged `NOT_USEFUL`.

## What this does not establish

A non-empty objective or intervention category is **not automatically source evidence** and is not promoted into the customer-facing A21a evidence contract by this probe.

This probe does not establish that either field is sufficiently project-specific, procurement-relevant or useful to customers. It only answers whether there is enough existing context to justify a separate blind utility review before ProcRun searches for and qualifies a new source.

## Safety boundary

The probe:

- receives no new source field that is not already admitted by the current production OpenCoesione collector;
- does not add objective or intervention category to the stricter A21a sanitized-source ingress contract;
- emits only aggregate counts, never project text;
- uses no component, classification, matching or evidence-retrieval output;
- does not touch the sealed A21/A21a holdout;
- does not involve local execution, SSH or human/source-owner contact.

The absolute zero-PII and no-contact requirements remain unchanged.

## Decision sequence

1. Reproduce the exact frozen 60-case source-only development sample and verify its source/sample hashes.
2. Restrict the diagnostic to the previously adjudicated `NOT_USEFUL` title cases.
3. Measure whether specific objective and intervention category are present and distinct from the title.
4. If existing metadata has meaningful coverage, perform a separate source-only blind utility review before changing the evidence contract.
5. If existing metadata lacks meaningful coverage or fails the later utility review, qualify a richer external source under the normal zero-PII source gate.
6. Freeze the eventual A21a utility threshold before any final holdout evaluation.

No percentage produced by this development diagnostic is itself a release threshold.
