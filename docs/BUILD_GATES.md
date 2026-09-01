# Phase A build gates

Implementation is not allowed to weaken the Product Requirements v1.0 or Phase-0 V1.1 evidence rules.

## A1 — Source safety

- Portugal 2030 discovery must use a source surface that does not require downloading a broader record containing prohibited fields.
- TED must use server-side field projection.
- Any schema drift outside the frozen allowlist fails closed.
- No beneficiary names, supplier names, contacts, NIF/tax IDs, email, phone, postal address, IP-derived profile data, or equivalent person-identifying fields may enter the intelligence pipeline.

## A2 — Temporal provenance

Every funded project must retain a defensible `first_seen_at`. A current project start date is not a substitute for first public observability.

## A3 — Evidence semantics

`OPEN` always means: no relevant procurement found in the indexed source coverage as of the stated cutoff.

It never means: proven that no procurement exists.

Insufficient coverage becomes `UNRESOLVED`.

## A4 — Component granularity

A project with different component states must not be collapsed to a misleading project-level OPEN/CLOSED answer. Project-level PARTIAL must preserve component-level status.

## A5 — Regression cases

The implementation must preserve the verified Phase-0 V1.1 behavior. In particular:

- `PACS-FC-04022300` must never regress to project-level OPEN when the pre-cutoff level-crossing procurement evidence is in coverage; expected project state is PARTIAL under the verified evidence set.
- previously verified dead leads must remain suppressible when their pre-cutoff procurement evidence is supplied.
- missing evidence coverage must fail closed rather than manufacture an OPEN state.

## A6 — Local disk

Runtime data is disposable and ignored by Git. Default local runtime budget: 20 GiB. Production historical state belongs on the EU-hosted server.

## A7 — Phase A definition of done

Given a new Portugal 2030 project, the system can automatically produce:

`project -> purchasable components -> pre-cutoff procurement evidence -> component states -> project state -> evidence ledger`

with no manual decision in the normal path and no prohibited data entering the intelligence pipeline.
