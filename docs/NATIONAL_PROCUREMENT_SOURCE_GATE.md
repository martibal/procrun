# Portugal procurement coverage gate

Status: **MVP CLAIM BOUNDARY CLOSED: TED-SCOPED OPEN APPROVED; FULL NATIONAL COVERAGE STRUCTURALLY UNAVAILABLE UNDER CURRENT PUBLIC-EVIDENCE RULES**

This document records the deliberate MVP scope decision. ProcRun does not claim complete Portuguese national procurement absence.

## Non-negotiable validation constraint

ProcRun must be developed and validated without interviews, surveys, outreach, requests for clarification, source-owner contact, authority contact, customer contact, paid expert/legal consultation, or any other human-dependent approval path.

A source may become APPROVED only from already-public, independently inspectable evidence and machine-verifiable behaviour. Silence is never permission. A private email, bespoke assurance, legal opinion or verbal confirmation cannot close this gate.

## Permanent MVP OPEN definition

For the MVP, `OPEN` means exactly:

> **No relevant procurement found in TED as of DATE.**

This is a TED-scoped negative-search conclusion. It is not a statement that no procurement exists outside TED, including purely national or below-threshold Portuguese procedures.

The former stronger national-coverage definition is retired from the MVP. It may not be implied by UI copy, exports, methodology, API fields or marketing.

## Why the stronger national claim is not used

TED is already APPROVED and field-projected. It does not constitute a complete Portuguese national register. The corrected Phase-0 case `PACS-FC-04022300` demonstrated why TED absence cannot be relabelled as national absence: Portuguese procedure 3809/2026 changed the conservative interpretation when national evidence was considered.

That finding remains preserved. The solution is not to pretend TED has national completeness; it is to state the narrower TED coverage honestly.

## National candidate findings

### BASE / IMPIC API — BLOCKED

The official BASE API supports contract and announcement queries, but documented responses include identity-bearing supplier/adjudicatário fields and no documented server-side output projection satisfies ProcRun's pre-receipt zero-person boundary. Broad-response receipt followed by local deletion is prohibited.

### BASE / dados.gov.pt announcements — BLOCKED FOR INTELLIGENCE INGEST

The nationwide historical announcements dataset resolves important reuse/history questions but remains a broad download without an authoritative field-level machine projection or source-specific guarantee that every received text field is natural-person-free before receipt.

### Diário da República / INCM full announcement — BLOCKED

Full Part L announcement surfaces contain contact/service, email, telephone or author fields and therefore cannot enter the intelligence plane.

### Diário da República Part L RSS/index — PASSIVE FUTURE CANDIDATE

The RSS/index is not required for the MVP. It may be reconsidered only if already-public authoritative INCM documentation establishes an exact RSS item schema, a pre-publication zero-natural-person guarantee for every consumed title/summary field, sufficient archive/completeness semantics, reuse rights and detectable schema/version behaviour.

No contact or clarification request may be made. Until those public facts exist, the route stays disabled.

A passive quarterly documentation check is the only permitted follow-up.

## Production invariant

- TED Search API is the sole negative-search coverage source required for MVP `OPEN`.
- `OPEN` must always be rendered/exported with its TED scope.
- TED absence must never be described as complete Portuguese procurement absence.
- Positive evidence from another separately approved source may be retained only under that source's own contract; it cannot silently widen the negative-search coverage claim.
- BASE, DRE full notices and Part L RSS remain disabled for intelligence ingest unless they independently satisfy the zero-PII source contract from public evidence.

## Release consequence

`A20 LIVE PORTUGAL OPEN CLASSIFICATION` is APPROVED for the explicitly TED-scoped definition above. Full-national-coverage classification is not an MVP feature and is not a release blocker.