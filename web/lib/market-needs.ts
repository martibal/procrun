import "server-only";

import { procrunDb } from "@/lib/procrun-db";

export type OpenNeedsByCategory = {
  category: string;
  openNeeds: number;
  fundedProjects: number;
  earliestCutoffDate: string;
  latestCutoffDate: string;
};

export async function loadOpenNeedsByCategory(): Promise<OpenNeedsByCategory[] | null> {
  const activePool = procrunDb();
  if (!activePool) return null;

  try {
    const result = await activePool.query<{
      category: string;
      open_needs: number;
      funded_projects: number;
      earliest_cutoff_date: string;
      latest_cutoff_date: string;
    }>(`
      WITH effective_observation AS (
        SELECT o.*
        FROM procrun.procurement_observations o
        WHERE NOT EXISTS (
          SELECT 1
          FROM procrun.procurement_observations correction
          WHERE correction.correction_of_id = o.id
        )
      ),
      current_observation AS (
        SELECT DISTINCT ON (component_id)
          component_id,
          operation_code,
          observed_at,
          state
        FROM effective_observation
        ORDER BY
          component_id,
          observed_at DESC,
          inserted_at DESC,
          id DESC
      ),
      latest_component AS (
        SELECT DISTINCT ON (component_id)
          component_id,
          operation_code,
          category
        FROM procrun.component_versions
        ORDER BY
          component_id,
          as_of DESC,
          inserted_at DESC,
          version_id DESC
      ),
      current_open AS (
        SELECT
          current_observation.component_id,
          current_observation.operation_code,
          current_observation.observed_at,
          latest_component.category
        FROM current_observation
        JOIN latest_component
          ON latest_component.component_id = current_observation.component_id
         AND latest_component.operation_code = current_observation.operation_code
        WHERE current_observation.state = 'OPEN'
      )
      SELECT
        category,
        count(*)::int AS open_needs,
        count(DISTINCT operation_code)::int AS funded_projects,
        min(observed_at)::text AS earliest_cutoff_date,
        max(observed_at)::text AS latest_cutoff_date
      FROM current_open
      GROUP BY category
      ORDER BY
        open_needs DESC,
        funded_projects DESC,
        category
    `);

    return result.rows.map((row) => ({
      category: row.category,
      openNeeds: row.open_needs,
      fundedProjects: row.funded_projects,
      earliestCutoffDate: row.earliest_cutoff_date,
      latestCutoffDate: row.latest_cutoff_date,
    }));
  } catch {
    return null;
  }
}