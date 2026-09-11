# ProcRun Phase R — recall preregistration

Status: FROZEN BEFORE TASK A MEASUREMENT
Date: 2026-09-11

## Frozen baseline

- Corpus: PR FESR Lombardia 2021-2027 customer corpus
- Logical projects: **4,305**
- Classified projects under the current evidence-bounded production semantics: **116**
- Baseline recall: **2.7%**

This baseline is not adjusted after any Phase R result.

## Frozen target

At least **40%** of the same 4,305-project corpus must receive either:

1. **Full evidence** — project-text phrase evidence plus a compatible structured signal; or
2. **Structured only** — a compatible approved structured classification signal without project-text phrase confirmation.

Structured-only classification is never OPEN or CLOSED and is never represented as full evidence.

## Sequential measurement contract

Task A is measured first, in isolation, before any phrase expansion or morphological normalisation is introduced. Task B source qualification may run in parallel because it does not change the corpus or matching rules. Tasks C and D must not be implemented until the Task A isolated measurement has been recorded.

For every task, report:

- total projects;
- baseline classified projects;
- newly classified projects attributable to that task alone;
- full-evidence count;
- structured-only count;
- unresolved count;
- percentage classified;
- source/resource hash and rule/mapping versions.

## Precision gate

Recall never overrides precision. Any task that demonstrably increases false positives is rejected even if recall improves. OPEN/CLOSED remains exact-evidence only. A structured-only suggestion can only state that an approved structured classification suggests a category; it cannot establish a purchasing need in project text and cannot establish procurement absence/presence.

## Permanent constraints

- zero PII in the intelligence plane;
- no human/source-owner contact;
- no download-then-filter as a safety mechanism;
- exact, traceable evidence for OPEN/CLOSED;
- new sources must pass the existing RIGHTS / ACCESS / DATA SAFETY process before receipt;
- no target reduction after results are known.
