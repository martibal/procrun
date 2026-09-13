# Readiness Dossier commercial validation gate

**Status: mandatory before any bando may be sold.**

This gate exists because green CI, deterministic code and unit tests prove only that ProcRun executes
its implementation consistently. They do not prove that the implemented customer-facing analysis is
factually and semantically correct for a real funding call.

## Absolute launch invariant

ProcRun SHALL NOT require validation, approval or confirmation from any person or organisation outside
the project before commercial launch. External means outside the project: source owners, authorities,
consultants, lawyers, advisers, reviewers or any other third party whose response would be needed before
ProcRun may proceed.

The founder's own source reading, structured extraction, coding and validation work is part of the
project build process and is not prohibited external validation.

Commercial release is permitted only when every automated customer-facing claim can be validated from
publicly available, independently inspectable evidence and deterministic computation. Any requirement
whose correct application depends on interpretation, discretion, unstated context, external verification
or professional judgment MUST remain non-automated and surface as professional verification required.

**Ambiguity is not a validation problem to be solved. Ambiguity is a reason not to automate the claim.**

## Meaning of "100% validated"

"100% validated" means 100% of ProcRun's automated claims fall inside this validation contract. It does
not mean ProcRun claims to understand or decide the complete legal universe of a funding call.

## Claim categories

1. `MACHINE_VERIFIABLE_FACT`: an explicit fact whose value and applicability can be verified directly
   from the frozen public source.
2. `EXPLICIT_SCOPED_FACT`: an explicit fact whose scope/condition is also represented structurally and
   can be verified directly from the frozen public source.
3. `PROFESSIONAL_VERIFICATION_REQUIRED`: any item requiring interpretation, discretion or context that
   cannot be proven under categories 1 or 2. ProcRun never turns this category into an automated verdict.

## Independent reconstruction requirement

Automated claims require a second reconstruction path that is blind to the first extraction. The second
pass must be performed without seeing the first extracted value/rule and must use a procedurally distinct
method where practical, for example structured keyword/citation search against the frozen source rather
than repeating the same close reading.

A second reading that merely confirms a visible first extraction does not count as independent evidence.
The validation record must state the reconstruction method and attest that it was blind to the first
extraction.

## Per-bando release requirements

Before a bando becomes sellable, the exact source package and benchmark snapshot must have one immutable
`RELEASED` validation record. That record must attest all of the following:

- source universe completeness for the supported claim set;
- ambiguity rule respected: ambiguous claims are not automated;
- benchmark cohort membership is explicit and verified against its qualified source;
- dossier semantics do not communicate stronger conclusions than the evidence supports;
- adversarial end-to-end suite passed;
- every automated validation case passed exactly;
- no external validation dependency exists;
- the release is explicitly acknowledged as founder/project validation rather than independent external
  legal/professional review.

The validation release binds:

- exact bando code;
- exact source package ID and SHA-256;
- exact benchmark snapshot ID and SHA-256;
- validation manifest and SHA-256;
- validation timestamp;
- every golden/adversarial case and reconstruction method.

Any new source-package version or benchmark snapshot is a new combination and has no inherited release.
It must obtain a new validation release before paid analysis resumes.

## Commercial fail-closed rule

Paid unlock and paid dossier creation MUST fail if the exact source-package/snapshot combination has no
matching immutable `RELEASED` validation record. A web page, checkout configuration, API route or other
presentation layer may never override this gate.

## Launch strategy

ProcRun is explicitly a quality-over-breadth product. Initial launch SHALL use **one fully validated
bando only**. Do not validate several launch bandi in parallel merely to increase catalogue breadth.

Sequence:

1. implement/freeze validation architecture;
2. select one launch bando;
3. build the complete frozen source package and benchmark binding;
4. classify every supported claim into the validation contract;
5. perform blind independent reconstruction for every automated claim;
6. run boundary and adversarial end-to-end golden cases;
7. create the immutable commercial validation release;
8. only then proceed to customer GUI/checkout for that bando;
9. learn from real use before deciding whether a second bando is operationally defensible.

## Accepted limitation

The source interpretation and validation are performed inside the project and are not independently
cross-verified by an external human reviewer. This is an explicit accepted constraint, not something
hidden by the validation terminology. The product compensates by sharply limiting automation to claims
that can be supported from public evidence, using blind internal reconstruction, deterministic tests and
fail-closed treatment of ambiguity.
