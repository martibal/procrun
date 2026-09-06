export type OpportunityState = "OPEN" | "CLOSED" | "UNRESOLVED";

export type Opportunity = {
  id: string;
  projectId: string;
  projectTitle: string;
  component: string;
  state: OpportunityState;
  cutoffDate: string;
  coverage: "TED";
  openWording?: string;
  projectEvidence: string;
  procurementEvidence?: string;
  valueEur?: number;
  geography: string;
  sourceVersion: string;
  isFixture: true;
};

export const opportunities: readonly Opportunity[] = [
  {
    id: "opp-water-pumps",
    projectId: "fixture-it-water-001",
    projectTitle: "Regional water-network resilience programme",
    component: "Pumping systems and controls",
    state: "OPEN",
    cutoffDate: "2026-09-04",
    coverage: "TED",
    openWording: "No relevant procurement found in TED as of 2026-09-04.",
    projectEvidence: "Upgrade pumping stations, electrical controls and remote monitoring across the network.",
    valueEur: 8200000,
    geography: "Lombardia · Italy",
    sourceVersion: "fixture:read-model:v1",
    isFixture: true,
  },
  {
    id: "opp-rail-signalling",
    projectId: "fixture-it-rail-002",
    projectTitle: "Regional rail corridor modernisation",
    component: "Signalling equipment",
    state: "CLOSED",
    cutoffDate: "2026-09-04",
    coverage: "TED",
    projectEvidence: "Modernisation includes signalling, communications and station systems.",
    procurementEvidence: "TED notice matched signalling-system procurement under the frozen matching rules.",
    valueEur: 14500000,
    geography: "Lombardia · Italy",
    sourceVersion: "fixture:read-model:v1",
    isFixture: true,
  },
  {
    id: "opp-grid-controls",
    projectId: "fixture-it-grid-003",
    projectTitle: "Local energy-network upgrade",
    component: "Grid monitoring and control systems",
    state: "UNRESOLVED",
    cutoffDate: "2026-09-04",
    coverage: "TED",
    projectEvidence: "Digital monitoring and control infrastructure for local distribution assets.",
    geography: "Lombardia · Italy",
    sourceVersion: "fixture:read-model:v1",
    isFixture: true,
  },
];

export function getOpportunity(id: string): Opportunity | undefined {
  return opportunities.find((item) => item.id === id);
}

export function toCsv(items: readonly Opportunity[]): string {
  const header = ["id","project_title","component","state","cutoff_date","coverage","coverage_wording","geography","source_version"];
  const quote = (value: string | number | undefined) => `"${String(value ?? "").replaceAll('"', '""')}"`;
  return [header.join(","), ...items.map((item) => [
    item.id,
    item.projectTitle,
    item.component,
    item.state,
    item.cutoffDate,
    item.coverage,
    item.openWording ?? "",
    item.geography,
    item.sourceVersion,
  ].map(quote).join(","))].join("\n");
}
