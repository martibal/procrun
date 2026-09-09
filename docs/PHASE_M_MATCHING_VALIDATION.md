# ProcRun Phase M — empirical validation of the matching engine

Status: **SUPERSEDED / HISTORICAL ONLY**

This specification is no longer normative.

It has been replaced by:

`docs/CLASSIFICATION_QUALITY_LAUNCH_GATE.md`

The replacement is the sole active paid-launch quality gate for component classification, procurement matching and OPEN/CLOSED/UNRESOLVED accuracy. It introduces the stricter production benchmark, 95% precision thresholds, explicit need-vs-TED validation for OPEN, wrong-domain/duplicate limits, independent double review of benchmark truth, and the golden regression corpus.

The historical Phase M thresholds (`90%`, `n >= 30` per OPEN/CLOSED group) must not be used as an alternative launch criterion.

Existing Phase M scripts, review files and `docs/MATCHING_QUALITY_REPORT.md` remain retained for traceability and may be used as historical evidence or implementation inputs, but they cannot override the canonical classification quality launch gate.

No prior Phase M result grandfathers a later taxonomy, matching-rule or state-rule version.