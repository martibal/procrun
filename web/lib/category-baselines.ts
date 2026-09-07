import "server-only";

import { Pool } from "pg";

export type CategoryBaseline = {
  category: string;
  n: number;
  p25Days: number;
  medianDays: number;
  p75Days: number;
  earliestOpenedAt: string;
  latestClosedAt: string;
};

const databaseUrl = process.env.PROCRUN_DATABASE_URL;
let pool: Pool | undefined;

function db(): Pool | undefined {
  if (!databaseUrl) return undefined;
  pool ??= new Pool({ connectionString: databaseUrl, max: 3 });
  return pool;
}

export async function loadCategoryBaselines(): Promise<CategoryBaseline[] | null> {
  const activePool = db();
  if (!activePool) return null;

  try {
    const result = await activePool.query<{
      category: string;
      n: number;
      p25_days: number;
      median_days: number;
      p75_days: number;
      earliest_opened_at: string;
      latest_closed_at: string;
    }>(`
      WITH latest_component AS (
        SELECT DISTINCT ON (component_id)
          component_id, category
        FROM procrun.component_versions
        ORDER BY component_id, as_of DESC, inserted_at DESC
      ),
      effective_observation AS (
        SELECT o.*
        FROM procrun.procurement_observations o
        WHERE NOT EXISTS (
          SELECT 1
          FROM procrun.procurement_observations correction
          WHERE correction.correction_of_id = o.id
        )
      ),
      first_open AS (
        SELECT component_id, min(observed_at) AS opened_at
        FROM effective_observation
        WHERE state = 'OPEN'
        GROUP BY component_id
      ),
      first_close AS (
        SELECT first_open.component_id, min(o.observed_at) AS closed_at
        FROM first_open
        JOIN effective_observation o
          ON o.component_id = first_open.component_id
         AND o.state = 'CLOSED'
         AND o.observed_at >= first_open.opened_at
        GROUP BY first_open.component_id
      ),
      durations AS (
        SELECT
          latest_component.category,
          first_open.opened_at,
          first_close.closed_at,
          (first_close.closed_at - first_open.opened_at)::int AS duration_days
        FROM first_open
        JOIN first_close USING (component_id)
        JOIN latest_component USING (component_id)
      )
      SELECT
        category,
        count(*)::int AS n,
        percentile_cont(0.25) WITHIN GROUP (ORDER BY duration_days)::float8 AS p25_days,
        percentile_cont(0.50) WITHIN GROUP (ORDER BY duration_days)::float8 AS median_days,
        percentile_cont(0.75) WITHIN GROUP (ORDER BY duration_days)::float8 AS p75_days,
        min(opened_at)::text AS earliest_opened_at,
        max(closed_at)::text AS latest_closed_at
      FROM durations
      GROUP BY category
      ORDER BY category
    `);

    return result.rows.map((row) => ({
      category: row.category,
      n: row.n,
      p25Days: row.p25_days,
      medianDays: row.median_days,
      p75Days: row.p75_days,
      earliestOpenedAt: row.earliest_opened_at,
      latestClosedAt: row.latest_closed_at,
    }));
  } catch {
    return null;
  }
}
