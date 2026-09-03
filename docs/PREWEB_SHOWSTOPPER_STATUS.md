# Pre-web showstopper closure status

Status: **WEB BUILD GO; LIVE SOURCE ACTIVATION REMAINS FAIL-CLOSED**

This is the final closure map for the technical risks identified before UI implementation.
A20 remains the authoritative final gate.

## 1. Funded-project source A1

**Status: EXTERNAL LIVE-INGEST BLOCKER — DOES NOT BLOCK WEB BUILD.**

Completed internally:

- PRR Projects remains fail-closed and cannot be called by a live intelligence collector;
- dataset-specific licence ambiguity is recorded rather than inheriting a generic portal licence;
- exact route/schema/free-text/privacy/reuse questions are frozen in
  `docs/A1_PRR_SOURCE_CLARIFICATION.md`;
- no download-then-filter fallback is permitted;
- the web layer is isolated behind a frozen customer-safe read model, so activating or replacing the funded-project collector does not require changing the browser contract.

Closure for live ingestion still requires an authoritative source-owner response that makes RIGHTS, ACCESS, TRANSPORT and FREE-TEXT SAFETY green for one exact machine route.

## 2. Validation universe

**Status: WEB CONTRACT CLOSED; SOURCE-TRANSFER EVIDENCE REQUIRED BEFORE LIVE ACTIVATION.**

The repository enforces that Portugal 2030 Phase-0 evidence cannot be inherited by PRR Projects.
`source_validation.py` is a separate gate from source compliance. Portugal 2030 is marked validated for
the frozen Phase-0 wedge; PRR is explicitly NOT_VALIDATED. No current funded source is product-ready for live activation.

If PRR becomes A1-approved, the preregistered source-transfer confirmation described in
`docs/SOURCE_UNIVERSE_VALIDATION.md` must pass before activation. This changes backend source eligibility, not the web-facing read model.

## 3. Procurement linkage / false OPEN

**Status: INTERNAL FALSE-OPEN ESCAPE HATCH CLOSED; EXTERNAL NATIONAL SOURCE REQUIRED BEFORE LIVE OPEN.**

Completed internally:

- OPEN coverage is no longer represented by an unqualified boolean; every component names the
  required procurement sources and the sources actually completed;
- TED-only absence cannot produce OPEN when Portuguese national coverage is required;
- grouped rail-crossing scope is detected and withheld unless the component boundary is resolved;
- the corrected PACS-FC-04022300 failure mode has a historical regression replay that cannot become
  the old false OPEN or a false CLOSED.

A Portuguese national procurement source must still pass `docs/NATIONAL_PROCUREMENT_SOURCE_GATE.md`
before live production can claim complete national coverage. Until then, incomplete coverage yields
`UNRESOLVED`, never a fabricated `OPEN`. This is a runtime/source-activation constraint, not a reason to delay UI implementation.

## 4. True end-to-end replay

**Status: CANONICAL PIPELINE/READ-BOUNDARY REPLAY CLOSED. LIVE-SOURCE REPLAY DEFERRED TO SOURCE ACTIVATION.**

The canonical path is exercised as:

`FundingProject -> deterministic component extraction -> exact evidence binding -> candidate matching
-> component state -> project aggregation -> customer-safe read model -> deterministic content hash`.

The historical PACS-FC-04022300 regression is also replayed through the canonical orchestration.
That is sufficient to freeze the UI contract. A separate live-source acceptance replay remains mandatory before live funded-project ingestion is enabled.

## 5. Model fallback

**Status: CLOSED FOR MVP.**

The MVP is deterministic-only. If deterministic extraction leaves unmatched scope requiring fallback,
that incompleteness forces component/project `UNRESOLVED`; it cannot create OPEN. No unapproved local
model is required for the web build.

A model can be introduced later only through the separate A9 production gate and may never set state.

## 6. Persistence / reconstruction

**Status: CLOSED FOR EXACT EVIDENCE PROVENANCE.**

Migration `002_exact_source_spans` adds append-only persistence for:

- component project-scope source field, offsets and exact evidence text;
- accepted procurement source field, offsets and exact evidence text.

`apply_all_migrations()` applies the base ledger plus exact-evidence migration from an empty database.
Integration tests round-trip both source-span types and prove the tables remain append-only.

## Final web-build consequence

The technical contract that the browser depends on is now frozen and regression-tested. The remaining
unknowns are source activation facts, not web-contract design unknowns. Therefore:

1. web implementation may start now against the customer-safe read model and safe fixtures;
2. live funded-project ingestion remains disabled until A1 is approved;
3. live `OPEN` output remains impossible where required national procurement coverage is incomplete;
4. PRR source-transfer validation and live E2E acceptance remain mandatory before the live source switch;
5. paid production remains governed separately by A19.

No source-safety requirement has been weakened to reach web-build readiness.
