# Phase R — candidate domain design gate

Status: **DIAGNOSTIC ONLY**

Reviewed: 2026-09-12

## Purpose

The public-definition qualification admitted two procurement-relevant candidate domains for further design:

- `digital_transformation`: intervention code `013` + action `1.2.3`;
- `waste_circular_economy`: intervention code `067` + action `2.6.2`.

This gate measures those candidates on the frozen 4,305-project Phase R corpus without adding them to the production `ComponentDomain` enum or changing any customer-facing classification.

## Frozen evidence contract

The diagnostic may use only:

- the exact frozen OpenCoesione source SHA-256 `35dc073ec9e5e06201080bc949a9da19dfd3366deee3524417491e2b2fd21c6a`;
- the already-qualified Regione Lombardia Socrata eight-field server-side projection;
- exact normalized CUP joins;
- the exact structured combinations preregistered above.

No beneficiary data, project narrative, organisation data, address/contact data or row-level artifact may be requested or emitted.

## Candidate semantics

### `digital_transformation`

The official action/call definition supports a procurement-relevant scope including IT services, digital technologies, software/cloud licences, electronic equipment and implementation services. The candidate is therefore narrower than generic SME digitalisation and is admitted for component-domain design only when both `013` and action `1.2.3` are present.

### `waste_circular_economy`

The official action/call definitions support a procurement-relevant scope including reuse/recycling infrastructure, collection systems, composting/recovery equipment, production-line changes and associated works. The candidate is admitted for component-domain design only when both `067` and action `2.6.2` are present.

## Fail-closed rules

- Intervention code alone is insufficient.
- Action alone is insufficient.
- A candidate hit is not OPEN/CLOSED evidence.
- A candidate hit does not create a `PurchaseComponent` in this gate.
- `ComponentDomain`, production mapping, customer read model and matching logic must remain unchanged.
- Any cohort-count drift fails the diagnostic rather than silently widening the rule.

## Decision rule

The diagnostic must measure the exact cohort size, overlap with already safely mapped projects and combined Phase R coverage ceiling.

If the two candidate cohorts reproduce and materially increase coverage, the next gate may design explicit component categories/CPV families for each candidate domain. Production admission still requires separate deterministic component-rule tests and a no-regression review of OPEN/CLOSED semantics.

The 40% Phase R target remains a commercial coverage gate and does not override evidence, privacy or no-contact constraints.
