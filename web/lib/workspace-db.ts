import { Pool } from "pg";
import { requireTenantKey } from "./tenant-capability";

export type SupplierProfile = {
  domains: string[];
  cpvPrefixes: string[];
  nutsPrefixes: string[];
  minProjectValueEur: number;
};

const allowedDomains = new Set([
  "water_wastewater", "rail_transport", "ports_coastal", "energy_efficiency", "resilience_fire",
]);

let pool: Pool | undefined;
let migrated = false;

function database(): Pool {
  const connectionString = process.env.PROCRUN_WORKSPACE_DATABASE_URL;
  if (!connectionString) throw new Error("PROCRUN_WORKSPACE_DATABASE_URL is not configured");
  pool ??= new Pool({ connectionString, max: 5 });
  return pool;
}

export function validateProfile(value: unknown): SupplierProfile {
  if (typeof value !== "object" || value === null || Array.isArray(value)) throw new Error("profile must be an object");
  const row = value as Record<string, unknown>;
  const domains = Array.isArray(row.domains) ? [...new Set(row.domains.map(String).filter(Boolean))] : [];
  if (domains.some((domain) => !allowedDomains.has(domain))) throw new Error("unsupported supplier domain");
  const cpvPrefixes = Array.isArray(row.cpvPrefixes) ? [...new Set(row.cpvPrefixes.map(String).filter(Boolean))] : [];
  if (cpvPrefixes.some((value) => !/^\d{2,8}$/.test(value))) throw new Error("invalid CPV prefix");
  const nutsPrefixes = Array.isArray(row.nutsPrefixes) ? [...new Set(row.nutsPrefixes.map((value) => String(value).toUpperCase()).filter(Boolean))] : [];
  if (nutsPrefixes.some((value) => !/^[A-Z0-9]{2,5}$/.test(value))) throw new Error("invalid NUTS prefix");
  const minProjectValueEur = Number(row.minProjectValueEur ?? 0);
  if (!Number.isSafeInteger(minProjectValueEur) || minProjectValueEur < 0) throw new Error("invalid project value floor");
  return { domains, cpvPrefixes, nutsPrefixes, minProjectValueEur };
}

export async function ensureWorkspaceSchema(): Promise<void> {
  if (migrated) return;
  await database().query(`
    CREATE SCHEMA IF NOT EXISTS procrun_workspace;
    CREATE TABLE IF NOT EXISTS procrun_workspace.supplier_profiles (
      tenant_key text PRIMARY KEY CHECK (tenant_key ~ '^org_[0-9a-f]{32}$'),
      domains text[] NOT NULL DEFAULT '{}',
      cpv_prefixes text[] NOT NULL DEFAULT '{}',
      nuts_prefixes text[] NOT NULL DEFAULT '{}',
      min_project_value_eur bigint NOT NULL DEFAULT 0 CHECK (min_project_value_eur >= 0),
      updated_at timestamptz NOT NULL DEFAULT now()
    );
    CREATE TABLE IF NOT EXISTS procrun_workspace.saved_opportunities (
      tenant_key text NOT NULL CHECK (tenant_key ~ '^org_[0-9a-f]{32}$'),
      opportunity_key text NOT NULL CHECK (length(opportunity_key) BETWEEN 1 AND 512),
      saved_at timestamptz NOT NULL DEFAULT now(),
      PRIMARY KEY (tenant_key, opportunity_key)
    );
  `);
  migrated = true;
}

export async function getProfile(tenantKey: string): Promise<SupplierProfile | null> {
  const tenant = requireTenantKey(tenantKey);
  await ensureWorkspaceSchema();
  const result = await database().query(
    `SELECT domains, cpv_prefixes, nuts_prefixes, min_project_value_eur
     FROM procrun_workspace.supplier_profiles WHERE tenant_key = $1`, [tenant],
  );
  if (!result.rowCount) return null;
  const row = result.rows[0];
  return {
    domains: row.domains ?? [], cpvPrefixes: row.cpv_prefixes ?? [], nutsPrefixes: row.nuts_prefixes ?? [],
    minProjectValueEur: Number(row.min_project_value_eur),
  };
}

export async function putProfile(tenantKey: string, value: unknown): Promise<SupplierProfile> {
  const tenant = requireTenantKey(tenantKey);
  const profile = validateProfile(value);
  await ensureWorkspaceSchema();
  await database().query(
    `INSERT INTO procrun_workspace.supplier_profiles
       (tenant_key, domains, cpv_prefixes, nuts_prefixes, min_project_value_eur)
     VALUES ($1,$2,$3,$4,$5)
     ON CONFLICT (tenant_key) DO UPDATE SET domains=EXCLUDED.domains, cpv_prefixes=EXCLUDED.cpv_prefixes,
       nuts_prefixes=EXCLUDED.nuts_prefixes, min_project_value_eur=EXCLUDED.min_project_value_eur, updated_at=now()`,
    [tenant, profile.domains, profile.cpvPrefixes, profile.nutsPrefixes, profile.minProjectValueEur],
  );
  return profile;
}

export async function listSaved(tenantKey: string): Promise<string[]> {
  const tenant = requireTenantKey(tenantKey);
  await ensureWorkspaceSchema();
  const result = await database().query(
    `SELECT opportunity_key FROM procrun_workspace.saved_opportunities WHERE tenant_key=$1 ORDER BY opportunity_key`, [tenant],
  );
  return result.rows.map((row) => String(row.opportunity_key));
}

export async function setSaved(tenantKey: string, opportunityKey: string, saved: boolean): Promise<void> {
  const tenant = requireTenantKey(tenantKey);
  const key = opportunityKey.trim();
  if (!key || key.length > 512) throw new Error("invalid opportunity key");
  await ensureWorkspaceSchema();
  if (saved) {
    await database().query(
      `INSERT INTO procrun_workspace.saved_opportunities (tenant_key, opportunity_key) VALUES ($1,$2) ON CONFLICT DO NOTHING`,
      [tenant, key],
    );
  } else {
    await database().query(
      `DELETE FROM procrun_workspace.saved_opportunities WHERE tenant_key=$1 AND opportunity_key=$2`, [tenant, key],
    );
  }
}

export async function deleteWorkspace(tenantKey: string): Promise<void> {
  const tenant = requireTenantKey(tenantKey);
  await ensureWorkspaceSchema();
  const client = await database().connect();
  try {
    await client.query("BEGIN");
    await client.query(`DELETE FROM procrun_workspace.saved_opportunities WHERE tenant_key=$1`, [tenant]);
    await client.query(`DELETE FROM procrun_workspace.supplier_profiles WHERE tenant_key=$1`, [tenant]);
    await client.query("COMMIT");
  } catch (error) {
    await client.query("ROLLBACK");
    throw error;
  } finally {
    client.release();
  }
}

export async function closeWorkspacePoolForTests(): Promise<void> {
  if (pool) await pool.end();
  pool = undefined;
  migrated = false;
}
