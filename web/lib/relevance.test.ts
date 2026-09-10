import { describe, expect, it } from "vitest";
import { scoreOpportunity } from "./relevance";
import type { Opportunity } from "./published-data";

const opportunity: Opportunity = {
  id: "OP-1:cmp-1",
  projectId: "OP-1",
  projectTitle: "Energy retrofit",
  componentId: "cmp-1",
  componentCategory: "energy_efficiency:photovoltaic",
  component: "Photovoltaic systems",
  state: "UNRESOLVED",
  cutoffDate: "2026-09-10",
  coverage: "TED",
  projectEvidenceType: "Project title",
  projectEvidence: "Energy retrofit photovoltaic",
  unresolvedEvidence: [],
  valueEur: 5_000_000,
  geography: "Lombardia · ITC4",
  sourceVersion: "customer-runway-v4:abc",
  cpvCodes: ["09331200"],
};

describe("supplier relevance", () => {
  it("is deterministic and cannot mutate evidence state", () => {
    const relevance = scoreOpportunity(opportunity, {
      domains: ["energy_efficiency"],
      cpvPrefixes: ["093312"],
      nutsPrefixes: ["ITC4"],
      minProjectValueEur: 1_000_000,
    });
    expect(relevance).toBe("HIGH");
    expect(opportunity.state).toBe("UNRESOLVED");
  });
});
