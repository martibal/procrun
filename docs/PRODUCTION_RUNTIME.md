# ProcRun production runtime

Status: **IMPLEMENTED IN REPOSITORY; LIVE HOST ACCEPTANCE REQUIRED BEFORE A20 WEB BUILD GO**

## Purpose

The production runtime exists only to execute the non-web delivery chain:

`OpenCoesione -> canonical FundingProject -> TED projected search -> deterministic runway -> append-only ledger -> customer-safe JSONL`

It exposes no ProcRun application port. PostgreSQL is bound to loopback only. The web layer is not installed or served by this runtime.

## Approved target

The current target is a dedicated Hetzner Cloud EU VPS under the already-approved `hetzner_cloud` compliance service. It must not share Urd Atlas/Trendanalytics infrastructure.

Default provisioning target:

- server: `procrun-prod`
- type: `cx33`
- location: `hel1`
- image: `ubuntu-24.04`
- provider daily backups: enabled
- local logical PostgreSQL backup: daily, restore-verified

The server type/location may not silently fall back to another target after a capacity or provisioning error. Any change requires an explicit repository decision and the same compliance/runtime acceptance.

## Provisioning

Run from a clean committed ProcRun checkout:

```powershell
$env:HCLOUD_TOKEN = "<token in current shell only>"
.\scripts\provision_production_server.ps1 -SshKey "<existing Hetzner SSH key name>"
```

The token is never written into Git or copied to the production server.

The provisioning script:

1. runs the repository Hetzner compliance gate;
2. refuses duplicate server names;
3. creates the exact configured server without automatic type/location fallback;
4. enables Hetzner daily backups;
5. uploads a `git archive` of the exact clean commit, so the server needs no GitHub credential;
6. waits for cloud-init;
7. creates the Python runtime and installs pinned dependencies;
8. installs systemd delivery/backup units;
9. executes the first real live delivery run;
10. requires a non-empty customer-safe JSONL output and at least one run manifest;
11. executes a PostgreSQL logical backup and restores it into a scratch database;
12. verifies no unexpected public TCP listener exists;
13. enables recurring timers only after all preceding checks pass.

Any failed step leaves A20 blocked. A created server is never treated as successful merely because infrastructure exists.

## Live delivery fail-closed rules

The production delivery command is:

```bash
/opt/procrun/venv/bin/python scripts/run_live_delivery.py \
  --output /var/lib/procrun/published/runway.jsonl
```

It fails without publishing a new output if any of these conditions occur:

- OpenCoesione transport/redirect/content/schema validation fails;
- the OpenCoesione batch is empty;
- TED projected search fails;
- TED ITERATION does not complete or its returned count does not reconcile;
- a source or evidence object violates its allowlist/domain invariant;
- the append-only ledger write fails;
- real sources produce zero resolved customer runway projects.

`OPEN` is valid only when the TED universe is complete and is rendered exactly as:

> **No relevant procurement found in TED as of DATE.**

No live result claims absence outside TED.

## Persistence

PostgreSQL is local to the dedicated runtime and listens only on `127.0.0.1`. The generated database password exists only in `/etc/procrun/procrun.env` with root/procrun group access.

The ledger remains append-only and stores source/version provenance, canonical projects/components/evidence, component/project assessments and run manifests. Browser code never connects directly to this database.

## Backup and restore

Two recovery paths are required:

1. Hetzner automatic daily server backups;
2. daily logical `pg_dump` files under `/var/backups/procrun`.

Every logical backup is immediately restored into a temporary database and checked for the ProcRun migration ledger. A backup job that cannot restore is a failed backup job.

The local logical retention is 14 days. Provider backup retention follows the active Hetzner seven-slot backup service.

## Timers

- verified logical backup: daily at 03:30 UTC plus up to five minutes randomized delay;
- live delivery: daily at 06:15 UTC plus up to five minutes randomized delay.

Timers are persistent and are enabled only after the first live production acceptance succeeds.

## Acceptance evidence required before A20 GO

Before `A20 WEB BUILD` may change to `GO`, repository status must record all of the following from the actual dedicated runtime:

- exact deployed commit;
- OpenCoesione accepted operation count, list update date and source SHA-256;
- TED production query count and complete page count;
- nonzero canonical/live customer output count;
- run-manifest presence in restored PostgreSQL data;
- successful logical restore verification;
- enabled provider backup and both systemd timers;
- no unexpected public listener;
- final Python/compliance/TED-contract CI green on that same commit.

No fixture, local unit test or GitHub-hosted OpenCoesione request may substitute for this acceptance.