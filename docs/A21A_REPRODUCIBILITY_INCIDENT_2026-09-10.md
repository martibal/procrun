# A21a reproducibility incident — 2026-09-10

**Status:** ACTIVE REMEDIATION — INVALIDATED DEVELOPMENT LINEAGE LOCKED OUT

## Incident

The legacy `build_a21a_live_sintesi_development_sample.py` path downloaded the complete OpenCoesione Lombardia ZIP before projecting the A21a source fields locally. That is a prohibited download-then-filter path under the permanent A21a zero-PII ingress contract.

This path was actually executed. GitHub Actions run `34414756824` successfully built and uploaded artifact `10128618927` (`a21a-live-sintesi-development-sample`). Therefore the resulting development lineage is invalid for active A21a qualification; this is not merely a code-level hypothetical.

## Invalidated lineage

The following hashes are permanently historical-only and must never satisfy an active A21a gate:

- 60-case development sample: `f214a0ee54bec0de8ef67d29707e18562fee582db57c60448b7014841e8e0b37`;
- derived 14-case weak-title sample: `d014391f1e6f0f4e10bc0041352a4ea15fb12e4fe03cc974d31709a2c0dee02b`.

The title-utility review, title/objective fallback review and decisions derived from those samples remain historical provenance only. Their labels or conclusions must not be copied into a replacement development set and presented as independent review.

The numerical threshold freeze `a21a-thresholds-v1` is also invalidated as a clean preregistration. The numerical values are retained for auditability, but the active evaluator is fail-closed until a new independent clean-development review has completed and a new threshold version is frozen afterwards.

## Clean replacement baseline

The replacement baseline is derived only from the approved publisher-sanitized A21a source pool produced by workflow run `34485064842`, artifact `10155244738`.

Pinned provenance:

- artifact ZIP SHA-256: `119c5e910dcf3d9495f8f4f3d74f131d68c0e8d850a85588e80bbac0542bcf95`;
- sanitized source-pool content SHA-256: `b34974616732dd7a1b95f0f8f577ce9f5b939f5448fc02610d02a5bf43955424`;
- deterministic 60-case clean-development sample canonical SHA-256: `3a53c93484a2c2eac6ec2fa2942b803ac72f0112ea0c4b52fffde0dd0a67fbd9`;
- case count: `60`;
- selection seed: `a21a-evidence-development-set-v1`;
- zero-PII status: `ZERO_PII_CONFIRMED`;
- download-then-filter used: `false`;
- prior review labels reused: `false`;
- independent clean review complete: `false`.

The machine-readable pin is `tests/fixtures/a21a_clean_development_lineage_v2.json` and the enforcement constants are in `procrun.a21a_lineage`.

## Holdout integrity

This incident invalidates the A21a development/preregistration lineage only. The sealed A21/A21b holdout was not used by the offending sample builder or the downstream development-review scripts. Existing fail-closed code requires `sealed_holdout_touched` to remain false. The sealed holdout must remain unopened while this remediation is completed.

## Required sequence before A21a can become green

1. Use only the pinned clean-v2 development baseline.
2. Perform a new independent review without reusing the invalidated v1 labels.
3. Reproduce the relevant development analyses from that clean review.
4. Freeze a new threshold preregistration only after those clean development results exist.
5. Freeze the final disjoint population and only then run the sealed final A21a evaluation.

This remediation is completed exclusively from approved published artifacts and deterministic local processing under the permanent no-outreach build rule.
