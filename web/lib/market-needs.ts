import "server-only";

import { procrunDb } from "@/lib/procrun-db";

export type MarketOverview = {
  fundedProjects: number;
  projectsWithComponents: number;
  assessedComponents: number;
  openComponents: number;
  closedComponents: number;
  unresolvedComponents: number;
  missingProgrammeProjects: number;
  missingFundingProjects: number;
  missingRegionProjects: number;
  earliestCutoffDate: string | null;
  latestCutoffDate: string | null;
};

export type MarketTrendPoint = {
  cutoffDate: string;
  assessedComponents: number;
  openComponents: number;
  closedComponents: number;
  unresolvedComponents: number;
};

export type OpenNeedsByCategory = {
  category: string;
  openNeeds: number;
  fundedProjects: number;
  earliestCutoffDate: string;
  latestCutoffDate: string;
};

export type ProgrammeConcentration = {
  category: string;
  totalOpenNeeds: number;
  openNeedsWithProgramme: number;
  topProgramme: string;
  topProgrammeOpenNeeds: number;
  topProgrammeSharePct: number;
};

export async function loadMarketOverview(): Promise<MarketOverview | null> {
  const activePool = procrunDb();
  if (!activePool) return null;

  try {
    const result = await activePool.query<{
      funded_projects: number;
      projects_with_components: number;
      assessed_components: number;
      open_components: number;
      closed_components: number;
      unresolved_components: number;
      missing_programme_projects: number;
      missing_funding_projects: number;
      missing_region_projects: number;
      earliest_cutoff_date: string | null;
      latest_cutoff_date: string | null;
    }>(`
      WITH latest_project AS (
        SELECT DISTINCT ON (operation_code)
          operation_code,
          approved_funding_eur,
          programme,
          region
        FROM procrun.funding_project_versions
        ORDER BY operation_code, as_of DESC, inserted_at DESC, version_id DESC
      ),
      latest_component AS (
        SELECT DISTINCT ON (component_id)
          component_id,
          operation_code
        FROM procrun.component_versions
        ORDER BY component_id, as_of DESC, inserted_at DESC, version_id DESC
      ),
      current_assessment AS (
        SELECT DISTINCT ON (component_id)
          component_id,
          operation_code,
          cutoff_date,
          state
        FROM procrun.assessment_versions
        ORDER BY
          component_id,
          cutoff_date DESC,
          as_of DESC,
          inserted_at DESC,
          version_id DESC
      ),
      project_component_scope AS (
        SELECT DISTINCT operation_code
        FROM latest_component
      )
      SELECT
        (SELECT count(*)::int FROM latest_project) AS funded_projects,
        (SELECT count(*)::int FROM project_component_scope) AS projects_with_components,
        (SELECT count(*)::int FROM current_assessment) AS assessed_components,
        (SELECT count(*)::int FROM current_assessment WHERE state = 'OPEN') AS open_components,
        (SELECT count(*)::int FROM current_assessment WHERE state = 'CLOSED') AS closed_components,
        (SELECT count(*)::int FROM current_assessment WHERE state = 'UNRESOLVED') AS unresolved_components,
        (
          SELECT count(*)::int
          FROM latest_project
          JOIN project_component_scope USING (operation_code)
          WHERE programme IS NULL
        ) AS missing_programme_projects,
        (
          SELECT count(*)::int
          FROM latest_project
          JOIN project_component_scope USING (operation_code)
          WHERE approved_funding_eur IS NULL
        ) AS missing_funding_projects,
        (
          SELECT count(*)::int
          FROM latest_project
          JOIN project_component_scope USING (operation_code)
          WHERE region IS NULL
        ) AS missing_region_projects,
        (SELECT min(cutoff_date)::text FROM current_assessment) AS earliest_cutoff_date,
        (SELECT max(cutoff_date)::text FROM current_assessment) AS latest_cutoff_date
    `);

    const row = result.rows[0];
    if (!row) return null;
    return {
      fundedProjects: row.funded_projects,
      projectsWithComponents: row.projects_with_components,
      assessedComponents: row.assessed_components,
      openComponents: row.open_components,
      closedComponents: row.closed_components,
      unresolvedComponents: row.unresolved_components,
      missingProgrammeProjects: row.missing_programme_projects,
      missingFundingProjects: row.missing_funding_projects,
      missingRegionProjects: row.missing_region_projects,
      earliestCutoffDate: row.earliest_cutoff_date,
      latestCutoffDate: row.latest_cutoff_date,
    };
  } catch {
    return null;
  }
}

export async function loadMarketTrend(): Promise<MarketTrendPoint[] | null> {
  const activePool = procrunDb();
  if (!activePool) return null;

  try {
    const result = await activePool.query<{
      cutoff_date: string;
      assessed_components: number;
      open_components: number;
      closed_components: number;
      unresolved_components: number;
    }>(`
      WITH recent_dates AS (
        SELECT cutoff_date
        FROM (
          SELECT DISTINCT cutoff_date
          FROM procrun.assessment_versions
          ORDER BY cutoff_date DESC
          LIMIT 30
        ) recent
      ),
      snapshot_ranked AS (
        SELECT
          recent_dates.cutoff_date AS snapshot_date,
          assessment_versions.component_id,
          assessment_versions.state,
          row_number() OVER (
            PARTITION BY recent_dates.cutoff_date, assessment_versions.component_id
            ORDER BY
              assessment_versions.cutoff_date DESC,
              assessment_versions.as_of DESC,
              assessment_versions.inserted_at DESC,
              assessment_versions.version_id DESC
          ) AS snapshot_rank
        FROM recent_dates
        JOIN procrun.assessment_versions
          ON assessment_versions.cutoff_date <= recent_dates.cutoff_date
      ),
      snapshot AS (
        SELECT snapshot_date, component_id, state
        FROM snapshot_ranked
        WHERE snapshot_rank = 1
      )
      SELECT
        snapshot_date::text AS cutoff_date,
        count(*)::int AS assessed_components,
        count(*) FILTER (WHERE state = 'OPEN')::int AS open_components,
        count(*) FILTER (WHERE state = 'CLOSED')::int AS closed_components,
        count(*) FILTER (WHERE state = 'UNRESOLVED')::int AS unresolved_components
      FROM snapshot
      GROUP BY snapshot_date
      ORDER BY snapshot_date
    `);

    return result.rows.map((row) => ({
      cutoffDate: row.cutoff_date,
      assessedComponents: row.assessed_components,
      openComponents: row.open_components,
      closedComponents: row.closed_components,
      unresolvedComponents: row.unresolved_components,
    }));
  } catch {
    return null;
  }
}

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
      WITH latest_component AS (
        SELECT DISTINCT ON (component_id)
          component_id,
          operation_code,
          category
        FROM procrun.component_versions
        ORDER BY component_id, as_of DESC, inserted_at DESC, version_id DESC
      ),
      current_assessment AS (
        SELECT DISTINCT ON (component_id)
          component_id,
          operation_code,
          cutoff_date,
          state
        FROM procrun.assessment_versions
        ORDER BY
          component_id,
          cutoff_date DESC,
          as_of DESC,
          inserted_at DESC,
          version_id DESC
      ),
      current_open AS (
        SELECT
          current_assessment.component_id,
          current_assessment.operation_code,
          current_assessment.cutoff_date,
          latest_component.category
        FROM current_assessment
        JOIN latest_component
          ON latest_component.component_id = current_assessment.component_id
         AND latest_component.operation_code = current_assessment.operation_code
        WHERE current_assessment.state = 'OPEN'
      )
      SELECT
        category,
        count(*)::int AS open_needs,
        count(DISTINCT operation_code)::int AS funded_projects,
        min(cutoff_date)::text AS earliest_cutoff_date,
        max(cutoff_date)::text AS latest_cutoff_date
      FROM current_open
      GROUP BY category
      ORDER BY open_needs DESC, funded_projects DESC, category
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
      WITH latest_component AS (
        SELECT DISTINCT ON (component_id)
          component_id,
          operation_code,
          category
        FROM procrun.component_versions
        ORDER BY component_id, as_of DESC, inserted_at DESC, version_id DESC
      ),
      current_assessment AS (
        SELECT DISTINCT ON (component_id)
          component_id,
          operation_code,
          state
        FROM procrun.assessment_versions
        ORDER BY
          component_id,
          cutoff_date DESC,
          as_of DESC,
          inserted_at DESC,
          version_id DESC
      ),
      latest_project AS (
        SELECT DISTINCT ON (operation_code)
          operation_code,
          programme
        FROM procrun.funding_project_versions
        ORDER BY operation_code, as_of DESC, inserted_at DESC, version_id DESC
      ),
      current_open AS (
        SELECT
          current_assessment.component_id,
          current_assessment.operation_code,
          latest_component.category,
          latest_project.programme
        FROM current_assessment
        JOIN latest_component
          ON latest_component.component_id = current_assessment.component_id
         AND latest_component.operation_code = current_assessment.operation_code
        LEFT JOIN latest_project
          ON latest_project.operation_code = current_assessment.operation_code
        WHERE current_assessment.state = 'OPEN'
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
        SELECT category, programme, count(*)::int AS programme_open_needs
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
