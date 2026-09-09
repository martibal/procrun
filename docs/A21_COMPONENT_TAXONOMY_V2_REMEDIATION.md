# A21 component taxonomy v2 remediation

Status: IN PROGRESS

This remediation exists because the first frozen A21 benchmark exposed two hard limits in `component-taxonomy-v1`:

1. the deterministic phrase layer is documented and implemented as Portuguese/English only, while the A21 source corpus is Italian; and
2. the frozen taxonomy has no `energy_efficiency:battery_storage` category, so a benchmark containing source-evidenced battery-storage demand cannot reach the required component recall threshold under v1.

## Non-negotiable rules

- `component-taxonomy-v1` is not edited in place conceptually; the production rule identifier must advance to `component-taxonomy-v2`.
- No state rule changes are permitted in this remediation.
- No OPEN/CLOSED threshold is weakened.
- Every deterministic component still requires an exact verbatim source span.
- Italian phrase additions are extraction vocabulary only; they do not prove procurement.
- CPV remains a hint and never standalone CLOSED evidence.
- The sealed A21 holdout must not be opened or used to author the v2 rules.

## v2 scope

- add an explicit `energy_efficiency:battery_storage` frozen category;
- add conservative Italian extraction phrases for existing frozen categories where the Italian wording is unambiguous;
- update the local-model category guidance so its allowlist exactly matches v2;
- permit an Italian (`it-IT`) frozen component benchmark corpus without changing the local-model fail-closed contract;
- add regression tests for Italian exact-span extraction and battery storage.

## Validation consequence

The original 200-case A21 benchmark is now a diagnostic/development set for the v1 failure and may not be represented as an untouched post-remediation holdout. The separately frozen 50-case holdout remains sealed and is the protected empirical check after v2 is implemented. A new post-remediation general benchmark must be assembled from material not used to author the v2 rules before final product GO.
