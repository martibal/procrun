# ProcRun source status

Status date: 2026-09-03
Canonical product spec: `docs/PRODUCT_FOUNDATION_FINAL.md`
Authoritative readiness gate: `docs/BUILD_GATES.md` A20

## Production rule

Every live source must be registered in `procrun.source_contracts` and pass `require_live_source()` before network retrieval. A route is usable only when RIGHTS, ACCESS and DATA SAFETY are all APPROVED. Public availability alone is insufficient.

## Current canonical architecture

ProcRun is again funded-project first. TED is procurement evidence/market context, not the discovery object.

`funded project -> purchasable components -> procurement evidence -> conservative state -> remaining runway`

## Current source registry decision

| Source | Overall | Rights | Access | Data safety | Role |
| --- | --- | --- | --- | --- | --- |
| TED Search API | APPROVED | APPROVED | APPROVED | APPROVED | Procurement evidence + market context |
| PRR Projects on dados.gov.pt | CONDITIONAL | APPROVED basis | APPROVED basis | CONDITIONAL | Preferred funded-project candidate; live collector disabled |
| Mais Transparência project detail HTML | BLOCKED | CONDITIONAL | CONDITIONAL | BLOCKED | Human research only; contains beneficiary surface |
| PT2030 operations bulk workbook | BLOCKED | CONDITIONAL | APPROVED | BLOCKED | Broad file; no download-then-filter |
| Portal BASE / APIBase2 | BLOCKED | CONDITIONAL | CONDITIONAL | BLOCKED | No production calls |

## PRR Projects evidence already established

Official dados.gov.pt terms state that datasets published on the portal may not contain personal data and that State datasets use CC BY 4.0 by default unless otherwise specified. The PRR publisher exposes Projects separately from Entities and the project dataset is described as daily/current open data.

That is strong evidence for the preferred source route, but ProcRun's absolute policy is stricter than ordinary portal/GDPR compliance. The terms also contemplate legally permitted publication of personal data, and the project dataset page does not provide a source-specific machine schema/free-text guarantee proving that every retained field can never contain a natural-person identifier before receipt.

Therefore PRR Projects remains **CONDITIONAL, not APPROVED**, until one of the following is obtained from an authoritative source:

1. a documented machine endpoint with a frozen output schema plus explicit pre-publication exclusion/redaction guarantee for all retained text fields; or
2. an explicit source-owner statement that the exact Projects distribution/endpoint contains no natural-person data, including project-title/summary text, before publication.

No row/file probe may be used as a substitute for that guarantee.

## TED production contract

TED Search API remains approved with explicit server-side field projection, bounded pagination, schema validation and no prohibited buyer/contact/supplier-person fields. Phase 0 source qualification supports active infrastructure procurement and historical market context. Phase 0B/0C failures remain failures of the retired TED-only supplier-demand product.

## Zero-PII rule

> **Do not receive a broad response containing prohibited fields and discard them afterwards.**

No natural-person data may enter the intelligence plane. Account/billing/support PII is a separate control plane and is not an exception.

## Activation procedure

Changing a funded-project source from CONDITIONAL to APPROVED requires all of the following in one reviewed change:

- authoritative rights citation;
- authoritative automated-access citation;
- authoritative exact data-safety citation;
- frozen route/schema/field allowlist;
- fail-closed collector tests;
- review-expiry date;
- updated A1/A20 state;
- green CI.

Until then, build the downstream production pipeline against the canonical FundingProject interface and fixtures, but do not enable live funded-project retrieval.
