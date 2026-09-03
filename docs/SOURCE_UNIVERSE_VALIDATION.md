# Funded-project source-universe validation gate

Status: **BLOCKING WEB BUILD**

## Non-transfer rule

Source compliance and product-mechanism validation are separate gates. A funded-project source may be
legally and technically safe yet still be unsuitable for the ProcRun product mechanism. No source
family inherits Phase-0 evidence from another source family merely because the normalized schema looks
similar.

The corrected Phase-0 v1.1 result validated a preregistered Portugal 2030 public-infrastructure /
equipment / engineering wedge. Its 30-project primary cohort produced 18 CLOSED, 6 OPEN, 4 PARTIAL and
2 UNRESOLVED cases, and retained its development-GO verdict after the PACS-FC-04022300 correction.
That result remains valid for the universe it tested.

It did **not** validate PRR Projects as a production source universe.

## Current source-family status

| Source family | Compliance | Mechanism validation | Product ready |
| --- | --- | --- | --- |
| Portugal 2030 project search/detail family | not production-approved | VALIDATED for the frozen Phase-0 wedge | NO |
| PRR Projects / dados.gov.pt | CONDITIONAL | NOT VALIDATED | NO |

The result is intentional: today there is no funded-project source that is simultaneously safe for
live ingestion and validated for the commercial mechanism.

## PRR confirmation gate

If PRR Projects becomes A1-approved, it must then pass a preregistered source-transfer confirmation
before it can power the paid runway product. That confirmation must be run only on the exact approved
PRR field surface; no broader download is permitted for evaluation.

Before looking at outcomes, freeze at minimum:

- deterministic population and sampling rule from the approved PRR Projects universe;
- infrastructure/product domains included;
- minimum sample size;
- exact component-extraction version;
- exact required procurement-source coverage boundary;
- state/outcome rules;
- false-OPEN treatment;
- thresholds for resolved share, suppression value and retained OPEN/PARTIAL value;
- an explicit rule that failure cannot be repaired by replacing the sample or lowering thresholds.

The confirmation is a source-transfer test, not a re-run of TED Phase 0B/0C and not a licence to change
the canonical product mechanism after seeing the data.

## Code enforcement

`src/procrun/source_validation.py` keeps the product-validation registry separate from
`src/procrun/source_contracts.py`. Production funded-project activation must pass both
`require_live_source()` and `require_validated_funded_source()`, or use the combined
`require_product_ready_funded_source()` gate.

A future code change that promotes PRR source compliance to APPROVED without separately updating the
mechanism-validation evidence must therefore remain fail-closed.
