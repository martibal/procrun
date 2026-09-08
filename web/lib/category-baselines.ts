import "server-only";

import { procrunDb } from "@/lib/procrun-db";

export const MIN_CATEGORY_BASELINE_N = 20;

export type CategoryBaseline = {
  category: string;
  n: number;
  p25Days: number;
  medianDays: number;
  p75Days: number;
  earliestOpenedAt: string;
  latestClosedAt: string;
};

export async function loadCategoryBaselines(): Promise<CategoryBaseline[] | null> {
  const activePool = procrunDb();
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
      HAVING count(*) >= ${MIN_CATEGORY_BASELINE_N}
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

export type OpenCategoryPercentile = {
  componentId: string;
  category: string;
  openedAt: string;
  asOfDate: string;
  currentAgeDays: number;
  n: number;
  percentile: number;
};

export async function loadOpenCategoryPercentile(
  componentId: string,
  asOfDate: string,
): Promise<OpenCategoryPercentile | null> {
  const activePool = procrunDb();
  if (!activePool) return null;

  try {
    const result = await activePool.query<{
      category: string;
      opened_at: string;
      current_age_days: number;
      duration_days: number | null;
    }>(`
      WITH latest_component AS (
        SELECT DISTINCT ON (component_id)
          component_id,
          category
        FROM procrun.component_versions
        ORDER BY component_id, as_of DESC, inserted_at DESC
      ),
      effective_observation AS (
        SELECT o.*
        FROM procrun.procurement_observations o
        WHERE o.observed_at::date <= $2::date
          AND NOT EXISTS (
            SELECT 1
            FROM procrun.procurement_observations correction
            WHERE correction.correction_of_id = o.id
          )
      ),
      ordered_target AS (
        SELECT
          o.*,
          lag(o.state) OVER (
            PARTITION BY o.component_id
            ORDER BY o.observed_at, o.inserted_at, o.id
          ) AS previous_state
        FROM effective_observation o
        WHERE o.component_id = $1
      ),
      current_state AS (
        SELECT state
        FROM ordered_target
        ORDER BY observed_at DESC, inserted_at DESC, id DESC
        LIMIT 1
      ),
      current_open AS (
        SELECT max(observed_at)::date AS opened_at
        FROM ordered_target
        WHERE state = 'OPEN'
          AND previous_state IS DISTINCT FROM 'OPEN'
      ),
      first_open AS (
        SELECT component_id, min(observed_at) AS opened_at
        FROM effective_observation
        WHERE state = 'OPEN'
        GROUP BY component_id
      ),
      first_close AS (
        SELECT
          first_open.component_id,
          min(o.observed_at) AS closed_at
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
          (first_close.closed_at - first_open.opened_at)::int AS duration_days
        FROM first_open
        JOIN first_close USING (component_id)
        JOIN latest_component USING (component_id)
      ),
      target_component AS (
        SELECT component_id, category
        FROM latest_component
        WHERE component_id = $1
      )
      SELECT
        target_component.category,
        current_open.opened_at::text AS opened_at,
        ($2::date - current_open.opened_at)::int AS current_age_days,
        durations.duration_days
      FROM target_component
      CROSS JOIN current_state
      CROSS JOIN current_open
      LEFT JOIN durations
        ON durations.category = target_component.category
      WHERE current_state.state = 'OPEN'
        AND current_open.opened_at IS NOT NULL
      ORDER BY durations.duration_days NULLS LAST
    `, [componentId, asOfDate]);

    if (result.rows.length === 0) return null;

    const first = result.rows[0];
    const durations = result.rows
      .map((row) => row.duration_days)
      .filter((value): value is number => value !== null);

    if (durations.length < MIN_CATEGORY_BASELINE_N) return null;
    if (first.current_age_days < 0) return null;

    const below = durations.filter(
      (duration) => duration < first.current_age_days,
    ).length;

    const equal = durations.filter(
      (duration) => duration === first.current_age_days,
    ).length;

    const percentile = Math.max(
      0,
      Math.min(
        100,
        ((below + 0.5 * equal) / durations.length) * 100,
      ),
    );

    return {
      componentId,
      category: first.category,
      openedAt: first.opened_at,
      asOfDate,
      currentAgeDays: first.current_age_days,
      n: durations.length,
      percentile,
    };
  } catch {
    return null;
  }
}
