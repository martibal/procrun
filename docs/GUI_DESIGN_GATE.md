# ProcRun GUI design gate

Status: **DESIGN READY ONLY WHEN TECHNICAL + LEGAL HARDENING CI IS GREEN / COMMERCIAL RELEASE STILL FAIL-CLOSED**

## Purpose

This gate separates **visual design work** from **commercial activation** without allowing the GUI to invent weaker legal, privacy, source-reuse or correctness semantics.

The Readiness backend contract is sufficiently frozen to design the customer interface. GUI design may proceed against the headless API and domain contracts in `main` only after `docs/LEGAL_HARDENING_GATE.md` and its regression tests are green.

This does **not** release a bando, enable paid analysis, enable checkout, or permit a dossier to be generated without an exact immutable commercial validation release.

## Frozen product surfaces for GUI design

The GUI must be designed around exactly these three server-side Readiness surfaces:

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

## Legal and source-reuse boundary

Visual components must preserve the source contract, not merely the data shape:

- verbatim source wording may be rendered only where commercial republication is permitted;
- `FACT_EXTRACTION_ONLY` Readiness documents render structured facts, citation and official link, never protected wording;
- source attribution must remain visible and source-specific;
- ProcRun must never imply endorsement by TED, EU institutions, OpenCoesione, Regione Lombardia or another source publisher;
- the customer intelligence plane must not receive natural-person identity/contact fields;
- ProcRun is designed as a B2B/professional service; consumer checkout is not part of the launch contract.

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

In addition, commercial checkout must remain closed until `commercialCheckoutReady()` has all mandatory merchant disclosures. Absence of legal name, geographic address, electronic contact route, organisation/register information or VAT status is a hard commercial block, not a design placeholder to be guessed.

The first launch bando `RLO12026055023` remains **validation-in-progress** until its exact source package, benchmark snapshot, blind reconstruction, adversarial cases and immutable validation release are complete. This status does not block visual design; it blocks commercial activation.

## Exit criterion

The project is ready to enter GUI design when all of the following are true:

- headless preview/unlock/dossier APIs exist;
- project cost, requested funding and duration are distinct typed inputs;
- source reuse governance is fail-closed;
- legal hardening gate is present and tested;
- OpenCoesione identity fields remain outside FundingProject/read model/customer exports under the frozen legal-person publication contract;
- source attribution metadata exists for TED and OpenCoesione;
- marketing copy does not promise universal verbatim wording;
- merchant disclosures are fail-closed rather than fabricated;
- source freshness/invalidation is fail-closed;
- paid unlock and dossier generation require exact commercial validation release binding;
- the browser/server boundary does not perform readiness calculations;
- CI is green.

When these conditions are green, there is no remaining legal/technical prerequisite to **visual GUI design**. A separate `RELEASED` bando and complete merchant/control-plane configuration remain mandatory before production checkout or paid dossier activation.
