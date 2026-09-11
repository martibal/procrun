export type OpportunityState = "OPEN" | "CLOSED" | "UNRESOLVED";
export type ProjectEvidenceType = "Project title" | "Project description";

export type Opportunity = {
  id: string;
  projectId: string;
  projectTitle: string;
  component: string;
  state: OpportunityState;
  cutoffDate: string;
  coverage: "TED";
  openWording?: string;
  interpretation: string;
  projectEvidenceType: ProjectEvidenceType;
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
    cutoffDate: "2026-09-10",
    coverage: "TED",
    openWording: "No procurement match satisfying ProcRun's frozen exact-evidence rules was found in TED as of 2026-09-10.",
    interpretation: "The admitted project wording supports this component, and the complete accepted TED search produced no qualifying procurement match at the cutoff.",
    projectEvidenceType: "Project description",
    projectEvidence: "Upgrade pumping stations, electrical controls and remote monitoring across the network.",
    valueEur: 8200000,
    geography: "Fixture region · Italy",
    sourceVersion: "fixture:read-model:v2",
    isFixture: true,
  },
  {
    id: "opp-rail-signalling",
    projectId: "fixture-it-rail-002",
    projectTitle: "Rail corridor modernisation",
    component: "Signalling equipment",
    state: "CLOSED",
    cutoffDate: "2026-09-10",
    coverage: "TED",
    interpretation: "Accepted exact TED procurement evidence closes this component under the frozen production rules.",
    projectEvidenceType: "Project description",
    projectEvidence: "Modernisation includes signalling, communications and station systems.",
    procurementEvidence: "TED notice matched signalling-system procurement under the frozen exact-evidence rules.",
    valueEur: 14500000,
    geography: "Fixture corridor · Italy",
    sourceVersion: "fixture:read-model:v2",
    isFixture: true,
  },
  {
    id: "opp-port-power",
    projectId: "fixture-it-port-003",
    projectTitle: "Port electrification programme",
    component: "Shore power distribution",
    state: "UNRESOLVED",
    cutoffDate: "2026-09-10",
    coverage: "TED",
    interpretation: "The available admitted wording does not support a safe OPEN or CLOSED conclusion for this component. The exact source wording remains visible rather than being rewritten into a stronger claim.",
    projectEvidenceType: "Project title",
    projectEvidence: "Port electrification programme",
    geography: "Fixture port · Italy",
    sourceVersion: "fixture:read-model:v2",
    isFixture: true,
  },
];

export function getOpportunity(id: string): Opportunity | undefined {
  return opportunities.find((item) => item.id === id);
}

export function toCsv(items: readonly Opportunity[]): string {
  const header = ["id","project_title","component","state","cutoff_date","coverage","coverage_wording","project_evidence_type","project_evidence","procrun_interpretation","procurement_evidence","geography","source_version"];
  const quote = (value: string | number | undefined) => `"${String(value ?? "").replaceAll('"', '""')}"`;
  return [header.join(","), ...items.map((item) => [
    item.id,
    item.projectTitle,
    item.component,
    item.state,
    item.cutoffDate,
    item.coverage,
    item.openWording ?? "",
    item.projectEvidenceType,
    item.projectEvidence,
    item.interpretation,
    item.procurementEvidence ?? "",
    item.geography,
    item.sourceVersion,
  ].map(quote).join(","))].join("\n");
}
