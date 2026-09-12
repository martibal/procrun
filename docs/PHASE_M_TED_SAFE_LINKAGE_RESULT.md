# Phase M — M0-B TED safe structured CUP-linkage result

Date: 2026-09-12

Preregistration commit: `4f928bb0f6959f2a61f7da3b8be8c01571c6d33b`

Workflow run: `34685668395`

## Decision

**BLOCKED_NO_STRUCTURED_CUP_EVIDENCE**

The frozen zero-free-text qualification completed its transport and projection checks successfully, but the structured CUP linkage hypothesis was not evidenced in the preregistered sample.

Results:

- TED accepted `internal-identifier-proc = "{cup}"` on the first frozen syntax attempt.
- All six frozen structured projection fields were supported.
- No identity fields were received.
- No free-text fields were received.
- No `internal-identifier-proc` values were received; that field was used only as a server-side query predicate.
- No raw notices or CUP-to-notice outcome rows were persisted.
- Frozen sample size: 20 CUPs.
- CUPs with at least one TED result: 0.
- Aggregate TED matches: 0.

Under the preregistered decision rule, this blocks the exact TED structured-CUP route. It does **not** prove that these projects never procure or never appear in TED through some other representation.

## Consequence

ProcRun MUST NOT broaden this failed gate to `notice-title`, `description-proc`, buyer fields, organisation/contact data, full-text search, full notices, XML, HTML or PDF in order to recover linkage. Such a fallback would violate the frozen zero-PII pre-receipt boundary.

MOP remains a prospective project-source candidate, but TED is not currently qualified as the materialisation layer through exact structured CUP linkage. Any alternative materialisation source must pass its own independent RIGHTS / ACCESS / DATA SAFETY qualification before outcome testing.
