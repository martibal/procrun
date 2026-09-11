import { readFile } from "node:fs/promises";
import path from "node:path";
import {
  parseRunwayProject,
  toOpportunities,
  type Opportunity,
  type ProcurementMatch,
  type RunwayProject,
} from "./published-data";

export type CustomerOpportunity = Opportunity & {
  interpretation: string;
  projectState: RunwayProject["state"];
  projectStart: string | null;
  projectEnd: string | null;
  programme: string | null;
  sourceUrl: string;
  contentHash: string;
  orchestrationVersion: string;
  componentRuleVersion: string;
  matchRuleVersion: string;
  projectClassifierVersion: string;
  readModelVersion: string;
  procurementMatches: ProcurementMatch[];
};

export type CustomerView = {
  mode: "live" | "missing";
  snapshotPath: string;
  cutoffDate: string | null;
  projects: RunwayProject[];
  opportunities: CustomerOpportunity[];
};

export function defaultCustomerSnapshotPath(): string {
  return process.env.PROCRUN_PUBLISHED_JSONL_PATH ?? path.resolve(process.cwd(), "data", "customer-runway.jsonl");
}

export function buildCustomerOpportunities(projects: readonly RunwayProject[]): CustomerOpportunity[] {
  const byProject = new Map(projects.map((project) => [project.operation_code, project]));
  const items = toOpportunities(projects);
  const enriched = items.map((item): CustomerOpportunity => {
    const project = byProject.get(item.projectId);
    if (!project) throw new Error(`customer opportunity references missing project: ${item.projectId}`);
    const component = item.componentId
      ? project.components.find((candidate) => candidate.component_id === item.componentId)
      : undefined;
    if (item.componentId && !component) {
      throw new Error(`customer opportunity references missing component: ${item.componentId}`);
    }
    return {
      ...item,
      interpretation:
        component?.state_explanation ??
        "No bounded purchase component was emitted for this project under the frozen production rules. The project remains UNRESOLVED and the exact admitted source wording is shown.",
      projectState: project.state,
      projectStart: project.project_start,
      projectEnd: project.project_end,
      programme: project.programme,
      sourceUrl: project.source_url,
      contentHash: project.content_hash,
      orchestrationVersion: project.orchestration_version,
      componentRuleVersion: project.component_rule_version,
      matchRuleVersion: project.match_rule_version,
      projectClassifierVersion: project.project_classifier_version,
      readModelVersion: project.read_model_version,
      procurementMatches: component?.procurement_matches ?? [],
    };
  });
  const represented = new Set(enriched.map((item) => item.projectId));
  if (represented.size !== projects.length) {
    throw new Error(`customer view omitted projects: represented=${represented.size}, projects=${projects.length}`);
  }
  return enriched;
}

export async function loadCustomerView(): Promise<CustomerView> {
  const snapshotPath = defaultCustomerSnapshotPath();
  let body: string;
  try {
    body = await readFile(snapshotPath, "utf8");
  } catch (error) {
    const code = (error as NodeJS.ErrnoException).code;
    if (code === "ENOENT") {
      return { mode: "missing", snapshotPath, cutoffDate: null, projects: [], opportunities: [] };
    }
    throw error;
  }
  const lines = body.split(/\r?\n/).filter((line) => line.trim());
  if (!lines.length) throw new Error("published customer runway snapshot is empty");
  const projects = lines.map((line) => parseRunwayProject(JSON.parse(line) as unknown));
  const opportunities = buildCustomerOpportunities(projects);
  const cutoffDates = [...new Set(projects.map((project) => project.cutoff_date))].sort();
  return {
    mode: "live",
    snapshotPath,
    cutoffDate: cutoffDates.at(-1) ?? null,
    projects,
    opportunities,
  };
}
