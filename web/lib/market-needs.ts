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

export type ProgrammeConcentration = {
  category: string;
  totalOpenNeeds: number;
  openNeedsWithProgramme: number;
  topProgramme: string;
  topProgrammeOpenNeeds: number;
  topProgrammeSharePct: number;
};

export async function loadProgrammeConcentration(): Promise<ProgrammeConcentration[] | null> {
  const activePool = procrunDb();
  if (!activePool) return null;

  try {
    const result = await activePool.query<{
      category: string;
      total_open_needs: number;
      open_needs_with_programme: number;
      top_programme: string;
      top_programme_open_needs: number;
      top_programme_share_pct: number;
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
      latest_project AS (
        SELECT DISTINCT ON (operation_code)
          operation_code,
          programme
        FROM procrun.funding_project_versions
        ORDER BY
          operation_code,
          as_of DESC,
          inserted_at DESC,
          version_id DESC
      ),
      current_open AS (
        SELECT
          current_observation.component_id,
          current_observation.operation_code,
          latest_component.category,
          latest_project.programme
        FROM current_observation
        JOIN latest_component
          ON latest_component.component_id = current_observation.component_id
         AND latest_component.operation_code = current_observation.operation_code
        LEFT JOIN latest_project
          ON latest_project.operation_code = current_observation.operation_code
        WHERE current_observation.state = 'OPEN'
      ),
      category_totals AS (
        SELECT
          category,
          count(*)::int AS total_open_needs,
          count(*) FILTER (WHERE programme IS NOT NULL)::int AS open_needs_with_programme
        FROM current_open
        GROUP BY category
      ),
      programme_counts AS (
        SELECT
          category,
          programme,
          count(*)::int AS programme_open_needs
        FROM current_open
        WHERE programme IS NOT NULL
        GROUP BY category, programme
      ),
      ranked AS (
        SELECT
          category,
          programme,
          programme_open_needs,
          row_number() OVER (
            PARTITION BY category
            ORDER BY programme_open_needs DESC, programme
          ) AS rank_in_category
        FROM programme_counts
      )
      SELECT
        category_totals.category,
        category_totals.total_open_needs,
        category_totals.open_needs_with_programme,
        ranked.programme AS top_programme,
        ranked.programme_open_needs AS top_programme_open_needs,
        (
          ranked.programme_open_needs::float8
          / NULLIF(category_totals.open_needs_with_programme, 0)::float8
          * 100.0
        )::float8 AS top_programme_share_pct
      FROM category_totals
      JOIN ranked
        ON ranked.category = category_totals.category
       AND ranked.rank_in_category = 1
      ORDER BY
        top_programme_share_pct DESC,
        category_totals.total_open_needs DESC,
        category_totals.category
    `);

    return result.rows.map((row) => ({
      category: row.category,
      totalOpenNeeds: row.total_open_needs,
      openNeedsWithProgramme: row.open_needs_with_programme,
      topProgramme: row.top_programme,
      topProgrammeOpenNeeds: row.top_programme_open_needs,
      topProgrammeSharePct: row.top_programme_share_pct,
    }));
  } catch {
    return null;
  }
}
