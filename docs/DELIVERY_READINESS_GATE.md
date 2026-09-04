# ProcRun delivery-readiness gate

## Permanent sequencing rule

Web implementation is the final build phase, not a parallel workstream.

**No customer-facing web application work may start or continue until the entire product delivery chain is production-ready and all delivery gates are green.**

The intended sequence is:

1. source contracts approved from public evidence only;
2. collectors implemented and fail-closed;
3. live source-transfer succeeds against real production sources;
4. canonical pipeline and customer-safe read model run end-to-end on live inputs;
5. coverage semantics, OPEN boundaries, exports and persistence are verified in production code;
6. regression, drift, schema, compliance and no-contact gates are green;
7. only then: start the customer-facing web build.

The target state at web-build start is therefore: **the product is launch-ready except for the web interface itself**. Once the web build is finished and validated, no unresolved source, pipeline, coverage or delivery dependency may remain before launch.

Any earlier fixture-based or shell web work is non-authoritative and must not be treated as satisfying this gate or as permission to continue web development.

## Current status

- TED source contract: APPROVED.
- TED-scoped OPEN semantics: APPROVED in code.
- OpenCoesione source contract: APPROVED for the frozen route only.
- OpenCoesione collector/parser/schema gate: IMPLEMENTED.
- OpenCoesione live source-transfer: **BLOCKED — HTTP 403 from the current GitHub-hosted runtime.**
- Full live delivery chain: **NOT GREEN.**
- Web build: **BLOCKED UNTIL FULL DELIVERY-READINESS IS GREEN.**

The 403 is a runtime/transport problem. It must be resolved with an automated, no-contact execution path that preserves the same frozen source URL, schema and zero-PII constraints. The source gate must not be weakened to obtain a green result.
