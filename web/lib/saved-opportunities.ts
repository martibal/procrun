import "server-only";

import { procrunDb } from "@/lib/procrun-db";

export type SavedOpportunity = {
  componentId: string;
  operationCode: string;
  projectTitle: string | null;
  description: string;
  category: string;
  state: "OPEN" | "CLOSED" | "UNRESOLVED";
  cutoffDate: string;
  approvedFundingEur: number | null;
  programme: string | null;
  region: string | null;
  nutsCode: string | null;
};

export async function saveOpportunity(accountId: string, componentId: string): Promise<void> {
  const pool = procrunDb();
  if (!pool) throw new Error("Saved Opportunities database is unavailable.");

  const client = await pool.connect();
  try {
    await client.query("BEGIN");
    const allowed = await client.query<{ component_id: string }>(`
      SELECT component_id
      FROM procrun.component_matches
      WHERE account_id = $1 AND component_id = $2
      LIMIT 1
    `, [accountId, componentId]);
    if (allowed.rows.length === 0) throw new Error("Opportunity is not in this account's matched feed.");

    await client.query(`
      INSERT INTO procrun.saved_opportunities (account_id, component_id)
      VALUES ($1, $2)
      ON CONFLICT (account_id, component_id) DO NOTHING
    `, [accountId, componentId]);
    await client.query("COMMIT");
  } catch (error) {
    await client.query("ROLLBACK");
    throw error;
  } finally {
    client.release();
  }
}

export async function removeSavedOpportunity(accountId: string, componentId: string): Promise<void> {
  const pool = procrunDb();
  if (!pool) throw new Error("Saved Opportunities database is unavailable.");
  await pool.query(
    "DELETE FROM procrun.saved_opportunities WHERE account_id = $1 AND component_id = $2",
    [accountId, componentId],
  );
}

export async function loadSavedComponentIds(accountId: string): Promise<Set<string> | null> {
  const pool = procrunDb();
  if (!pool) return null;
  try {
    const result = await pool.query<{ component_id: string }>(
      "SELECT component_id FROM procrun.saved_opportunities WHERE account_id = $1 ORDER BY component_id",
      [accountId],
    );
    return new Set(result.rows.map((row) => row.component_id));
  } catch {
    return null;
  }
}

export async function loadSavedOpportunities(accountId: string): Promise<SavedOpportunity[] | null> {
  const pool = procrunDb();
  if (!pool) return null;
  try {
    const result = await pool.query<{
      component_id: string;
      operation_code: string;
      project_title: string | null;
      description: string;
      category: string;
      state: SavedOpportunity["state"];
      cutoff_date: string;
      approved_funding_eur: string | number | null;
      programme: string | null;
      region: string | null;
      nuts_code: string | null;
    }>(`
      WITH latest_component AS (
        SELECT DISTINCT ON (component_id)
          component_id, operation_code, description, category
        FROM procrun.component_versions
        ORDER BY component_id, as_of DESC, inserted_at DESC, version_id DESC
      ),
      current_assessment AS (
        SELECT DISTINCT ON (component_id)
          component_id, operation_code, cutoff_date, state
        FROM procrun.assessment_versions
        ORDER BY component_id, cutoff_date DESC, as_of DESC, inserted_at DESC, version_id DESC
      ),
      latest_project AS (
        SELECT DISTINCT ON (operation_code)
          operation_code, project_title, approved_funding_eur, programme, region, nuts_code
        FROM procrun.funding_project_versions
        ORDER BY operation_code, as_of DESC, inserted_at DESC, version_id DESC
      )
      SELECT
        s.component_id,
        c.operation_code,
        p.project_title,
        c.description,
        c.category,
        a.state,
        a.cutoff_date::text,
        p.approved_funding_eur,
        p.programme,
        p.region,
        p.nuts_code
      FROM procrun.saved_opportunities s
      JOIN latest_component c ON c.component_id = s.component_id
      JOIN current_assessment a
        ON a.component_id = c.component_id
       AND a.operation_code = c.operation_code
      JOIN latest_project p ON p.operation_code = c.operation_code
      WHERE s.account_id = $1
      ORDER BY p.project_title NULLS LAST, c.description, s.component_id
    `, [accountId]);

    return result.rows.map((row) => ({
      componentId: row.component_id,
      operationCode: row.operation_code,
      projectTitle: row.project_title,
      description: row.description,
      category: row.category,
      state: row.state,
      cutoffDate: row.cutoff_date,
      approvedFundingEur: row.approved_funding_eur === null ? null : Number(row.approved_funding_eur),
      programme: row.programme,
      region: row.region,
      nutsCode: row.nuts_code,
    }));
  } catch {
    return null;
  }
}
