# Procurement Runway build/release gates

Implementation is not allowed to weaken Product Requirements v1.0 or Phase-0 V1.1 evidence rules.

## A1 — Source safety

- A source is production-usable only when RIGHTS, ACCESS and DATA SAFETY are all approved.
- Portugal 2030 discovery must not require receipt of broader records containing prohibited fields.
- TED uses server-side field projection only.
- Any schema drift outside the frozen allowlist fails closed.
- No beneficiary natural-person name, supplier/adjudicatário, contact, NIF/tax ID, email, phone, personal/postal address, signature or equivalent person-identifying field may enter the intelligence pipeline.
- Public availability does not override these requirements.

## A2 — Temporal provenance

Every funded project retains defensible `first_seen_at`. Project start date is never substituted for first public observability. If first public observability is not proven, `temporal_provenance=UNRESOLVED` and the project cannot support a historical lead-time claim.

## A3 — Evidence semantics

`OPEN` means only: no relevant procurement found in the indexed permitted source coverage as of the stated cutoff.

It never means: proven that no procurement exists.

Insufficient coverage becomes `UNRESOLVED`.

## A4 — Component granularity

A project with different component states must not be collapsed into a misleading project-level OPEN/CLOSED answer. Project-level `PARTIAL` preserves component-level status.

## A5 — Regression cases

- `PACS-FC-04022300` must never regress to project-level OPEN when its verified pre-cutoff level-crossing procurement evidence is in coverage; expected project state is PARTIAL.
- verified dead leads remain suppressible when their pre-cutoff procurement evidence is supplied.
- missing evidence coverage fails closed rather than manufacturing OPEN.

## A6 — Local disk

Runtime data is disposable and ignored by Git. Default local runtime budget: 20 GiB. Production historical state belongs on the EU-hosted server.

## A7 — Core engine definition of done

Given a permitted funded-project input, the system can produce:

`project -> purchasable components -> pre-cutoff procurement evidence -> component states -> project state -> evidence ledger`

with no manual decision in the normal path and no prohibited data entering the intelligence pipeline.

Live Portugal release remains independently gated on an approved project-discovery transport.

## A8 — PostgreSQL ledger

- PostgreSQL 16 is canonical; `pg_trgm` and full-text indexes are enabled for bounded candidate search.
- Every source content version has source/record ID, URL, normalized allowlisted fields, schema version and SHA-256.
- Retrieval timestamps are immutable observations.
- Funding projects, components, evidence, component/project assessments, outcomes and manifests are versioned.
- Corrections append a new version with `supersedes_version_id`; database triggers reject UPDATE/DELETE on ledger tables.
- Classification provenance retains accepted evidence IDs, candidate data and rejected-evidence reasons.
- CI exercises invariants against PostgreSQL 16, not only mocks.

## A9 — Local-model benchmark boundary

- Deterministic rules remain primary.
- Model sees only unmatched, allowlisted scope spans and frozen categories.
- Model output is proposal-only and cannot set procurement/opportunity state.
- Benchmark adapter accepts only registry `BENCHMARK_CANDIDATE` artifacts.
- Exact GGUF and `llama-cli` bytes are hash-bound before inference.
- Runtime is offline, deterministic, time-bounded and memory-bounded.
- Generated/cached proposals are revalidated against exact source spans and allowed domain/category pairs.
- Production approval requires an explicit later evidence-backed registry decision.

## A10 — Rights/access compliance

Every production source must have:

- explicit commercial-reuse decision;
- explicit automated-access decision/conditions;
- legal/terms reference URLs;
- attribution requirement/text where applicable;
- finite review date and review-due date;
- fail-closed test for stale/non-approved status.

Direct scraping of Mais Transparência HTML is not an approved production source contract. Portal BASE APIBase2 remains blocked irrespective of token availability until the pre-receipt field boundary is solved.

## A11 — Third-party dependency/provider control

- Direct production Python dependencies are exact-version pinned.
- Runtime transitive dependency versions are constrained by `requirements-runtime.lock`.
- Runtime licences are recorded in `src/procrun/compliance.py` / `THIRD_PARTY_NOTICES.md`.
- New direct runtime dependencies require a reviewed licence entry before CI can pass.
- GitHub, Hetzner and Hugging Face are limited to the explicitly reviewed roles in `docs/COMPLIANCE.md`.
- Stripe and Cloudflare are `CONDITIONAL`; they must not be activated merely because integration code exists.
- Approved provider/dependency/model reviews expire and fail closed until renewed.

## A12 — Customer website/control-plane release gate

Before paid customer release:

- legal entity/merchant identity is final;
- customer Terms of Service and Privacy Notice are published;
- account/billing/support PII is architecturally separate from the intelligence ledger/model;
- payment-provider account/terms and VAT/invoicing flow are approved;
- necessary processor/subprocessor DPAs/inventory are in place;
- source attribution/methodology page reflects then-current source obligations;
- no analytics/session-replay/advertising SDK is enabled by default;
- application/reverse-proxy logging does not persist client IP in the ProcRun data plane;
- TLS, secrets, least privilege, encrypted backup and restore procedure are verified;
- then-current Portuguese source rights/attribution and customer terms receive a short external legal review.

## A13 — Cost ceiling

Projected trailing-30-day recurring core infrastructure spend:

- target: <= NOK 400/month;
- warn above NOK 400/month;
- no recurring architecture change may exceed NOK 500/month without an explicit architecture decision.

Customer-volume-driven payment fees are tracked separately from this core-infrastructure gate.
