# ProcRun classification-engine product-validation release gate

Status date: 2026-09-09
Status: **AUTHORITATIVE HARD RELEASE GATE — NOT YET GREEN**

This document governs empirical product validation of ProcRun's classification engine only. It does
not govern web, billing, authentication or other customer-application work.

The validated chain is:

`FundingProject -> PurchaseComponent -> ProcurementEvidence -> ComponentState -> ProjectState`

The purpose is not merely to prove that code implements frozen rules. The purpose is to prove, on
real production-like projects, that the engine's classifications are empirically correct,
conservative, reproducible and commercially defensible.

## 1. Frozen state contract

Component states:

- `OPEN`
- `CLOSED`
- `UNRESOLVED`

Project aggregation:

- all components `OPEN` -> `OPEN`
- all components `CLOSED` -> `CLOSED`
- fully resolved mixture of `OPEN` and `CLOSED` -> `PARTIAL`
- any `UNRESOLVED` -> `UNRESOLVED`
- no defensibly classified component -> `UNRESOLVED`

`OPEN` means exactly:

> **No relevant procurement found in TED as of DATE.**

It never means proven absence outside TED.

`CLOSED` requires accepted pre-cutoff procurement evidence that actually covers the concrete
component. Ambiguity, incomplete coverage or review-band evidence must not be converted to OPEN.

False OPEN is the highest-cost classification error.

## 2. Independence and blind gold-standard rule

No engine output may be used as the answer key for the same case.

A separate gold standard must be frozen before release-gate scoring. For each case it records:

- project identity and frozen cutoff date;
- independently adjudicated purchasable components;
- exact project-scope evidence spans;
- relevant and explicitly rejected procurement evidence;
- effective procurement dates and pre/post-cutoff status;
- expected component states;
- expected project state;
- written rationale sufficient for later audit.

The adjudication may use only already-public, independently inspectable material and must remain
entirely inside ProcRun's permanent no-human-response validation boundary.

If engine output must be used mechanically to retrieve candidate notices, the final gold decision
must still be made independently and documented before scoring.

Gold-standard corrections are allowed only when the gold record itself is demonstrably wrong. Every
correction must be versioned, explained and hash-anchored. A correction must never be made merely to
improve engine scores.

## 3. Benchmark population

Final product acceptance requires at least **200 real funded projects**, or the entire qualifying
production universe if fewer than 200 exist.

The benchmark must be stratified across:

- every supported component domain;
- short and long scope descriptions;
- one-component and multi-component projects;
- projects with known procurement;
- projects for which no relevant TED procurement was found;
- ambiguous candidate matches;
- expected `UNRESOLVED` cases;
- multiple geographies, project sizes and time periods;
- high-precision and low-precision project descriptions.

Convenience sampling of only easy cases is prohibited.

At least 25% of the general benchmark must be a disjoint holdout that is not used for rule tuning.
Final general accuracy metrics are judged on this holdout.

## 4. Dedicated OPEN safety population

The 25% general holdout is **not sufficient by itself** to validate a zero-false-OPEN claim.

For the false-OPEN safety test, the engine must additionally be evaluated against a dedicated OPEN
population consisting of **all available projects that the release-candidate engine classifies OPEN
within the frozen production-validation universe**.

The release report must record:

- number of OPEN-classified projects in that universe;
- number independently adjudicated;
- whether the OPEN population is complete;
- false-OPEN count;
- observed false-OPEN rate; and
- the one-sided 95% binomial upper confidence bound for the underlying false-OPEN probability.

The statistical bound is diagnostic; it does not weaken the release rule. Product acceptance still
requires zero observed false OPEN and complete adjudication of the dedicated OPEN population.

If the candidate engine produces no OPEN cases, the OPEN gate is not failed, but the report must state
that no empirical positive-OPEN claim was validated for that release candidate.

## 5. Primary release metrics

### 5.1 False OPEN

A false OPEN occurs when the engine returns `OPEN` while the gold standard is `CLOSED` or
`UNRESOLVED`.

Release requirement:

- dedicated OPEN population complete;
- **false OPEN count = 0**;
- **observed false OPEN rate = 0.0%**.

Any false OPEN is a Critical failure and forces `NO-GO`.

### 5.2 False CLOSED

A false CLOSED occurs when the engine returns `CLOSED` while gold is `OPEN` or `UNRESOLVED`.

Holdout requirement:

- **false CLOSED rate <= 1.0%**.

A CLOSED result caused by semantic similarity alone, wrong-project evidence or invalid/missing exact
source evidence is a Critical failure regardless of aggregate rate.

### 5.3 Project-state exact accuracy

Holdout requirement:

- **>= 95% exact ProjectState accuracy**.

High aggregate accuracy never compensates for a false OPEN.

### 5.4 Component-state exact accuracy

Holdout requirement:

- **>= 95% exact ComponentState accuracy**.

## 6. Component extraction quality

The classifier cannot be validated independently of component extraction.

Release requirements:

- component recall **>= 95%**;
- component precision **>= 98%**;
- exact/verbatim project source-span validity **= 100%**.

A missed component that can produce an incorrect project state is Critical. An invented unsupported
component that changes project state is Critical.

## 7. Procurement-match quality

For notices used to establish CLOSED:

- accepted-match precision on holdout **= 100%**;
- review-band evidence must never create OPEN;
- semantic similarity alone must never create CLOSED;
- cross-project contamination that changes state must be **0**.

The benchmark must explicitly include look-alike projects, shared authorities, shared geographies,
shared CPV codes and same-category projects running concurrently.

## 8. Historical cutoff integrity

Post-cutoff procurement evidence must never rewrite a historical pre-cutoff state to CLOSED.

Requirement:

- cutoff integrity **= 100%**.

## 9. Coverage integrity

OPEN is allowed only with complete required procurement-source coverage and a resolved component
boundary.

Tests must include incomplete pagination, incomplete required-source sets, interrupted retrieval and
unresolved component boundaries.

Every such case must yield `UNRESOLVED`.

Requirement:

- coverage fail-closed behaviour **= 100%**.

## 10. Adversarial suite

The frozen adversarial suite must cover at minimum:

1. nearly identical project names;
2. same municipality/region;
3. same contracting authority;
4. same CPV but different actual scope;
5. broad generic project text;
6. extremely short project text;
7. one project split across many procurements;
8. only one of several components procured;
9. procurement after cutoff;
10. temporally incompatible procurement;
11. generic notice descriptions;
12. same location but wrong project;
13. same component type in concurrent projects;
14. missing or wrong project reference;
15. semantic similarity only;
16. CPV overlap only;
17. incomplete pagination;
18. duplicate notices;
19. correction/change notices;
20. missing or inconsistent evidence spans.

No adversarial case may produce a known false OPEN or invalid CLOSED.

## 11. Determinism

For frozen inputs and identical engine/rule versions, the benchmark must be run at least three times.
The following must be identical:

- component IDs;
- component states;
- project states;
- accepted evidence IDs;
- rule versions;
- content hashes.

Requirement:

- **100% deterministic output**.

## 12. Persistent false-OPEN consequence plan

Zero tolerance is a product-safety rule, not a target that may be silently relaxed under launch
pressure.

If a false OPEN is traced to a specific rule, rule combination, category mapping, match tier or
boundary assumption, that mechanism must be changed to fail closed before another release attempt.

If the **same causal mechanism** produces a false OPEN in two separately frozen evaluation rounds,
the implicated mechanism must be **retired from OPEN-producing use**. Its affected cases must resolve
to `UNRESOLVED` unless and until a new explicitly versioned mechanism is supported by independent new
evidence and passes a fresh pre-frozen validation round.

This retirement is not a temporary benchmark patch. Re-enabling the mechanism requires:

1. a new rule/version identifier;
2. an explicit written causal analysis;
3. new independently frozen cases targeting the failure mechanism;
4. zero false OPEN on those cases and the complete dedicated OPEN population; and
5. normal regression-gate approval.

The release gate itself must never be weakened because zero false OPEN proves difficult to achieve.
Output volume is sacrificed before the safety threshold.

## 13. Error taxonomy and severity

Every mismatch must be classified as one of:

- `MISSED_COMPONENT`
- `INVENTED_COMPONENT`
- `WRONG_PROJECT_MATCH`
- `WRONG_COMPONENT_MATCH`
- `FALSE_OPEN`
- `FALSE_CLOSED`
- `WRONG_PARTIAL`
- `WRONG_UNRESOLVED`
- `CUTOFF_LEAK`
- `INCOMPLETE_COVERAGE_OPEN`
- `INVALID_EVIDENCE_SPAN`
- `POST_CUTOFF_CLOSE`
- `CROSS_PROJECT_CONTAMINATION`
- `NONDETERMINISM`
- `GOLD_STANDARD_ERROR`

Critical failures include any false OPEN, state-changing wrong-project match, CLOSED without valid
accepted evidence, post-cutoff leakage, OPEN under incomplete coverage, state-changing invented
component or nondeterministic state.

Final GO permits **0 Critical failures**.

## 14. Hard release gate versus continuous quality dashboard

This document is the **only hard pass/fail gate for empirical correctness of the final classification
engine**.

Broader component-quality measures from earlier component/model benchmark work remain useful but are
not competing launch gates. Measures such as wrong-domain rate, duplicate rate, over-specificity,
minimal-phrase exactness, fallback-model latency and similar diagnostics belong to a **continuous
quality dashboard** unless this document explicitly promotes one into a hard threshold.

Those dashboard metrics must still be reported and improved. They do not independently authorize or
block release unless they cause a hard-gate failure defined here.

`docs/MODEL_BENCHMARK.md` remains authoritative only for the local-model fallback benchmark. It does
not establish final procurement-state correctness.

## 15. Regression gate

After first successful product validation, this benchmark becomes a permanent regression gate for any
change to:

- component taxonomy;
- extraction rules;
- matching rules;
- coverage logic;
- cutoff logic;
- project aggregation;
- evidence handling.

A changed engine version may pass only when:

1. zero false OPEN remains true;
2. no existing Critical case regresses;
3. all other hard thresholds pass; and
4. every changed classification is explicitly accounted for.

## 16. Required benchmark report

Every full run must emit machine-readable and human-readable reports containing at least:

- benchmark version;
- engine/rule versions;
- Git commit;
- input dataset hash;
- gold-standard hash;
- number of projects and components;
- state confusion matrices;
- false OPEN count/rate;
- dedicated OPEN population completeness and size;
- one-sided 95% false-OPEN upper confidence bound;
- false CLOSED count/rate;
- exact project-state accuracy;
- exact component-state accuracy;
- component precision/recall;
- accepted CLOSED-match precision;
- unresolved rate;
- cutoff and coverage integrity;
- results by domain, geography and text-length band;
- every mismatch with error taxonomy/severity;
- separate general-holdout result;
- active retired OPEN-producing mechanisms;
- final `GO`, `NO-GO` or `CONDITIONAL — REMEDIATION REQUIRED` decision.

## 17. Freeze requirements

Before a release-candidate result is inspected, freeze and hash:

- benchmark project IDs;
- cutoff dates;
- gold components and evidence;
- gold component/project states;
- metric definitions;
- acceptance thresholds;
- error taxonomy;
- adversarial cases;
- dedicated OPEN-population definition.

The frozen package hash must be committed before release-gate scoring.

## 18. Product acceptance

The classification engine may be declared:

**PRODUCT VALIDATED — CLASSIFICATION ENGINE: GO**

only when all of the following hold:

- >= 200 real projects, or the entire qualifying universe if smaller;
- disjoint >= 25% general holdout;
- complete dedicated OPEN safety population;
- 0 Critical errors;
- false OPEN = 0%;
- false CLOSED <= 1%;
- ProjectState accuracy >= 95%;
- ComponentState accuracy >= 95%;
- component recall >= 95%;
- component precision >= 98%;
- accepted CLOSED-match precision = 100% on holdout;
- cutoff integrity = 100%;
- coverage fail-closed = 100%;
- determinism = 100%;
- adversarial suite has no Critical failure;
- benchmark/gold standard are frozen, versioned and hash-anchored; and
- the benchmark is installed as a permanent regression gate.

Until those conditions are demonstrated, the only valid status is:

**CLASSIFICATION ENGINE PRODUCT VALIDATION: NOT YET GREEN**

Implementation completeness, green unit tests or successful production ingestion do not override
this empirical release gate.

## 19. Priority order

Future classification work must optimize in this order:

1. prevent false OPEN;
2. prevent false CLOSED;
3. maximize correctly resolved output;
4. reduce `UNRESOLVED` only when doing so does not weaken 1 or 2.

More output is never a quality objective by itself. A conservative `UNRESOLVED` is preferable to an
unsupported commercial conclusion.
