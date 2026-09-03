# Portugal national procurement coverage gate

Status: **BLOCKING OPEN / WEB BUILD**

## Why TED alone is insufficient for the OPEN invariant

ProcRun's `OPEN` state means that no relevant procurement was found in all approved sources required
for the stated coverage boundary. TED is an approved, field-projected source, but TED is the EU
publication layer and is not a complete national register of every Portuguese public procurement
procedure relevant to the Phase-0 product mechanism.

The corrected Phase-0 cohort itself used national procurement evidence from Diário da República and
other authoritative project/procurement sources. The critical correction of `PACS-FC-04022300` was
caused by Portuguese procedure 3809/2026: missing that procedure produced the highest-cost error, a
false project-level OPEN.

Therefore production code must never infer `coverage_complete=True` from successful TED pagination
alone.

## Current national candidates

### Portal BASE / IMPIC API

The official API is useful for discovery and daily updates, but its documented response surface is not
field-projectable. Contract records include adjudicatário/supplier fields and other identity-bearing
fields. ProcRun's absolute rule prohibits receiving a broad response and discarding prohibited fields
locally. The route therefore remains BLOCKED for the intelligence plane until IMPIC provides an exact
safe announcement/project-procurement response or server-side projection contract.

### Diário da República / INCM

DRE is the authoritative publication source for Portuguese public-procurement announcements. Public
announcement documents/pages contain contact/person data alongside procurement content, so scraping or
downloading the full page/document is not an acceptable intelligence-plane transport. A machine route
can be approved only if INCM documents a bounded response containing the non-personal procurement
fields ProcRun needs before receipt.

## Minimum safe national announcement surface

The required surface is intentionally small:

- announcement/publication identifier;
- publication date;
- procedure/contract title or object;
- description/scope where covered by a pre-publication zero-natural-person guarantee;
- CPV;
- procedure type;
- base/estimated value and currency;
- place/NUTS where available;
- EU-funding/project reference where available;
- canonical source URL.

No contact person, email, phone, street-address person field, supplier/adjudicatário identity or other
natural-person identifier may enter the intelligence plane.

## Exact external clarification required

An authoritative response from IMPIC or INCM must establish at least one production route that:

1. is permitted for recurring automated/commercial reuse;
2. returns only the bounded non-personal announcement surface before receipt, or is source-specifically
   guaranteed never to contain natural-person identifiers;
3. covers the Portuguese announcement population needed to support a defensible `OPEN` state;
4. provides stable pagination/completeness semantics and a schema/version boundary that can fail closed;
5. documents latency/refresh expectations sufficient to state an `as of` coverage date.

## Production invariant

Until this gate is green:

- TED evidence may create `CLOSED` when a high-confidence positive match exists;
- TED-only absence may **not** create `OPEN`;
- any component whose national coverage is required remains `UNRESOLVED`;
- the web build remains blocked because a live product that cannot safely establish national absence
  has not yet proven the core runway contract.
