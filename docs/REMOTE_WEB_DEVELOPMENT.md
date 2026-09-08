# ProcRun remote web development database access

## Goal

A developer should be able to work from any trusted PC without copying the production database locally and without opening PostgreSQL to the public internet.

The production database remains on `procrun-prod` and remains bound to `127.0.0.1:5432`. Local Next.js development connects through an encrypted SSH tunnel. Browser code never receives database credentials and never connects directly to PostgreSQL.

## One-time server setup

From a trusted Windows PC with the ProcRun SSH key and an up-to-date checkout, run from the repository root:

```powershell
.\scripts\bootstrap_remote_web_dev.ps1
```

The script:

1. copies only the role-definition SQL to `/tmp` on the server;
2. creates or refreshes the least-privilege `procrun_web_dev` role;
3. grants only the columns required by the current customer web application;
4. does not grant the unresolved precise-geography field or source-only identity fields;
5. prompts interactively for the PostgreSQL role password so no password literal is placed in a command line or Git;
6. removes the temporary SQL file from the server.

The role has no insert/delete permission. It receives narrow update permission only for the existing account activity summary fields used by the development web application.

## Daily use from any trusted PC

Requirements on that PC:

- current ProcRun Git checkout;
- Node/npm dependencies installed in `web/`;
- SSH key at `%USERPROFILE%\.ssh\procrun_hetzner`.

Then:

```powershell
cd C:\procrun

git fetch origin
git switch web/customer-site-foundation
git pull origin web/customer-site-foundation

cd web
npm install
npm run dev:remote
```

`npm run dev:remote` opens an SSH local-forward from `127.0.0.1:55432` to the production server's loopback-only PostgreSQL listener, prompts securely for the `procrun_web_dev` password unless `PROCRUN_DEV_DB_PASSWORD` is already present in the local process environment, sets `PROCRUN_DATABASE_URL` only for the lifetime of the local development process, starts Next.js, and closes the tunnel when Next.js stops.

No database copy, `.env.local` database secret, public PostgreSQL listener, or PC-specific database is required.

## Security boundary

This mechanism is for trusted developer workstations only. It does not make the production database public and must not be reused as the eventual customer/browser database architecture.

The customer-facing production application still requires its own authenticated deployment/control plane. The production runtime contract remains unchanged: PostgreSQL listens only on loopback and the browser must never connect directly to the intelligence database.
