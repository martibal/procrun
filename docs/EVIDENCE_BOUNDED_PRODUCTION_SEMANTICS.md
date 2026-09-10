# ProcRun evidence-bounded production semantics

Status: **AUTHORITATIVE OWN-CODE PRODUCTION CONTRACT**

This contract replaces the earlier inferential A21 release target. The old target asked ProcRun to prove that its component interpretation matched an independent human gold standard at fixed population metrics. That benchmark was never completed and must not be represented as passed.

ProcRun now makes a narrower and stronger class of production claims that can be verified mechanically from the admitted sources themselves. The product is not abandoned and no legal or privacy requirement is weakened. Ambiguity is converted to `UNRESOLVED`, not hidden or guessed.

## Logical project identity

`OperationLocalIdentifier` is the canonical logical identity for an OpenCoesione operation. CUP may be retained only as a procurement-reference alias. Distinct operations sharing a CUP must never collapse into one project. Exact duplicate local-ID rows may be collapsed; conflicting rows sharing a local ID fail closed.

## Component evidence

A production component exists only when a phrase from the frozen component taxonomy occurs verbatim in the approved project source text. Every component carries exact source offsets. No local model, LLM, semantic expansion or programme-context inference may manufacture a production component.

If no component can be established, or if unmatched source wording leaves the project boundary incomplete, the project is published as `UNRESOLVED`. The exact source wording that prevents resolution remains customer-visible.

## CLOSED

`CLOSED` is allowed only when a pre-cutoff TED record satisfies the frozen structural match requirements and carries an exact source span for the component. A structural candidate without the required exact component evidence cannot become CLOSED.

## OPEN

`OPEN` is not an assertion that procurement does not exist. It means exactly:

> **No procurement match satisfying ProcRun's frozen exact-evidence rules was found in TED as of DATE.**

OPEN additionally requires complete TED query coverage through the cutoff, a resolved component boundary, and zero accepted or review-band pre-cutoff candidates. A plausible exact-project-reference or CPV/geography candidate that cannot support CLOSED blocks OPEN and yields `UNRESOLVED`.

Customer-facing coverage wording must state that OPEN does not establish absence outside TED or under different wording/classification.

## Project state

Project aggregation remains deterministic: any unresolved component makes the project `UNRESOLVED`; all CLOSED => CLOSED; all OPEN => OPEN; a fully resolved OPEN/CLOSED mixture => PARTIAL. Empty component sets => UNRESOLVED.

## Privacy and provenance

Only the frozen customer-safe `RunwayProject` contract may cross to the web/product plane. Beneficiary identity, buyer/contact identity, source transport envelopes, raw source rows, model prompts and unvalidated candidate text are prohibited. Every published project remains hash-anchored and every source/evidence decision remains reproducible.

## Hard production proof

A release is own-code green only when the `infrastructure-closure` workflow proves on live approved sources that:

1. every logical OpenCoesione operation is represented; none is silently omitted;
2. the full TED Italy query universe is complete through the cutoff;
3. component and procurement source spans are exact;
4. component-free and ambiguous projects remain UNRESOLVED with exact source wording;
5. CLOSED never exists without exact accepted procurement evidence;
6. OPEN has no accepted/review candidate and uses the exact rule-bounded wording;
7. no prohibited customer fields cross the read-model boundary;
8. three repeated builds from the same frozen inputs produce the same output hash;
9. the real append-only PostgreSQL persistence path accepts the result;
10. the persisted customer-safe JSONL hash equals the in-memory proof hash;
11. the live universe contains at least one resolved customer result.

The workflow emits a hash/count-only proof report. It does not publish source rows or customer JSONL as an artifact.

## Status of historical A21/A21a work

Historical A21/A21a gold-standard and fallback experiments remain useful research provenance, but they are not production dependencies and they must not be used to imply that an uncompleted human-gold benchmark passed. The production path contains no model fallback that needs such a benchmark. Any future attempt to reintroduce inferred components or broader semantic claims creates a new release gate and cannot inherit this approval.
