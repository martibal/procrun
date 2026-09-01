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

## Local disk policy

The repository contains code and small fixtures only. Raw datasets, caches, databases, model weights, exports, and downloaded archives are ignored by Git. Local runtime data should stay bounded and disposable; production state belongs on the EU-hosted server.

## Development

Python 3.12+.

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -e ".[dev]"
pytest
```

## Current status

Phase A bootstrap. Product Requirements v1.0 and Phase-0 V1.1 are the governing specifications; implementation must not weaken their evidence or PII rules.
