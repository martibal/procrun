# UNRESOLVED source-evidence semantics

Status: **CORRECTION BEFORE EMPIRICAL QUALITY VALIDATION**

The customer requirement is not merely to show project text next to an `UNRESOLVED` label. The column must show the exact project wording that actually caused a text/scope ambiguity when such wording is the reason the classification cannot be resolved.

The previous `customer-runway-v2` implementation exposed the primary evidence span of each unresolved component. That span proves that the component exists, but it is not necessarily the text that caused the unresolved condition.

For component-boundary ambiguity, the actual trigger is already represented by `ExtractionResult.unmatched_scope_spans`: exact spans from `FundingProject.project_scope_text` that the deterministic component rules could not safely resolve. Because the approved OpenCoesione collector maps `SintesiProgetto_OperationSummary` directly to `project_scope_text`, these spans are verbatim source wording from `SINTESI_PROG`.

`customer-runway-v3` therefore applies these rules:

1. `unresolved_source_evidence` is populated only when the project is `UNRESOLVED` **and** exact unmatched source spans exist.
2. The returned text must match the original `project_scope_text` at the stored offsets exactly.
3. The text is never generated, rewritten or translated by this contract.
4. If `UNRESOLVED` is caused by a TED review-band match, incomplete procurement coverage, or another non-text cause, the source-text column is empty rather than falsely attributing the state to project wording.
5. The existing component `state_explanation` and `coverage_note` remain the explanation surfaces for those non-text causes.

This correction is required before representative quality testing. The next empirical task is to measure whether real OpenCoesione `SINTESI_PROG` unmatched spans are sufficiently useful to customers and occur often enough to justify the dedicated table column.