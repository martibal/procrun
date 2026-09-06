# ProcRun — customer data and commercialization contract

Status: **NORMATIVE / MANDATORY**
Effective date: 2026-09-06
Applies to: all current and future customer-facing product surfaces, exports, APIs, documentation, marketing, pricing, billing copy, demos, samples and source links.

This contract exists to prevent a gap between (a) what upstream source licences and data-safety rules permit, (b) what ProcRun actually processes, (c) what ProcRun charges for, and (d) what customers are shown or given access to.

If any implementation, copy, export, API response, pricing statement or future feature conflicts with this contract, the conflicting change is rejected until the inconsistency is resolved. Commercial convenience never overrides source, privacy, attribution or customer-safe boundaries.

## 1. Core commercial premise

ProcRun does **not** sell exclusive access to public OpenCoesione or TED source data.

Where an approved upstream source is publicly accessible and permits commercial reuse under its applicable terms, ProcRun may use that source only within its separately approved source contract. Customer payment is for the ProcRun service layer built on top of approved sources, including source-bounded processing, component extraction, procurement matching, conservative state assessment, evidence linkage, supplier relevance, filtering, monitoring, history, workflow, exports and other explicitly approved derived functionality.

Customer-facing pricing and sales copy must therefore describe the paid product as ProcRun analysis, opportunity workflow, evidence, filtering and related service functionality. It must not imply that the customer is paying for exclusive ownership of, privileged access to, or proprietary rights in underlying public source data.

Forbidden examples include claims equivalent to:

- `Pay to access Lombardia public project data.`
- `Exclusive access to OpenCoesione data.`
- `ProcRun owns the underlying public procurement data.`

Acceptable framing is equivalent to:

- `ProcRun turns approved public funding and procurement sources into a supplier-side opportunity feed with evidence and filtering.`
- `The subscription pays for ProcRun's analysis, matching, workflow and customer-safe delivery layer.`

## 2. Public availability does not widen ProcRun's rights or safety boundary

A field, document or record being publicly reachable by a customer does **not** by itself make it admissible to ProcRun.

A public source link is navigational and evidentiary only. It does not:

- approve a new source;
- approve additional fields from an existing source;
- authorize ProcRun to ingest, store, transform, display or export data outside the approved source contract;
- weaken the zero-person intelligence-plane rule;
- make customer-visible any field excluded from the customer-safe read model;
- create a presumption that third-party content, logos, marks or embedded works may be reused.

Customers may independently follow an upstream source link and see information that ProcRun intentionally does not ingest or expose. That does not create an inconsistency. ProcRun's own surface remains deliberately narrower.

## 3. Source gate is mandatory before any customer use

No new external source may appear in production code, customer-facing copy, evidence, geography, enrichment, download, API output, export or UI unless it has first passed the same applicable source-gate process used elsewhere in ProcRun.

At minimum, the gate must establish from already-public evidence:

1. **RIGHTS** — the relevant commercial reuse, attribution, modification, redistribution and linking conditions;
2. **ACCESS** — a stable, bounded, no-contact technical access route appropriate for the intended use;
3. **DATA SAFETY** — the exact pre-receipt field/schema boundary and whether prohibited personal/contact/identity data can enter the intelligence plane;
4. **SCHEMA / SEMANTICS** — exact fields and meanings needed for the proposed customer claim;
5. **ATTRIBUTION / BRANDING** — required source credit and any logo, trademark, endorsement or third-party-content restrictions;
6. **CUSTOMER MAPPING** — the exact fields allowed into an approved customer-safe read model or explicitly versioned successor.

Temporary use, prior manual inspection, convenience, apparent public availability or the fact that a value looks correct never substitutes for this gate.

If the gate cannot be closed from already-public evidence without human contact, the source is rejected or remains blocked.

## 4. Customer-visible data boundary

Customer-facing product code may consume only:

- `src/procrun/read_model.py` (`customer-runway-v1`); or
- an explicitly versioned successor that has been approved under the same customer-safe boundary.

No web page, demo, CSV export, API route, sample, marketing component or billing surface may bypass this boundary by reading raw source payloads, collector objects, databases or ad hoc enrichment directly.

The fact that an upstream ZIP, CSV, API response or notice contains additional fields does not make those fields customer-safe.

Identity/contact/person fields excluded from the intelligence plane remain excluded even if the upstream publisher makes them publicly visible.

## 5. Source data and ProcRun analysis must be distinguishable

Every customer surface that combines upstream evidence with ProcRun-derived conclusions must make the distinction understandable.

The following concepts must not be collapsed into one another:

- **Source data / source evidence** — facts or text published by an approved external source;
- **ProcRun-derived analysis** — component extraction, matching, classification, state, supplier relevance, aggregation or other ProcRun transformation;
- **Coverage limitation** — what source universe was actually checked and what remains outside it.

A customer must be able to understand which statement comes from the source and which statement is ProcRun's analysis.

No derived statement may be presented as though it were directly asserted by the upstream publisher.

## 6. Attribution and source-link rules

Where an approved source's terms require attribution, ProcRun must preserve the required source credit in the relevant customer-facing documentation or evidence surface.

Source links must point to the original approved publication or an otherwise approved official source location whenever practical.

A source link must never be described in a way that implies endorsement, partnership or certification by the source owner, the EU, TED, OpenCoesione or another public body.

ProcRun must not use third-party logos, trademarks or protected visual assets merely because source data may be reused. Rights in data and rights in branding are separate questions.

Any source-specific attribution wording belongs in the source contract / source-status documentation and must remain consistent with customer-facing implementation.

## 7. Current source-specific commercial boundary

### OpenCoesione PR FESR Lombardia 2021-2027

The approved ProcRun route is the exact bounded OpenCoesione 2021-2027 operation-list publication used for PR FESR Lombardia, subject to the frozen source contract in `docs/OPENCOESIONE_A1_QUALIFICATION.md` and `docs/SOURCE_STATUS.md`.

ProcRun may commercialize the ProcRun service built from the approved route only to the extent already established by that source contract. The customer-facing product must retain source attribution and the approved customer-safe field boundary.

A customer's ability to download the original OpenCoesione ZIP does not permit ProcRun to expose source-only beneficiary identity, unapproved geography, or any other field outside the customer-safe contract.

### TED

TED is approved only for the roles and bounded field-projected contract recorded in ProcRun's source documentation. Customer-facing procurement evidence and negative-search claims must preserve the frozen TED coverage limitation.

For MVP `OPEN`, the canonical wording remains:

> **No relevant procurement found in TED as of DATE.**

This must not be converted into a claim that no procurement exists outside TED, including national or below-threshold procedures.

Public availability of a TED notice does not authorize ProcRun to expose personal/contact information or fields outside the approved projection.

## 8. Pricing and packaging consistency

Pricing, checkout, Terms, FAQ, landing page, methodology, demo, account surfaces and sales copy must describe the same product scope.

Before any paid release or pricing change, verify that:

- the named geography matches actual live source coverage;
- the named source coverage matches the approved source registry;
- the features listed in pricing are implemented and customer-safe;
- no paid feature is described as exclusive access to underlying public data;
- any export/API entitlement contains only approved customer-safe fields;
- source attribution remains available where required;
- coverage caveats are not removed from paid tiers;
- no marketing copy implies broader rights, completeness, certainty or endorsement than the underlying contracts support.

A pricing tier never grants additional source rights. A higher-paying customer receives more approved ProcRun functionality, not a wider legal or privacy boundary.

## 9. Export, API, demo and sample rules

The same legal/data boundary applies regardless of delivery format.

CSV, JSON, API, downloadable samples, demos, screenshots and copied evidence must not expose anything that the normal authenticated UI would be prohibited from exposing.

A field cannot become permissible merely because it is placed in an export rather than on-screen.

Anonymous demos and public samples must be at least as restrictive as authenticated customer output unless a narrower, explicitly approved public-safe contract exists.

## 10. Consistency rule for written claims

The repository is the source of truth for product/source constraints. Customer-facing text must not contradict normative source, privacy, evidence, coverage or commercialization documents.

When a change affects any of the following, all affected surfaces must be reviewed in the same change or release:

- source coverage;
- geography;
- OPEN/CLOSED semantics;
- available evidence;
- customer-visible fields;
- attribution;
- product/package name;
- price;
- export/API contents;
- legal/Privacy/Terms statements;
- claims about completeness, exclusivity, provenance or source endorsement.

If two documents or customer surfaces disagree, the more restrictive approved source/privacy/customer-safe rule controls until the inconsistency is corrected.

## 11. Fail-closed release gate

A customer-facing change touching source-derived information must not ship unless the reviewer can answer **yes** to all applicable questions:

1. Is every source already approved for this exact role?
2. Is every displayed/exported field admitted to the customer-safe contract?
3. Are source facts and ProcRun-derived conclusions clearly distinguishable?
4. Are required attribution and source links present?
5. Does the copy avoid implying exclusive ownership/access to public data?
6. Does the copy preserve actual geographic and procurement coverage?
7. Are privacy/person/contact exclusions preserved?
8. Do pricing, Terms, Privacy, methodology, demo, API/export and product UI remain mutually consistent?
9. Does the change avoid unapproved logos, endorsement claims or third-party content?
10. Is any new source or new field fully source-gated before use?

Any `no`, `unknown` or unresolved conflict means **DO NOT RELEASE**.

## 12. Incident and remediation rule

If an unapproved source, field or claim reaches customer-facing code or a diagnostic crosses the approved data-safety boundary:

- remove or disable the affected customer-facing use immediately;
- preserve fail-closed behaviour;
- verify persistence/logging before deleting evidence blindly;
- record the incident and remediation in `docs/SOURCE_STATUS.md` or the designated incident record;
- do not treat prior accidental use as evidence of approval;
- require the normal source/field gate before any future reintroduction.

## 13. Authority and maintenance

This document is a permanent product contract and must be read together with:

- `README.md`;
- `docs/SOURCE_STATUS.md`;
- `docs/OPENCOESIONE_A1_QUALIFICATION.md`;
- `docs/PRODUCT_FOUNDATION_FINAL.md`;
- `docs/BUILD_GATES.md`;
- `THIRD_PARTY_NOTICES.md`;
- the approved customer-safe read-model contract.

Future development must not silently weaken this contract. Any deliberate change to the commercial/source/customer boundary requires an explicit versioned documentation change, source/legal evidence sufficient to support it, and corresponding implementation/tests before release.

**Permanent rule:** public availability is not equivalent to ProcRun admissibility; source reuse rights are not equivalent to branding/person-data rights; and customer payment is for the approved ProcRun service layer, not for exclusive ownership of underlying public source data.
