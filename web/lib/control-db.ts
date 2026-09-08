import "server-only";

import { Pool } from "pg";

let pool: Pool | undefined;
let poolDatabaseUrl: string | undefined;

export function controlDb(): Pool | undefined {
  const databaseUrl = process.env.PROCRUN_CONTROL_DATABASE_URL?.trim();
  if (!databaseUrl) return undefined;

  if (!pool || poolDatabaseUrl !== databaseUrl) {
    pool = new Pool({ connectionString: databaseUrl, max: 2 });
    poolDatabaseUrl = databaseUrl;
  }
  return pool;
}

export async function ensureControlSchema(): Promise<boolean> {
  const activePool = controlDb();
  if (!activePool) return false;

  try {
    await activePool.query(`
      CREATE SCHEMA IF NOT EXISTS procrun_control;
      CREATE TABLE IF NOT EXISTS procrun_control.billing_accounts (
        account_id text PRIMARY KEY,
        stripe_customer_id text UNIQUE,
        stripe_subscription_id text UNIQUE,
        subscription_status text,
        current_period_end timestamptz,
        updated_at timestamptz NOT NULL DEFAULT now()
      );
    `);
    return true;
  } catch {
    return false;
  }
}
