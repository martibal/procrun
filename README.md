# Procurement Runway

Private Phase A data-plane repository for Procurement Runway.

## Product boundary

The engine identifies publicly funded projects, decomposes them into purchasable components, checks procurement evidence up to a dated cutoff, and assigns evidence-backed component states.

Core states:

- `OPEN` — no relevant procurement found in the indexed coverage as of cutoff.
- `CLOSED` — relevant procurement is evidenced on or before cutoff.
- `PARTIAL` — project contains components with different procurement states.
- `UNRESOLVED` — evidence or source coverage is insufficient; fail closed and do not surface an opportunity.

## Phase A scope

Portugal only. No customer UI, billing, CRM, contact database, or generic tender search.

The first milestone is a deterministic pipeline:

`Portugal 2030 project -> components -> prior procurement evidence -> component state -> evidence ledger`

## Privacy rule

The intelligence pipeline is zero-PII by design. Source adapters must emit only explicitly allowlisted fields. Unexpected fields fail validation before persistence, logging, model context, or customer-facing output.

## Evidence ledger

PostgreSQL 16 is the canonical historical ledger. Source content, projects, components, procurement evidence, component/project assessments, outcomes, and run manifests are stored as immutable versions. Corrections append a new row with an explicit `supersedes_version_id`; database triggers reject `UPDATE` and `DELETE` on ledger tables.

`first_seen_at` is never inferred from `project_start`. If defensible historical observability is unavailable, the project remains `temporal_provenance=UNRESOLVED` and cannot support a historical lead-time claim.

See [`docs/LEDGER.md`](docs/LEDGER.md).

## Local disk policy

The repository contains code and small fixtures only. Raw datasets, caches, databases, model weights, exports, and downloaded archives are ignored by Git. Local runtime data should stay bounded and disposable; production state belongs on the EU-hosted server.

The development PostgreSQL container has no host-mounted or named volume. `docker compose down` removes its disposable database state rather than accumulating a local historical replica.

## Development

Python 3.12+ and Docker are recommended.

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -e ".[dev]"
docker compose up -d db
```

Set the integration-test database URL before running the full suite.

Windows PowerShell:

```powershell
$env:PROCRUN_TEST_DATABASE_URL="postgresql://procrun:procrun-local-only@127.0.0.1:5432/procrun"
pytest
```

macOS/Linux:

```bash
export PROCRUN_TEST_DATABASE_URL="postgresql://procrun:procrun-local-only@127.0.0.1:5432/procrun"
pytest
```

Remove the disposable local database when finished:

```bash
docker compose down
```

## Current status

Phase A data-plane work is active. Source contracts, fail-closed PII boundaries, deterministic classification aggregation, bounded local storage, and the append-only PostgreSQL ledger are implemented. The Portugal 2030 live collector remains gated until an approved transport-level PII-safe project route and defensible first-seen provenance are proven.

Product Requirements v1.0 and Phase-0 V1.1 are the governing specifications; implementation must not weaken their evidence or PII rules.
