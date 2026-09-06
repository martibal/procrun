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
  coverageNote?: string;
  projectEvidence: string;
  procurementEvidence?: string;
  valueEur?: number;
  geography: string;
  locationBasis?: string;
  locationSourceUrl?: string;
  programme?: string;
  projectStart?: string;
  sourceUrl?: string;
  sourceVersion: string;
  isFixture: boolean;
};

export const opportunities: readonly Opportunity[] = [
  {
    id: "opp-led-playing-fields",
    projectId: "F28C25000130007",
    projectTitle: "SOSTITUZIONE LED PER ILLUMINAZIONE CAMPI DA GIOCO E VIALETTI",
    component: "Lighting",
    state: "OPEN",
    cutoffDate: "2026-09-06",
    coverage: "TED",
    openWording: "No relevant procurement found in TED as of 2026-09-06.",
    coverageNote: "Coverage: TED. No relevant procurement means no matching procurement was found in the complete TED query universe through the stated cutoff. This does not establish absence outside TED, including national or below-threshold procedures.",
    projectEvidence: "SOSTITUZIONE LED PER ILLUMINAZIONE CAMPI DA GIOCO E VIALETTI",
    valueEur: 35845,
    geography: "Milano province, Lombardia, Italy",
    locationBasis: "Province of the operational site reported in the official Lombardia funding decision for this project.",
    locationSourceUrl: "https://www.unioncamerelombardia.it/fileadmin/bandi/2024/Bando_Investimenti_Linea_Microimprese/All._1_Determinazione_n._9-2025_Investimenti_Linea_Microimprese_imprese_ammesse.pdf",
    programme: "PR FESR Lombardia 2021-2027",
    projectStart: "2025-01-11",
    sourceUrl: "https://opencoesione.gov.it/media/open_data/beneficiari/2021-2027/beneficiari_PR_FESR_LOMBARDIA.zip",
    sourceVersion: "customer-runway-v1",
    isFixture: false,
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
    geography: "Lombardia, Italy",
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
    geography: "Lombardia, Italy",
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
