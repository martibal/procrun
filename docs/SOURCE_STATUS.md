# ProcRun source status

Status date: 2026-09-03
Terms/compliance re-review due: 2026-11-30 unless a source contract says otherwise.
Canonical product spec: `docs/PRODUCT_FOUNDATION_V2.md`

## Production rule

Production source use is enforced by `procrun.source_contracts`. Every network collector must call `require_live_source()` before retrieval.

A route is usable only when all three gates are approved:

1. **RIGHTS** — commercial reuse/derivative use is approved;
2. **ACCESS** — automated access through the exact route is approved;
3. **DATA SAFETY** — prohibited fields can be excluded before receipt.

Anything else fails closed. Public availability is not sufficient.

## Current v2 decision

**TED Search API is the production foundation for ProcRun v2.**

Known Portugal funded-project discovery source families are **CLOSED BY DEFAULT** for product development. They are not dependencies for the active-infrastructure opportunity product and must not be reopened merely to recreate the retired funded-project-first product.

The old Portugal 2030 discovery blocker is therefore no longer a website-build blocker.

## Current source registry

| Source | Overall | Rights | Access | Data safety | v2 implication |
| --- | --- | --- | --- | --- | --- |
| TED Search API | APPROVED | APPROVED | APPROVED | APPROVED | Production source for opportunity discovery and market intelligence |
| Mais Transparência project search | CONDITIONAL | CONDITIONAL | CONDITIONAL | CONDITIONAL | Research/history only; not a v2 dependency |
| Mais Transparência project detail | BLOCKED | CONDITIONAL | CONDITIONAL | BLOCKED | Must not be ingested |
| PT2030 operations bulk workbook | BLOCKED | CONDITIONAL | APPROVED | BLOCKED | Must not be downloaded then filtered |
| Portal BASE / APIBase2 | BLOCKED | CONDITIONAL | CONDITIONAL | BLOCKED | No production calls |

Research candidates not registered in `SOURCE_CONTRACTS` are not production sources.

## TED production contract

The MVP uses the public TED Search API with explicit server-side field projection and strict schema validation.

The final live capability inventory in CI #161 proved:

- executable Portugal query semantics;
- executable date filtering;
- combined Portugal + 12-month query;
- minimal server-side projection;
- individual projectability of every retained qualification field;
- full iteration across 18,776 Portugal notices in the tested 12-month slice;
- 4,893 infrastructure notices;
- 3,812 later/active-stage infrastructure notices;
- 100.0% title and description population for the tested early and later infrastructure slices.

The v2 product decision from that run was:

- active infrastructure opportunity feed: SUPPORTED;
- procurement market intelligence: SUPPORTED;
- early procurement runway: NOT SUPPORTED;
- comprehensive EU-funding subset: NOT SUPPORTED.

### TED transport requirements

- endpoint: TED Search API v3;
- explicit requested-field allowlist only;
- server-side projection only;
- ITERATION pagination for complete walks;
- bounded page size and field-cell budget;
- duplicate publication numbers fail closed;
- timeout/incomplete pagination fails closed;
- unknown envelope/notice fields fail before normalization;
- raw response bodies and iteration tokens are not persisted for customer use.

### Intelligence-safe field policy

Customer intelligence may use approved non-person procurement fields such as:

- publication number/date;
- notice type;
- procedure identifier;
- notice title;
- procurement description/scope;
- CPV classification;
- contract nature;
- procedure type;
- estimated value/currency;
- place-of-performance subdivision;
- approved EU-funding markers where present.

The v2 customer contract does not require contact person, personal email, phone, supplier/winner identity, personal/postal address, tax identifiers or equivalent person-identifying fields.

Any production field beyond the frozen contract requires a source-contract review before use.

## Zero-PII rule

No natural-person data may enter the intelligence pipeline.

Critical rule:

> **Do not receive a broad response containing prohibited fields and discard them afterwards.**

If a route cannot prevent prohibited fields from entering the response, it remains blocked regardless of convenience or public availability.

Account/billing/support PII belongs to the separate customer control plane and is not an intelligence-source exception.

## Closed Portugal funded-project discovery families

The following source families have already been investigated and do not currently satisfy the complete v2/zero-PII source contract needed for funded-project ingestion:

- Mais Transparência project search/detail;
- Portugal 2030 approved-operations bulk workbooks;
- Portal BASE/APIBase2;
- Kohesio project download/REST routes;
- EU Knowledge Graph/SPARQL coverage tested for the earlier product path;
- programme/managing-authority variants documented in the research record.

They remain useful historical research but are not prerequisites for ProcRun v2.

A known family may only be reopened when **genuinely new authoritative evidence** establishes the exact safe transport, rights/access and required field boundary. Do not weaken the privacy rule or perform broad row/file probes to look for a workaround.

## Website source presentation

Customer-facing pages must:

- credit TED/EU as required;
- identify ProcRun's transformation/classification separately from source facts;
- provide publication/source references;
- avoid implying EU/TED endorsement;
- avoid distorting source meaning;
- show an as-of/observation timestamp.

The browser must consume the ProcRun customer-safe read model, not arbitrary raw TED responses.

## Review expiry

Approved live-source reviews are time-bounded. `require_live_source()` rejects stale approved sources until the then-current terms are rechecked and the registry is explicitly renewed.