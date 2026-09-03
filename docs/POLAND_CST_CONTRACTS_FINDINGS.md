# Poland CST 2021 implementation-contract report findings

Status date: 2026-09-03.

This note evaluates the current national Portal Funduszy Europejskich report `Stan wdrażania Funduszy Europejskich w Polsce w latach 2021-2027 - Lista umów z miejscami realizacji` as another Poland source family. It does not approve a ProcRun source and does not change `SOURCE_CONTRACTS`.

## Official publication

The current national report is produced by the institution coordinating the Partnership Agreement from data collected in the Centralny System Teleinformatyczny CST 2021. The official page describes it as a list of signed implementation agreements with basic amounts.

The official description states that each agreement is characterised, among other things, by:

- implementation level;
- place of implementation;
- beneficiary;
- beneficiary address data;
- policy objective;
- intervention scope;
- basic financial amounts.

The current page is dated 2026-09-01 and states data through 2026-08-31.

## Gate decision

This route fails independently on both privacy transport and project-scope suitability.

### Pre-receipt privacy

The official publication explicitly says the report contains the beneficiary and beneficiary address data. ProcRun may not receive a broad report and discard those columns afterwards.

No authoritative field-bounded transport contract for this report was established during this review.

### Scope

The official description identifies policy objective and intervention scope, but does not establish a project-specific free-text description equivalent to the `Opis projektu` field in the national SL2021 project list. Policy/intervention classifications are useful context, but they are not a substitute for sufficiently rich project-specific scope from which exact component evidence spans can be supported.

Accordingly, even a future safe projection of the described fields would not by itself satisfy ProcRun's scope requirement.

## Final gate

- current 2021-2027 national coverage: **PASS**;
- source provenance: **PASS / CST 2021 national implementation reporting**;
- broad-report zero-PII safety: **FAIL** because beneficiary and beneficiary address data are explicitly included;
- authoritative pre-receipt field projection: **NOT ESTABLISHED**;
- sufficiently rich project-specific scope: **FAIL / NOT ESTABLISHED by the official report description**;
- download-then-filter: **PROHIBITED**;
- report/file row smoke test: **PROHIBITED**;
- production eligibility: **REJECTED**.

No report body or project/agreement row was fetched.

## Reopen conditions

Do not reopen this route unless authoritative documentation establishes both:

1. field-bounded transport that excludes beneficiary and address data before receipt; and
2. a sufficiently rich project-specific scope field on that safe surface, with its own pre-publication zero-PII guarantee.
