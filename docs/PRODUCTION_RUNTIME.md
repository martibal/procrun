# ProcRun production runtime

Status: **LIVE HOST ACCEPTED — NON-WEB PRODUCTION RUNTIME PASS**

## Purpose

The production runtime executes only the intelligence delivery chain:

`OpenCoesione -> FundingProject -> TED projected search -> deterministic runway -> append-only ledger -> customer-safe JSONL`

It exposes no ProcRun customer application port. PostgreSQL is bound to loopback only. The customer web/control plane is a separate phase.

## Accepted target

- server: `procrun-prod`
- Hetzner server id: `164569825`
- location: `hel1`
- image: Ubuntu 24.04
- provider daily backups: enabled
- local logical PostgreSQL backup: daily and restore-verified

The runtime is dedicated to ProcRun and does not share Urd Atlas/Trendanalytics infrastructure.

## Live acceptance evidence

The first complete accepted production run completed on 2026-09-04/05 and produced:

- 4,631 funded projects;
- 176,540 TED records across 708 complete pages;
- 81 projects with components / published projects;
- 37 useful/resolved projects;
- 44 safely unresolved projects;
- customer-safe JSONL at `/var/lib/procrun/published/runway.jsonl`;
- PostgreSQL run manifest;
- clean oneshot service completion.

The accepted live run was generated before later non-semantic operations/type housekeeping. The final delivery runtime code was subsequently promoted to commit `51c0071fe20011bb407d50c1df63a9d35ef68e76` without re-running TED; that commit had green delivery CI before promotion.

## Live delivery fail-closed rules

The production command is:

```bash
/opt/procrun/venv/bin/python scripts/run_live_delivery.py --output /var/lib/procrun/published/runway.jsonl
```

A new publication fails closed if OpenCoesione transport/schema validation fails, the funded-project batch is empty, TED retrieval is incomplete, evidence/read-model invariants fail, the append-only ledger write fails, or real sources produce zero resolved customer runway projects.

`OPEN` is valid only with complete TED coverage and is rendered exactly as:

> **No relevant procurement found in TED as of DATE.**

## Persistence and network boundary

PostgreSQL listens on `127.0.0.1:5432`. The verified listener check showed only PostgreSQL loopback, local system DNS and public SSH/22; no ProcRun database/application listener was publicly exposed.

Database secrets remain outside Git in the production environment. Browser code must never connect directly to the intelligence database.

## Backup and restore

Two recovery paths are active:

1. Hetzner provider backup;
2. logical `pg_dump` under `/var/backups/procrun`.

The logical backup service has completed a real scratch restore verification with `restore_verified=true`. Local logical retention is 14 days.

## Timers

Both timers are enabled and active:

- logical backup: daily 03:30 UTC plus up to five minutes randomized delay;
- live delivery: daily 06:15 UTC plus up to five minutes randomized delay.

The verified next schedules after activation were 2026-09-06 03:33:24 UTC and 06:17:37 UTC respectively.

## Operational semantics

A systemd delivery service is a oneshot and is expected to become inactive/dead after a successful run. Nonzero exit or fail-closed validation is a failed delivery, not a partial success. A failed new run must not be represented as a fresh publication.

Backup success requires restore verification, not merely creation of a dump file.

The historical GitHub-hosted OpenCoesione HTTP 403 is not a production-runtime failure: GitHub Actions is intentionally not the live OpenCoesione transfer runtime.

## Pre-web decision

All production-runtime acceptance requirements are satisfied. See `docs/PREWEB_RELEASE_BASELINE.md` and A19/A20 in `docs/BUILD_GATES.md`.
