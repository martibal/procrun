# Pre-web showstopper closure status

Status: **WEB BUILD BLOCKED**

This is the working closure map for the six technical risks identified before UI implementation.
A20 remains the authoritative final gate.

## 1. Funded-project source A1

**Status: EXTERNAL BLOCKER — NOT CLOSED.**

Completed internally:

- PRR Projects remains fail-closed and cannot be called by a live intelligence collector;
- dataset-specific licence ambiguity is recorded rather than inheriting a generic portal licence;
- exact route/schema/free-text/privacy/reuse questions are frozen in
  `docs/A1_PRR_SOURCE_CLARIFICATION.md`;
- no download-then-filter fallback is permitted.

Closure requires an authoritative source-owner response that makes RIGHTS, ACCESS, TRANSPORT and
FREE-TEXT SAFETY green for one exact machine route.

## 2. Validation universe

**Status: TECHNICAL GATE CLOSED; SOURCE-TRANSFER EVIDENCE STILL REQUIRED.**

The repository now enforces that Portugal 2030 Phase-0 evidence cannot be inherited by PRR Projects.
`source_validation.py` is a separate gate from source compliance. Portugal 2030 is marked validated for
the frozen Phase-0 wedge; PRR is explicitly NOT_VALIDATED. No current funded source is product-ready.

If PRR becomes A1-approved, the preregistered source-transfer confirmation described in
`docs/SOURCE_UNIVERSE_VALIDATION.md` must pass before activation.

## 3. Procurement linkage / false OPEN

**Status: INTERNAL FALSE-OPEN ESCAPE HATCH CLOSED; EXTERNAL NATIONAL SOURCE BLOCKER REMAINS.**

Completed internally:

- OPEN coverage is no longer represented by an unqualified boolean; every component names the
  required procurement sources and the sources actually completed;
- TED-only absence cannot produce OPEN when Portuguese national coverage is required;
- grouped rail-crossing scope is detected and withheld unless the component boundary is resolved;
- the corrected PACS-FC-04022300 failure mode has a historical regression replay that cannot become
  the old false OPEN or a false CLOSED.

Closure still requires one approved Portuguese national procurement announcement source with a safe
pre-receipt field surface and completeness semantics. Requirements are frozen in
`docs/NATIONAL_PROCUREMENT_SOURCE_GATE.md`.

## 4. True end-to-end replay

**Status: CORE PIPELINE REPLAY CLOSED; FULL LIVE-SOURCE REPLAY BLOCKED BY 1 AND 3.**

The canonical path is now exercised as:

`FundingProject -> deterministic component extraction -> exact evidence binding -> candidate matching
-> component state -> project aggregation -> customer-safe read model -> deterministic content hash`.

The historical PACS-FC-04022300 regression is also replayed through the canonical orchestration.
A live-source replay cannot truthfully be completed until the funded-project and national procurement
sources are approved.

## 5. Model fallback

**Status: CLOSED FOR MVP.**

The MVP is deterministic-only. If deterministic extraction leaves unmatched scope requiring fallback,
that incompleteness forces component/project `UNRESOLVED`; it cannot create OPEN. No unapproved local
model is required to start the eventual web build.

A model can be introduced later only through the separate A9 production gate and may never set state.

## 6. Persistence / reconstruction

**Status: CLOSED FOR EXACT EVIDENCE PROVENANCE.**

Migration `002_exact_source_spans` adds append-only persistence for:

- component project-scope source field, offsets and exact evidence text;
- accepted procurement source field, offsets and exact evidence text.

`apply_all_migrations()` applies the base ledger plus exact-evidence migration from an empty database.
Integration tests round-trip both source-span types and prove the tables remain append-only.

## A20 consequence

Do not start the web build yet. The remaining blockers are no longer ambiguous implementation work;
they are two explicit external source contracts plus the PRR source-transfer validation that can only
run after the funded source is safely available:

1. approve one funded-project source;
2. approve one complete-enough Portuguese national procurement source for OPEN;
3. if the funded source is PRR, run and pass its preregistered source-transfer confirmation;
4. run the resulting live end-to-end acceptance replay;
5. then change A20 to `WEB BUILD: GO` only if CI is green and no new contract-changing blocker appears.
