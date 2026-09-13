# ProcRun GUI design gate

Status: **DESIGN READY / COMMERCIAL RELEASE STILL FAIL-CLOSED**

## Purpose

This gate separates **visual design work** from **commercial activation**.

The Readiness backend contract is sufficiently frozen to design the customer interface without weakening the commercial correctness gate. GUI design may therefore proceed against the headless API and domain contracts already in `main`.

This does **not** release a bando, enable paid analysis, enable checkout, or permit a dossier to be generated without an exact immutable commercial validation release.

## Frozen product surfaces for GUI design

The GUI must be designed around exactly these three server-side surfaces:

1. `GET /v1/readiness/preview`
   - may be shown before purchase;
   - returns only availability/state language;
   - must not reveal exact historical sample size, statistics or comparable identities.
2. `POST /v1/readiness/unlock`
   - paid surface;
   - requires a valid purchase capability;
   - fails closed unless the exact source-package hash and benchmark-snapshot hash have a matching `RELEASED` validation record.
3. `POST /v1/readiness/dossiers`
   - paid persistence surface;
   - requires the same purchase boundary and matching release;
   - freezes structured adviser confirmations and returns the immutable dossier hash.

Python remains the single source of truth for all calculations and classification. The GUI must not reimplement thresholds, requirement logic, benchmark calculations or eligibility-like inference in TypeScript.

## Input contract

The GUI may collect only the structured Readiness inputs already admitted by the backend contract:

- `bando_code`;
- `benchmark_snapshot_id`;
- `proposed_project_cost_eur` (optional where the selected source package has no cost-bound check);
- `proposed_funding_eur`;
- `proposed_duration_months` (optional);
- structured adviser confirmation enums required by the selected source package.

No customer free-text field belongs in the readiness data plane. No person/company lookup is added for GUI convenience.

## Output language boundary

Visual design must preserve the frozen semantics in `docs/READINESS_DOSSIER_V2.md`:

- never `ELIGIBLE` / `INELIGIBLE`;
- never approval probability;
- never a claim that ProcRun performed professional/legal eligibility verification;
- mechanical results are factual comparisons to an exact published boundary;
- context-dependent items remain `PROFESSIONAL_VERIFICATION_REQUIRED` or structured adviser confirmations;
- source provenance and hashes remain visible/auditable in the paid dossier.

## Commercial activation invariant

GUI work may use fixtures, mocks and design-time states. Production paid actions may not use fixtures or a design override.

The commercial path remains fail-closed in `readiness_application._commercial_validation_binding()`: a missing exact release raises `DossierBlockedError`. A visual component, feature flag or checkout implementation must never catch that condition and substitute a successful result.

The first launch bando `RLO12026055023` remains **validation-in-progress** until its exact source package, benchmark snapshot, blind reconstruction, adversarial cases and immutable validation release are complete. This status does not block visual design; it blocks commercial activation.

## Exit criterion

The project is ready to enter GUI design when all of the following are true:

- headless preview/unlock/dossier APIs exist;
- project cost, requested funding and duration are distinct typed inputs;
- source reuse governance is fail-closed;
- source freshness/invalidation is fail-closed;
- paid unlock and dossier generation require exact commercial validation release binding;
- the browser/server boundary does not perform readiness calculations;
- CI is green.

These conditions are now the technical prerequisite for visual design. A separate `RELEASED` bando remains mandatory before production checkout or paid dossier activation.
