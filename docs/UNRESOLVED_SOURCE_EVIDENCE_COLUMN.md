# UNRESOLVED source-evidence customer column

Status: **IMPLEMENTATION CONTRACT — QUALITY VALIDATION STILL REQUIRED**

## Customer problem

A customer must not be asked to trust the label `UNRESOLVED` without seeing the source wording behind the unresolved scope. The customer-facing table therefore needs a text field that exposes the exact project wording associated with the component(s) that remain unresolved.

## Authoritative text source

For the approved OpenCoesione PR FESR Lombardia 2021-2027 operation-list route, `SintesiProgetto_OperationSummary` is mapped directly to `FundingProject.project_scope_text`.

The A21a source requalification established that the RGS upstream rule covers both `TITOLO_PROGETTO` and `SINTESI_PROG`. This document does not reopen any other source family.

## Read-model contract

The customer-safe read model exposes `unresolved_source_evidence` at project level.

Rules:

1. The field is populated only when the project state is `UNRESOLVED`.
2. It contains only exact `project_scope_text` spans already attached to components whose state is `UNRESOLVED`.
3. The text is never generated, paraphrased or translated inside this contract.
4. Duplicate source spans are collapsed.
5. An `UNRESOLVED` project with no unresolved component source span fails closed instead of emitting an unexplained label.
6. Resolved project states expose an empty unresolved-evidence field.

This makes the browser/API layer able to render the requested table column without reproducing classification logic.

## What this does not prove

This implementation proves provenance and exact-span behaviour. It does **not** yet prove that the selected source wording is sufficiently useful to a customer in representative real projects.

The next empirical gate is therefore quality, not source access:

- representative OpenCoesione `SINTESI_PROG` cases;
- blind adjudication of which source wording is actually useful for explaining unresolved cases;
- exact-span validity = 100%;
- no rewritten/hallucinated source wording;
- retrieval relevance must meet the preregistered A21a threshold before the column is treated as production-quality.

The sealed A21 holdout remains untouched.
