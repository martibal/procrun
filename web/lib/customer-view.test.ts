import { describe, expect, it } from "vitest";
import { buildCustomerOpportunities } from "./customer-view";
import type { RunwayProject } from "./published-data";

function project(overrides: Partial<RunwayProject> = {}): RunwayProject {
  return {
    operation_code: "op-1",
    project_title: "Water project",
    project_start: "2025-01-01",
    project_end: "2027-01-01",
    approved_funding_eur: 1000000,
    programme: "Programme",
    region: "Lombardia",
    nuts_code: "ITC4",
    source_url: "https://example.invalid/project",
    source_evidence: {
      source_type: "Project description",
      source_field: "project_scope_text",
      text: "Install pumps",
      start: 0,
      end: 13,
      source_url: "https://example.invalid/project",
    },
    state: "UNRESOLVED",
    cutoff_date: "2026-09-11",
    components: [],
    unresolved_source_evidence: [
      { source_field: "project_scope_text", text: "Install pumps", start: 0, end: 13 },
    ],
    orchestration_version: "orchestration-v1",
    component_rule_version: "component-v1",
    match_rule_version: "match-v1",
    project_classifier_version: "project-v1",
    read_model_version: "customer-runway-v4",
    content_hash: "abc123",
    ...overrides,
  };
}

describe("customer view", () => {
  it("keeps component-free projects visible with customer-facing UNRESOLVED wording", () => {
    const rows = buildCustomerOpportunities([project()]);
    expect(rows).toHaveLength(1);
    expect(rows[0].projectId).toBe("op-1");
    expect(rows[0].state).toBe("UNRESOLVED");
    expect(rows[0].projectEvidence).toBe("Install pumps");
    expect(rows[0].interpretation).toContain("does not identify a purchasing need clearly enough");
    expect(rows[0].interpretation).not.toContain("bounded");
    expect(rows[0].interpretation).not.toContain("frozen");
  });

  it("translates OPEN state into customer-facing wording without internal rule jargon", () => {
    const rows = buildCustomerOpportunities([
      project({
        state: "OPEN",
        unresolved_source_evidence: [],
        components: [
          {
            component_id: "cmp-1",
            category: "water:pumps",
            label: "Pumping systems",
            state: "OPEN",
            cutoff_date: "2026-09-11",
            project_evidence: { source_field: "project_scope_text", text: "Install pumps", start: 0, end: 13 },
            procurement_matches: [],
            coverage_note: "Complete TED coverage",
            state_explanation: "No procurement match satisfying ProcRun's frozen exact-evidence rules was found in TED as of 2026-09-11.",
          },
        ],
      }),
    ]);
    expect(rows).toHaveLength(1);
    expect(rows[0].componentId).toBe("cmp-1");
    expect(rows[0].interpretation).toContain("no matching procurement notice in TED");
    expect(rows[0].interpretation).not.toContain("frozen exact-evidence rules");
  });
});
