# ProcRun delivery-readiness gate

## Permanent sequencing rule

Web implementation is the final build phase, not a parallel workstream.

**No customer-facing web application work may start or continue until the entire product delivery chain is production-ready and all non-web delivery and release gates are green.**

The intended sequence is:

1. source contracts approved from public evidence only;
2. collectors implemented and fail-closed;
3. live source-transfer succeeds against real production sources;
4. canonical pipeline and customer-safe read model run end-to-end on live inputs;
5. coverage semantics, OPEN boundaries, exports and persistence are verified in production code;
6. regression, drift, schema, compliance and no-contact gates are green;
7. non-web commercial/control-plane/release controls are launch-ready;
8. only then: start the customer-facing web build.

The target state at web-build start is therefore: **the product is launch-ready except for the web interface itself**. Once the web build is finished and validated, no unresolved source, pipeline, coverage, delivery, billing/control-plane, legal-content or operational dependency may remain before launch.

Any earlier fixture-based or shell web work is non-authoritative and must not be treated as satisfying this gate or as permission to continue web development.

## Current status

- TED source contract: **APPROVED**.
- TED-scoped OPEN semantics: **APPROVED in code and live contract CI**.
- OpenCoesione source contract: **APPROVED for the frozen route only**.
- OpenCoesione collector/parser/schema gate: **IMPLEMENTED, fail-closed**.
- OpenCoesione live source-transfer: **PASS on dedicated Hetzner production runtime**.
- Full live delivery chain: **PASS** — 4,631 funded projects -> complete 176,540-notice/708-page Italy TED universe -> 81 published projects with components -> 37 useful/resolved, 44 safely unresolved -> customer-safe JSONL + PostgreSQL run manifest.
- Persistence/operations: **PASS** — logical backup + scratch restore verified, provider backup enabled, PostgreSQL loopback-only, no unexpected public listener, delivery and backup timers enabled/active.
- Final delivery CI: **PASS** on production release `51c0071fe20011bb407d50c1df63a9d35ef68e76`; web job intentionally skipped.
- Remaining non-web release controls: **OPEN** under A8/A19 in `docs/BUILD_GATES.md`.
- Web build: **BLOCKED ONLY UNTIL THOSE REMAINING NON-WEB RELEASE CONTROLS ARE GREEN**.

The old GitHub-hosted HTTP 403 remains useful historical evidence only: GitHub Actions is not the production OpenCoesione transfer runtime. It is no longer a delivery blocker because the approved dedicated no-contact production runtime has passed the frozen source contract and complete delivery acceptance without weakening the route, schema or zero-PII boundary.
