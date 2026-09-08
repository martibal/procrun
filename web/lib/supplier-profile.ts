import "server-only";

import { procrunDb } from "@/lib/procrun-db";

export type SupplierProfile = {
  accountId: string;
  companyName: string;
  targetMarket: "LOMBARDIA";
  categoryPrefixes: string[];
  cpvInclude: string[];
  cpvExclude: string[];
  minProjectValueEur: number | null;
  maxProjectValueEur: number | null;
};

export type SupplierProfileInput = Omit<SupplierProfile, "accountId">;

function normalizedCategories(categories: string[]): string[] {
  const values = new Set<string>();
  for (const category of categories) {
    const clean = category.trim();
    if (!clean) continue;
    values.add(clean);
    const root = clean.split(":", 1)[0];
    if (root) values.add(root);
  }
  return Array.from(values).sort();
}

export async function loadAvailableCategories(): Promise<string[] | null> {
  const activePool = procrunDb();
  if (!activePool) return null;

  try {
    const result = await activePool.query<{ category: string }>(`
      WITH latest_component AS (
        SELECT DISTINCT ON (component_id)
          component_id,
          category
        FROM procrun.component_versions
        ORDER BY component_id, as_of DESC, inserted_at DESC, version_id DESC
      )
      SELECT DISTINCT category
      FROM latest_component
      WHERE length(btrim(category)) > 0
      ORDER BY category
    `);
    return normalizedCategories(result.rows.map((row) => row.category));
  } catch {
    return null;
  }
}

export async function loadSupplierProfile(accountId: string): Promise<SupplierProfile | null> {
  const activePool = procrunDb();
  if (!activePool) return null;

  try {
    const result = await activePool.query<{
      account_id: string;
      company_name: string;
      target_market: "LOMBARDIA";
      category_prefixes: string[];
      cpv_include: string[];
      cpv_exclude: string[];
      min_project_value_eur: string | number | null;
      max_project_value_eur: string | number | null;
    }>(`
      SELECT
        account_id,
        company_name,
        target_market,
        category_prefixes,
        cpv_include,
        cpv_exclude,
        min_project_value_eur,
        max_project_value_eur
      FROM procrun.supplier_profiles
      WHERE account_id = $1
      LIMIT 1
    `, [accountId]);

    const row = result.rows[0];
    if (!row) return null;
    return {
      accountId: row.account_id,
      companyName: row.company_name,
      targetMarket: row.target_market,
      categoryPrefixes: row.category_prefixes ?? [],
      cpvInclude: row.cpv_include ?? [],
      cpvExclude: row.cpv_exclude ?? [],
      minProjectValueEur: row.min_project_value_eur === null ? null : Number(row.min_project_value_eur),
      maxProjectValueEur: row.max_project_value_eur === null ? null : Number(row.max_project_value_eur),
    };
  } catch {
    return null;
  }
}

export async function saveSupplierProfile(
  accountId: string,
  input: SupplierProfileInput,
): Promise<void> {
  const activePool = procrunDb();
  if (!activePool) throw new Error("Supplier Profile database is unavailable.");
  if (input.targetMarket !== "LOMBARDIA") throw new Error("Unsupported Supplier Profile market.");

  const client = await activePool.connect();
  try {
    await client.query("BEGIN");
    await client.query(
      "INSERT INTO procrun.accounts (account_id) VALUES ($1) ON CONFLICT (account_id) DO NOTHING",
      [accountId],
    );
    await client.query(`
      INSERT INTO procrun.supplier_profiles (
        account_id,
        company_name,
        target_market,
        category_prefixes,
        cpv_include,
        cpv_exclude,
        min_project_value_eur,
        max_project_value_eur,
        completed_at,
        updated_at
      ) VALUES ($1, $2, $3, $4::text[], $5::text[], $6::text[], $7, $8, now(), now())
      ON CONFLICT (account_id) DO UPDATE SET
        company_name = EXCLUDED.company_name,
        target_market = EXCLUDED.target_market,
        category_prefixes = EXCLUDED.category_prefixes,
        cpv_include = EXCLUDED.cpv_include,
        cpv_exclude = EXCLUDED.cpv_exclude,
        min_project_value_eur = EXCLUDED.min_project_value_eur,
        max_project_value_eur = EXCLUDED.max_project_value_eur,
        updated_at = now()
    `, [
      accountId,
      input.companyName,
      input.targetMarket,
      input.categoryPrefixes,
      input.cpvInclude,
      input.cpvExclude,
      input.minProjectValueEur,
      input.maxProjectValueEur,
    ]);
    await client.query("COMMIT");
  } catch (error) {
    await client.query("ROLLBACK");
    throw error;
  } finally {
    client.release();
  }
}

export async function syncComponentMatches(
  accountId: string,
  componentIds: string[],
): Promise<boolean> {
  const activePool = procrunDb();
  if (!activePool) return false;

  const ids = Array.from(new Set(componentIds)).sort();
  const client = await activePool.connect();
  try {
    await client.query("BEGIN");
    await client.query(
      "INSERT INTO procrun.accounts (account_id) VALUES ($1) ON CONFLICT (account_id) DO NOTHING",
      [accountId],
    );
    await client.query(`
      INSERT INTO procrun.component_matches (account_id, component_id, first_matched_at)
      SELECT $1, component_id, now()
      FROM unnest($2::text[]) AS component_id
      ON CONFLICT (account_id, component_id) DO NOTHING
    `, [accountId, ids]);
    await client.query(`
      DELETE FROM procrun.component_matches
      WHERE account_id = $1
        AND NOT (component_id = ANY($2::text[]))
    `, [accountId, ids]);
    await client.query("COMMIT");
    return true;
  } catch {
    await client.query("ROLLBACK");
    return false;
  } finally {
    client.release();
  }
}
