import "server-only";

import { procrunDb } from "@/lib/procrun-db";

export type ProductionProjectSummary = {
  operationCode: string;
  projectTitle: string | null;
  projectStart: string | null;
  projectEnd: string | null;
  approvedFundingEur: number | null;
  programme: string | null;
  region: string | null;
  municipality: string | null;
  nutsCode: string | null;
  componentCount: number;
  openCount: number;
  closedCount: number;
  unresolvedCount: number;
  earliestCutoffDate: string;
  latestCutoffDate: string;
};

export type ProductionProjectComponent = {
  componentId: string;
  category: string;
  description: string;
  scopeEvidence: string;
  state: "OPEN" | "CLOSED" | "UNRESOLVED";
  cutoffDate: string;
  coverageNote: string;
  evidenceReference: string | null;
  evidenceUrl: string | null;
  evidenceExcerpt: string | null;
};

export type ProductionProjectDetail = {
  operationCode: string;
  projectTitle: string | null;
  projectStart: string | null;
  projectEnd: string | null;
  approvedFundingEur: number | null;
  executedFundingEur: number | null;
  programme: string | null;
  fund: string | null;
  objective: string | null;
  theme: string | null;
  region: string | null;
  municipality: string | null;
  nutsCode: string | null;
  projectScopeText: string;
  components: ProductionProjectComponent[];
};

export async function loadProductionProjects(): Promise<ProductionProjectSummary[] | null> {
  const activePool = procrunDb();
  if (!activePool) return null;

  try {
    const result = await activePool.query<{
      operation_code: string;
      project_title: string | null;
      project_start: string | null;
      project_end: string | null;
      approved_funding_eur: string | number | null;
      programme: string | null;
      region: string | null;
      municipality: string | null;
      nuts_code: string | null;
      component_count: number;
      open_count: number;
      closed_count: number;
      unresolved_count: number;
      earliest_cutoff_date: string;
      latest_cutoff_date: string;
    }>(`
      WITH latest_project AS (
        SELECT DISTINCT ON (operation_code)
          operation_code,
          project_title,
          project_start,
          project_end,
          approved_funding_eur,
          programme,
          region,
          municipality,
          nuts_code
        FROM procrun.funding_project_versions
        ORDER BY
          operation_code,
          as_of DESC,
          inserted_at DESC,
          version_id DESC
      ),
      latest_component AS (
        SELECT DISTINCT ON (component_id)
          component_id,
          operation_code,
          category,
          description
        FROM procrun.component_versions
        ORDER BY
          component_id,
          as_of DESC,
          inserted_at DESC,
          version_id DESC
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
      current_components AS (
        SELECT
          latest_component.component_id,
          latest_component.operation_code,
          current_observation.observed_at,
          current_observation.state
        FROM latest_component
        JOIN current_observation
          ON current_observation.component_id = latest_component.component_id
         AND current_observation.operation_code = latest_component.operation_code
      )
      SELECT
        latest_project.operation_code,
        latest_project.project_title,
        latest_project.project_start::text,
        latest_project.project_end::text,
        latest_project.approved_funding_eur,
        latest_project.programme,
        latest_project.region,
        latest_project.municipality,
        latest_project.nuts_code,
        count(*)::int AS component_count,
        count(*) FILTER (WHERE current_components.state = 'OPEN')::int AS open_count,
        count(*) FILTER (WHERE current_components.state = 'CLOSED')::int AS closed_count,
        count(*) FILTER (WHERE current_components.state = 'UNRESOLVED')::int AS unresolved_count,
        min(current_components.observed_at)::text AS earliest_cutoff_date,
        max(current_components.observed_at)::text AS latest_cutoff_date
      FROM current_components
      JOIN latest_project
        ON latest_project.operation_code = current_components.operation_code
      GROUP BY
        latest_project.operation_code,
        latest_project.project_title,
        latest_project.project_start,
        latest_project.project_end,
        latest_project.approved_funding_eur,
        latest_project.programme,
        latest_project.region,
        latest_project.municipality,
        latest_project.nuts_code
      ORDER BY
        open_count DESC,
        component_count DESC,
        latest_project.project_title NULLS LAST,
        latest_project.operation_code
    `);

    return result.rows.map((row) => ({
      operationCode: row.operation_code,
      projectTitle: row.project_title,
      projectStart: row.project_start,
      projectEnd: row.project_end,
      approvedFundingEur:
        row.approved_funding_eur === null
          ? null
          : Number(row.approved_funding_eur),
      programme: row.programme,
      region: row.region,
      municipality: row.municipality,
      nutsCode: row.nuts_code,
      componentCount: row.component_count,
      openCount: row.open_count,
      closedCount: row.closed_count,
      unresolvedCount: row.unresolved_count,
      earliestCutoffDate: row.earliest_cutoff_date,
      latestCutoffDate: row.latest_cutoff_date,
    }));
  } catch {
    return null;
  }
}

export async function loadProductionProject(
  operationCode: string,
): Promise<ProductionProjectDetail | null> {
  const activePool = procrunDb();
  if (!activePool) return null;

  try {
    const projectResult = await activePool.query<{
      operation_code: string;
      project_title: string | null;
      project_start: string | null;
      project_end: string | null;
      approved_funding_eur: string | number | null;
      executed_funding_eur: string | number | null;
      programme: string | null;
      fund: string | null;
      objective: string | null;
      theme: string | null;
      region: string | null;
      municipality: string | null;
      nuts_code: string | null;
      project_scope_text: string;
    }>(`
      SELECT
        operation_code,
        project_title,
        project_start::text,
        project_end::text,
        approved_funding_eur,
        executed_funding_eur,
        programme,
        fund,
        objective,
        theme,
        region,
        municipality,
        nuts_code,
        project_scope_text
      FROM procrun.funding_project_versions
      WHERE operation_code = $1
      ORDER BY
        as_of DESC,
        inserted_at DESC,
        version_id DESC
      LIMIT 1
    `, [operationCode]);

    if (projectResult.rows.length === 0) return null;

    const componentResult = await activePool.query<{
      component_id: string;
      category: string;
      description: string;
      scope_evidence: string;
      state: "OPEN" | "CLOSED" | "UNRESOLVED";
      cutoff_date: string;
      coverage_note: string;
      evidence_reference: string | null;
      evidence_url: string | null;
      evidence_excerpt: string | null;
    }>(`
      WITH latest_component AS (
        SELECT DISTINCT ON (component_id)
          component_id,
          operation_code,
          category,
          description,
          scope_evidence
        FROM procrun.component_versions
        WHERE operation_code = $1
        ORDER BY
          component_id,
          as_of DESC,
          inserted_at DESC,
          version_id DESC
      ),
      effective_observation AS (
        SELECT o.*
        FROM procrun.procurement_observations o
        WHERE o.operation_code = $1
          AND NOT EXISTS (
            SELECT 1
            FROM procrun.procurement_observations correction
            WHERE correction.correction_of_id = o.id
          )
      ),
      current_observation AS (
        SELECT DISTINCT ON (component_id)
          component_id,
          observed_at,
          state,
          evidence_reference,
          evidence_url,
          evidence_excerpt,
          coverage_note
        FROM effective_observation
        ORDER BY
          component_id,
          observed_at DESC,
          inserted_at DESC,
          id DESC
      )
      SELECT
        latest_component.component_id,
        latest_component.category,
        latest_component.description,
        latest_component.scope_evidence,
        current_observation.state,
        current_observation.observed_at::text AS cutoff_date,
        current_observation.coverage_note,
        current_observation.evidence_reference,
        current_observation.evidence_url,
        current_observation.evidence_excerpt
      FROM latest_component
      JOIN current_observation USING (component_id)
      ORDER BY
        CASE current_observation.state
          WHEN 'OPEN' THEN 1
          WHEN 'CLOSED' THEN 2
          ELSE 3
        END,
        latest_component.category,
        latest_component.description,
        latest_component.component_id
    `, [operationCode]);

    if (componentResult.rows.length === 0) return null;

    const project = projectResult.rows[0];

    return {
      operationCode: project.operation_code,
      projectTitle: project.project_title,
      projectStart: project.project_start,
      projectEnd: project.project_end,
      approvedFundingEur:
        project.approved_funding_eur === null
          ? null
          : Number(project.approved_funding_eur),
      executedFundingEur:
        project.executed_funding_eur === null
          ? null
          : Number(project.executed_funding_eur),
      programme: project.programme,
      fund: project.fund,
      objective: project.objective,
      theme: project.theme,
      region: project.region,
      municipality: project.municipality,
      nutsCode: project.nuts_code,
      projectScopeText: project.project_scope_text,
      components: componentResult.rows.map((row) => ({
        componentId: row.component_id,
        category: row.category,
        description: row.description,
        scopeEvidence: row.scope_evidence,
        state: row.state,
        cutoffDate: row.cutoff_date,
        coverageNote: row.coverage_note,
        evidenceReference: row.evidence_reference,
        evidenceUrl: row.evidence_url,
        evidenceExcerpt: row.evidence_excerpt,
      })),
    };
  } catch {
    return null;
  }
}