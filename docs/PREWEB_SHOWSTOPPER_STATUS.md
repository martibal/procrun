# Pre-web showstopper closure status

Status: **WEB BUILD BLOCKED — TWO PUBLIC-EVIDENCE SOURCE GATES REMAIN**

A20 remains the authoritative final gate.

## 1. Funded-project source A1

**Status: BLOCKED.**

PRR Projects is not production-approved from public evidence alone. The former source-owner clarification path is retired because ProcRun forbids outreach, authority/source-owner contact, customer contact and paid expert/legal consultation as validation mechanisms.

Valid closure now requires either:

- new authoritative public material that independently closes RIGHTS, ACCESS, TRANSPORT, FREE-TEXT SAFETY, SCHEMA and COVERAGE for the exact PRR production route; or
- a different funded-project source that passes the same gate entirely from public evidence.

No download-then-filter fallback is permitted.

## 2. Validation universe

**Status: INTERNAL GATE IMPLEMENTED; SOURCE-TRANSFER VALIDATION STILL REQUIRED AFTER A1.**

Portugal 2030 Phase-0 evidence cannot be inherited automatically by a replacement funded source. `source_validation.py` keeps source compliance separate from source-transfer validation.

When a funded-project source becomes A1-approved, its preregistered source-transfer confirmation must pass before production activation and before A20 may turn green.

## 3. Procurement linkage / false OPEN

**Status: INTERNAL FALSE-OPEN PROTECTION CLOSED; NATIONAL SOURCE GATE BLOCKED.**

Completed internally:

- every component names required procurement sources and completed sources;
- TED-only absence cannot produce OPEN where national Portugal coverage is required;
- incomplete coverage yields `UNRESOLVED`;
- grouped-scope ambiguity abstains;
- PACS-FC-04022300 is replayed as a regression case.

Still required: one Portuguese national procurement source must pass `docs/NATIONAL_PROCUREMENT_SOURCE_GATE.md` entirely from public evidence, with pre-receipt zero-PII safety and completeness semantics adequate for absence-based `OPEN` claims.

## 4. End-to-end replay

**Status: FIXTURE PIPELINE CLOSED; LIVE ACCEPTANCE BLOCKED BY SOURCE GATES.**

The canonical internal path is exercised as:

`FundingProject -> deterministic component extraction -> exact evidence binding -> candidate matching -> component state -> project aggregation -> customer-safe read model -> deterministic content hash`.

A true live-source acceptance replay cannot be completed until both remaining source gates are approved. Under the user's pre-build rule, that live acceptance is required before web work begins.

## 5. Model fallback

**Status: CLOSED FOR MVP.**

The MVP is deterministic-only. Unmatched scope that would require fallback forces `UNRESOLVED`; it cannot create `OPEN`.

## 6. Persistence / reconstruction

**Status: CLOSED.**

Exact source spans, append-only evidence provenance, empty-database migrations and reconstruction hashes are implemented and regression-tested.

## Final consequence

Do not start the web build yet.

Remaining work, in order:

1. qualify one funded-project source using public evidence only;
2. qualify one complete-enough Portuguese national procurement source using public evidence only;
3. run the funded-source transfer validation;
4. run live end-to-end acceptance;
5. require green CI;
6. only then change A20 to `WEB BUILD: GO`.

No human-dependent validation or weaker TED-only product pivot is an acceptable shortcut.
