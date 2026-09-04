# OpenCoesione source-transfer confirmation — preregistration

Status: **FROZEN BEFORE LIVE PROJECT PAYLOAD ACCESS**

Date frozen: 2026-09-04.

This gate is independent of source-lawfulness approval. OpenCoesione does not inherit the Portugal 2030 Phase-0 result. The exact approved PR FESR Lombardia operation-list payload must demonstrate that the canonical funded-project -> component -> TED procurement-evidence -> state -> customer-safe read-model mechanism transfers to this source family before web development may begin.

## Immutable source boundary

- funded-project source: `opencoesione_2021_2027_operations`;
- exact live pilot: PR FESR Lombardia 2021-2027 operation-list ZIP/CSV;
- source bytes must pass the frozen OpenCoesione schema/parser contract;
- beneficiary identity fields are never mapped to `FundingProject`;
- procurement source: `ted_search_api` only;
- any absence conclusion is therefore explicitly TED-scoped.

No source owner, authority, customer or other human may be contacted for this validation.

## Population and cohort rule

The source-transfer cohort is derived mechanically from the full accepted PR FESR Lombardia list after schema validation:

1. map every accepted operation to canonical `FundingProject`;
2. run the existing frozen deterministic component extractor across all five current component domains;
3. an operation is eligible only if at least one deterministic component is extracted from an exact source span;
4. order eligible operations by `sha256("opencoesione-transfer-v1|" + operation_code)` ascending;
5. take the first 30 unique operations, or fail the gate if fewer than 30 eligible operations exist;
6. no replacement, discretionary exclusion or post-outcome resampling is allowed.

The cohort is deliberately defined from the current taxonomy rather than after inspecting Italian source outcomes. Unmatched text remains a product limitation and may force `UNRESOLVED`; it may not be repaired by changing the sample after results are known.

## TED coverage rule

For each extracted component, the validation must issue a bounded TED Search API query using only the approved projected field surface. The query is built deterministically from:

- Italy as procurement country scope;
- the project timing/cutoff boundary;
- the component rule's frozen CPV prefixes where available;
- frozen component phrases only where a textual clause is required by TED query syntax.

A component receives complete TED coverage only if the collector reaches a normal complete termination with no timeout, missing iteration token, page cap or count mismatch. Any incomplete retrieval produces `UNRESOLVED`, never `OPEN`.

Positive procurement evidence must still pass the existing exact-span candidate/matching rules. Search retrieval by itself never closes a component.

## Frozen cutoff

The confirmation uses the latest complete source-list update date as the project observation boundary and a TED cutoff no later than the validation execution date. Evidence published after the cutoff cannot rewrite the state.

## Pass/fail thresholds

All thresholds are frozen before live project payload access:

1. **Transport/schema:** 100% of the accepted source batch passes the exact source route, provenance and schema checks; otherwise FAIL.
2. **Cohort availability:** at least 30 deterministic-component-eligible operations; otherwise FAIL.
3. **Pipeline integrity:** 30/30 cohort operations reach a deterministic customer-safe read-model object or an explicit fail-closed `UNRESOLVED` result without exception or raw-source leakage; otherwise FAIL.
4. **Resolved share:** at least 24/30 (80%) project outcomes are `OPEN`, `PARTIAL` or `CLOSED`; otherwise FAIL.
5. **Commercially actionable retained share:** at least 6/30 (20%) are `OPEN` or `PARTIAL`; otherwise FAIL.
6. **Suppression value:** at least 3/30 (10%) are `CLOSED`; otherwise FAIL.
7. **False-OPEN invariant:** zero `OPEN` component/project states may be produced from incomplete TED retrieval, unresolved component scope, missing required coverage or post-cutoff evidence; any violation is immediate FAIL.
8. **Privacy/read boundary:** zero forbidden beneficiary/contact/raw-response fields may appear in canonical `FundingProject` or customer-safe read models; any violation is immediate FAIL.
9. **Determinism:** repeated construction of every accepted customer-safe object must produce identical content hashes; any mismatch is FAIL.

These thresholds may not be lowered after observing the source-transfer outcome. A failed gate means OpenCoesione is not product-ready for the canonical runway mechanism under the current implementation.

## Launch-universe consequence

If and only if this gate passes, the validated launch funded-project universe becomes the bounded **PR FESR Lombardia 2021-2027 / Italy TED-scoped runway wedge** represented by this source-transfer test. Older `ProcRun Portugal` packaging is then stale and must be removed before web build. If the gate fails, web remains blocked; the result may not be repaired by pretending that the Portuguese funded-project route is live.
