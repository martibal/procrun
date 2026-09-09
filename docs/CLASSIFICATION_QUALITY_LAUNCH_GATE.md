# ProcRun — classification quality launch gate

Status: **ACTIVE / CANONICAL PAID-LAUNCH GATE**

This document is the authoritative quality gate for customer-facing classification of outstanding procurement needs. It supersedes `docs/PHASE_M_MATCHING_VALIDATION.md` as the normative matching/classification launch specification.

This gate does **not** reopen source, rights, privacy or TED-scope approvals. It answers a different question: whether ProcRun's actual classification output is accurate enough that paying customers receive a high-precision product rather than a noisy keyword feed.

Core chain under test:

`funded project -> identified purchasing need -> TED evidence -> OPEN/CLOSED/UNRESOLVED -> what may still remain to buy`

## 1. Paid-launch rule

ProcRun must not open paid access until this gate is PASS.

PASS requires empirical validation against real Lombardia production records, with a frozen review corpus and reproducible scoring. Green unit tests, deterministic execution and technically correct fail-closed behaviour are necessary but not sufficient.

## 2. Benchmark corpus

The first benchmark must contain at least **300 reviewed classification units** drawn deterministically from real current ProcRun Lombardia production records within the already approved customer-safe/source-safe boundary.

The sample must be stratified across active domains/categories and OPEN/CLOSED/UNRESOLVED states as far as the available population permits. It must deliberately include known ambiguity classes such as generic monitoring, automation/control, photovoltaic, electrical and civil-works language.

If the current production population cannot supply 300 eligible units, the gate remains NOT PASS. The sample-size threshold must not be reduced to manufacture a pass.

Synthetic fixtures may support regression testing but cannot substitute for the empirical production benchmark.

## 3. Human reference truth

Each benchmark unit must contain an explicit reference judgement for at least:

- `need_present`: yes/no
- `correct_need_category`
- `correct_sector_or_null`
- `correct_state`: OPEN/CLOSED/UNRESOLVED
- `evidence_sufficient`: yes/no
- `duplicate`: yes/no
- `over_specific`: yes/no

Uncertain evidence must be judged conservatively. Review uncertainty is not to be forced into a confident category merely to make scoring easier.

### 3.1 OPEN must be judged as two independent propositions

For a customer-facing OPEN result to be correct, both must hold:

A. the purchasing need itself is supported by project evidence; and
B. no matching procurement has been found in the complete declared TED query universe through the recorded cutoff.

A correct TED-negative search does not rescue a wrongly identified need.

### 3.2 CLOSED evidence standard

CLOSED requires procurement evidence that can be tied to the identified component. Same-project presence, broad sector similarity or a broadly related CPV code is not sufficient by itself.

### 3.3 Reference-truth reliability / independent double review

The benchmark truth must itself be validated before it is used as a launch metric.

At least **30 of the first 300 units** must be reviewed independently a second time. The second review must be completed without access to the first verdict.

Agreement must be measured separately for:

- need present
- category
- sector
- state
- evidence sufficiency

Minimum raw agreement for each scored field is **90%** on the double-reviewed subset. Cohen's kappa should also be reported where the field structure makes it meaningful.

If agreement is below the threshold, the reference definitions or review protocol must be clarified and the affected units re-reviewed before the benchmark is frozen. This is a benchmark-quality failure, not automatically a model/classifier failure.

The no-contact rule remains unchanged: no source owner, authority, customer or external paid reviewer may be contacted to close this gate. Review uses already-public evidence and internal inspection only.

## 4. Required metrics

The benchmark report must calculate at least:

- overall component precision
- recall where the review design establishes discoverable missed needs
- OPEN opportunity precision
- CLOSED precision
- UNRESOLVED precision
- state confusion matrix
- false-positive rate
- wrong-domain rate
- over-specificity rate
- duplicate rate
- per-category precision and n
- inter-rater raw agreement and, where applicable, kappa

## 5. Precision-first product rule

False positives are more damaging than conservative abstention. ProcRun must prefer less output over unsupported output.

Therefore:

- generic terms must not by themselves establish a sector-specific need;
- weakly supported needs should be made more generic, withheld or left unresolved;
- insufficient procurement evidence must not be promoted to CLOSED;
- incomplete or ambiguous state evidence must fail closed to UNRESOLVED;
- recall must not be improved by materially degrading precision.

## 6. Generic need and sector context are separate claims

The classification model must treat these as independent concepts:

- what is being bought
- sector context
- functional role

Generic terms such as monitoring, automation, photovoltaic, electrical and civil works must not establish a sector merely because the corresponding rule is stored under that domain.

Where the current taxonomy cannot represent a safe generic classification, the system must abstain/fail closed rather than emit an unsupported sector-specific customer classification.

### 6.1 Mandatory existing ambiguity regression cases

The current taxonomy contains real cross-domain ambiguity and these cases are mandatory benchmark/golden-corpus tests.

At minimum:

- generic `monitoring` alone must not establish `water_wastewater`;
- generic `monitoring` alone must not establish `ports_coastal`;
- generic `automation` / `control system` alone must not establish `water_wastewater`;
- generic `photovoltaic` alone must not establish `ports_coastal` when no port/coastal context is evidenced;
- a phrase shared by multiple active domains must not create duplicate sector-specific opportunities from the same unsupported signal.

This requirement is deliberately stronger than deterministic extraction. Repeating the same ambiguous error deterministically is still an error.

## 7. Error taxonomy

Every benchmark error must be assigned to a root-cause class. Minimum classes:

- generic phrase caused wrong sector
- phrase too broad
- missing context requirement
- duplicate extraction
- incorrect CPV association
- incorrect project-domain assignment
- incorrect TED matching
- incorrect OPEN/CLOSED decision
- insufficient evidence treated as certain
- taxonomy overlap

The report must show count, share of all errors, affected categories and affected rules.

Remediation order follows measured error contribution, not subjective taxonomy preference.

## 8. Locked launch thresholds

The following thresholds are locked for this launch gate:

- reviewed benchmark units: **n >= 300**
- overall component precision: **>= 95%**
- customer-facing OPEN precision: **>= 95%**
- wrong-domain rate: **<= 2%**
- customer-facing duplicate rate: **<= 1%**
- any individually validated customer-facing category with `n >= 20`: **precision >= 90%**
- independent double-review subset: **n >= 30**
- raw inter-rater agreement per scored field: **>= 90%**

Categories with `n < 20` are marked `INSUFFICIENT_BENCHMARK_SAMPLE` and may not be represented as independently validated categories.

The thresholds must not be reduced after results are seen.

## 9. Iterative validation is expected

The first run is a baseline, not an assumed PASS.

Expected sequence:

`benchmark v0 -> error analysis -> taxonomy/matching fixes -> benchmark v1 -> regression analysis -> further remediation -> final benchmark`

Plan for at least **two complete re-evaluations after baseline** if the locked thresholds are not already met. A failed run is retained for traceability and creates a remediation cycle; it does not terminate ProcRun and it does not justify threshold reduction.

No failed run may be hidden, deleted or replaced by a more favourable post-hoc metric.

## 10. Golden regression corpus

After adjudication, at least **100 representative benchmark units** must be frozen as a permanent golden regression corpus.

It must include:

- prior false positives
- wrong-domain cases
- over-specific cases
- duplicate cases
- OPEN/CLOSED/UNRESOLVED boundary cases
- negative generic-term cases from section 6.1

Changes affecting component extraction, taxonomy, domain logic, TED matching, state classification, deduplication or customer-safe opportunity generation must run this corpus in CI.

CI must fail on a forbidden-classification regression, state regression or duplicate regression.

## 11. Determinism and manifest

Every scored run must record at least:

- benchmark version and seed
- source/TED cutoff
- taxonomy/component-rule version
- matching/state rule version
- customer read-model/policy version where applicable
- code revision
- sample size and category/state distribution
- output/report hash

Same frozen inputs and versions must produce the same system output.

Determinism and correctness are separate gates; both are required.

## 12. Benchmark report

Before paid launch, repository evidence must contain a reproducible report with at least:

- benchmark version
- code revision
- taxonomy version
- sample size
- overall precision
- recall where measurable
- OPEN/CLOSED/UNRESOLVED precision
- state confusion matrix
- wrong-domain rate
- over-specificity rate
- false-positive rate
- duplicate rate
- per-category precision and n
- inter-rater agreement
- known remaining weaknesses
- root-cause error matrix
- PASS/NOT PASS against every locked threshold

## 13. Definition of Done

This gate is PASS only when all of the following are true:

- at least 300 real production classification units have completed reference review;
- benchmark truth has passed the independent double-review reliability gate;
- all active main categories are represented where production population permits;
- overall component precision is at least 95%;
- OPEN precision is at least 95%;
- wrong-domain rate is at most 2%;
- duplicate rate is at most 1%;
- no customer-facing category with n >= 20 has precision below 90%;
- generic signals cannot create unsupported sector-specific customer classifications;
- the known monitoring/automation/photovoltaic ambiguity classes are closed;
- OPEN is validated as both correct need identification and correct TED-negative conclusion;
- CLOSED requires component-relevant procurement evidence;
- UNRESOLVED remains a valid conservative outcome;
- at least 100 adjudicated cases are frozen in the golden regression corpus;
- relevant CI changes execute the golden corpus;
- the final benchmark has been rerun after the last classification-affecting change;
- the final report and manifest are committed and reproducible;
- no known severe classification defect remains open.

## 14. Governing product principle

**ProcRun does not try to publish the largest possible number of opportunities. It publishes the opportunities for which the available evidence is strong enough to support the claim being made.**

That principle governs taxonomy specificity, matching, state classification and launch acceptance.