import "server-only";

import { procrunDb } from "@/lib/procrun-db";

export type ProjectNeedState = "OPEN" | "CLOSED" | "UNRESOLVED";

export type ProductionProjectNeed = {
  category: string;
  description: string;
  scopeEvidence: string;
  state: ProjectNeedState;
  cutoffDate: string;
};

export type ProductionProjectSummary = {
  operationCode: string;
  projectTitle: string | null;
  projectStart: string | null;
  projectEnd: string | null;
  approvedFundingEur: number | null;
  programme: string | null;
  region: string | null;
  nutsCode: string | null;
  categories: string[];
  needs: ProductionProjectNeed[];
  componentCount: number;
  openCount: number;
  closedCount: number;
  unresolvedCount: number;
  earliestCutoffDate: string;
  latestCutoffDate: string;
};

export type ProductionProjectComponent = ProductionProjectNeed & {
  componentId: string;
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
  nutsCode: string | null;
  projectScopeText: string;
  components: ProductionProjectComponent[];
};

type RawNeed = ProductionProjectNeed;

type RawComponent = ProductionProjectComponent;

function canonicalCategory(categories: string[], description: string): string {
  const unique = Array.from(new Set(categories));
  if (unique.length === 1) return unique[0];

  const leaves = Array.from(
    new Set(unique.map((category) => category.split(":").at(-1) ?? category)),
  );
  if (leaves.length === 1) return `general:${leaves[0]}`;

  return `general:${description.toLocaleLowerCase().replace(/[^a-z0-9]+/g, "_").replace(/^_+|_+$/g, "") || "need"}`;
}

function normalizeNeeds(rows: RawNeed[]): ProductionProjectNeed[] {
  const grouped = new Map<string, RawNeed[]>();

  for (const row of rows) {
    const key = [
      row.description.trim().toLocaleLowerCase(),
      row.scopeEvidence.trim().toLocaleLowerCase(),
      row.state,
      row.cutoffDate,
    ].join("\u0000");
    const group = grouped.get(key) ?? [];
    group.push(row);
    grouped.set(key, group);
  }

  return Array.from(grouped.values())
    .map((group) => ({
      ...group[0],
      category: canonicalCategory(group.map((item) => item.category), group[0].description),
    }))
    .sort((a, b) => {
      const rank = { OPEN: 0, UNRESOLVED: 1, CLOSED: 2 } as const;
      return rank[a.state] - rank[b.state]
        || a.description.localeCompare(b.description)
        || a.category.localeCompare(b.category);
    });
}

function normalizeComponents(rows: RawComponent[]): ProductionProjectComponent[] {
  const grouped = new Map<string, RawComponent[]>();

  for (const row of rows) {
    const key = [
      row.description.trim().toLocaleLowerCase(),
      row.scopeEvidence.trim().toLocaleLowerCase(),
      row.state,
      row.cutoffDate,
      row.evidenceReference ?? "",
      row.evidenceUrl ?? "",
      row.evidenceExcerpt ?? "",
    ].join("\u0000");
    const group = grouped.get(key) ?? [];
    group.push(row);
    grouped.set(key, group);
  }

  return Array.from(grouped.values())
    .map((group) => ({
      ...group[0],
      category: canonicalCategory(group.map((item) => item.category), group[0].description),
    }))
    .sort((a, b) => {
      const rank = { OPEN: 0, UNRESOLVED: 1, CLOSED: 2 } as const;
      return rank[a.state] - rank[b.state]
        || a.description.localeCompare(b.description)
        || a.category.localeCompare(b.category);
    });
}

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
      nuts_code: string | null;
      raw_needs: Array<{
        category: string;
        description: string;
        scopeEvidence: string;
        state: ProjectNeedState;
        cutoffDate: string;
      }>;
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
          nuts_code
        FROM procrun.funding_project_versions
        ORDER BY operation_code, as_of DESC, inserted_at DESC, version_id DESC
      ),
      latest_component AS (
        SELECT DISTINCT ON (component_id)
          component_id,
          operation_code,
          category,
          description,
          scope_evidence
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
      current_components AS (
        SELECT
          latest_component.component_id,
          latest_component.operation_code,
          latest_component.category,
          latest_component.description,
          latest_component.scope_evidence,
          current_assessment.cutoff_date,
          current_assessment.state
        FROM latest_component
        JOIN current_assessment
          ON current_assessment.component_id = latest_component.component_id
         AND current_assessment.operation_code = latest_component.operation_code
      )
      SELECT
        latest_project.operation_code,
        latest_project.project_title,
        latest_project.project_start::text,
        latest_project.project_end::text,
        latest_project.approved_funding_eur,
        latest_project.programme,
        latest_project.region,
        latest_project.nuts_code,
        jsonb_agg(
          jsonb_build_object(
            'category', current_components.category,
            'description', current_components.description,
            'scopeEvidence', current_components.scope_evidence,
            'state', current_components.state,
            'cutoffDate', current_components.cutoff_date::text
          )
          ORDER BY current_components.state, current_components.description, current_components.category
        ) AS raw_needs
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
        latest_project.nuts_code
      ORDER BY latest_project.project_title NULLS LAST, latest_project.operation_code
    `);

    return result.rows
      .map((row) => {
        const needs = normalizeNeeds(row.raw_needs ?? []);
        const cutoffDates = needs.map((item) => item.cutoffDate).sort();
        return {
          operationCode: row.operation_code,
          projectTitle: row.project_title,
          projectStart: row.project_start,
          projectEnd: row.project_end,
          approvedFundingEur: row.approved_funding_eur === null ? null : Number(row.approved_funding_eur),
          programme: row.programme,
          region: row.region,
          nutsCode: row.nuts_code,
          categories: Array.from(new Set(needs.map((item) => item.category))).sort(),
          needs,
          componentCount: needs.length,
          openCount: needs.filter((item) => item.state === "OPEN").length,
          closedCount: needs.filter((item) => item.state === "CLOSED").length,
          unresolvedCount: needs.filter((item) => item.state === "UNRESOLVED").length,
          earliestCutoffDate: cutoffDates[0] ?? "Unavailable",
          latestCutoffDate: cutoffDates.at(-1) ?? "Unavailable",
        } satisfies ProductionProjectSummary;
      })
      .sort((a, b) =>
        b.openCount - a.openCount
        || b.componentCount - a.componentCount
        || (a.projectTitle ?? a.operationCode).localeCompare(b.projectTitle ?? b.operationCode),
      );
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
        nuts_code,
        project_scope_text
      FROM procrun.funding_project_versions
      WHERE operation_code = $1
      ORDER BY as_of DESC, inserted_at DESC, version_id DESC
      LIMIT 1
    `, [operationCode]);

    if (projectResult.rows.length === 0) return null;

    const componentResult = await activePool.query<{
      component_id: string;
      category: string;
      description: string;
      scope_evidence: string;
      state: ProjectNeedState;
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
        ORDER BY component_id, as_of DESC, inserted_at DESC, version_id DESC
      ),
      effective_observation AS (
        SELECT
          o.id,
          o.component_id,
          o.operation_code,
          o.observed_at,
          o.state,
          o.evidence_reference,
          o.evidence_url,
          o.evidence_excerpt,
          o.coverage_note,
          o.inserted_at,
          o.correction_of_id
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
        ORDER BY component_id, observed_at DESC, inserted_at DESC, id DESC
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
      ORDER BY latest_component.description, latest_component.category
    `, [operationCode]);

    if (componentResult.rows.length === 0) return null;

    const project = projectResult.rows[0];
    const components = normalizeComponents(componentResult.rows.map((row) => ({
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
    })));

    return {
      operationCode: project.operation_code,
      projectTitle: project.project_title,
      projectStart: project.project_start,
      projectEnd: project.project_end,
      approvedFundingEur: project.approved_funding_eur === null ? null : Number(project.approved_funding_eur),
      executedFundingEur: project.executed_funding_eur === null ? null : Number(project.executed_funding_eur),
      programme: project.programme,
      fund: project.fund,
      objective: project.objective,
      theme: project.theme,
      region: project.region,
      nutsCode: project.nuts_code,
      projectScopeText: project.project_scope_text,
      components,
    };
  } catch {
    return null;
  }
}
