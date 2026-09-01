# Phase A PostgreSQL ledger

The ledger is the canonical historical state for Procurement Runway. It is designed to satisfy Product Requirements v1.0 Section 8: immutable `as_of`, source provenance and hashes, versioned classifications, explicit supersession, outcome lead-time tracking, and deterministic run manifests.

## Storage model

PostgreSQL 16 owns the durable relational state. `pg_trgm` and built-in full-text search are enabled for later candidate matching without adding a paid vector database.

The Phase-A schema contains:

- `source_record_versions` — allowlisted normalized source content plus source URL/ID, schema version, first-seen metadata and SHA-256.
- `source_retrievals` — immutable observations of when a source content version was retrieved for a run.
- `funding_project_versions` — canonical Portugal-project fields and temporal-provenance state.
- `component_versions` — purchasable component definitions and exact supporting scope text.
- `procurement_evidence_versions` — component-linked procurement facts with exact source-version provenance.
- `assessment_versions` — component state, cutoff, rule/model versions, matching candidates, accepted evidence versions and rejected-evidence reasons.
- `project_assessment_versions` — derived project OPEN/CLOSED/PARTIAL/UNRESOLVED state linked to exact component-assessment versions.
- `outcome_versions` — later procurement linked to the original component assessment with computed `lead_days`.
- `run_manifests` — run counts, input/output hashes, schema version and classifier version.

## Append-only rule

Ledger rows are never corrected in place. Every version table has a PostgreSQL trigger that rejects `UPDATE` and `DELETE`. A material correction appends a new content version whose `supersedes_version_id` points to the prior current version.

Unchanged content is idempotent: the append API returns the existing current version. A later reversion from A -> B -> A is still preserved as a third version because version identity includes the predecessor, not only the content hash.

## Hash rule

Hashes use canonical UTF-8 JSON: mapping keys are sorted, whitespace is eliminated, enums use their values, and timezone-aware datetimes are normalized to UTC. Naive datetimes are rejected.

Runtime timestamps such as database `inserted_at` are not analytical content and are excluded from content hashes. Run-manifest hashes cover the run key, counts, schema/classifier versions and input/output hashes, so an unchanged rerun has identical analytical hashes.

## Temporal provenance

`project_start` is never a substitute for market observability. `FundingProject.first_seen_at` may be absent, and the default is `temporal_provenance=UNRESOLVED`. `RESOLVED` is reserved for an approved source history that defensibly establishes first public appearance.

## PII boundary

The ledger accepts normalized domain models only after source-level allowlist enforcement. A live source must also pass `require_live_source()` before source content can be recorded. Raw HTTP bodies, HTML, XML, PDFs and prohibited fields have no storage path in this schema.

## Migrations

`apply_migrations()` records versioned migrations in `procrun.schema_migrations` and applies the initial schema transactionally. CI runs the integration suite against an actual PostgreSQL 16 service and verifies the append-only database trigger rather than only testing Python behavior.
