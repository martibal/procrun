import { requireAccount } from "@/lib/auth";
import { loadProductionProjects } from "@/lib/production-projects";
import { rankProjectsForProfile } from "@/lib/relevance";
import { loadSavedOpportunities } from "@/lib/saved-opportunities";
import { loadSupplierProfile } from "@/lib/supplier-profile";

export const dynamic = "force-dynamic";

type ExportRow = {
  operationCode: string;
  projectTitle: string | null;
  programme: string | null;
  region: string | null;
  nutsCode: string | null;
  approvedFundingEur: number | null;
  componentId: string;
  purchasingNeed: string;
  state: string;
  cutoffDate: string;
  relevanceBand: string;
};

function csv(rows: ExportRow[]): string {
  const header = [
    "operation_code",
    "project_title",
    "programme",
    "region",
    "nuts_code",
    "approved_funding_eur",
    "component_id",
    "purchasing_need",
    "state",
    "cutoff_date",
    "relevance_band",
  ];
  const quote = (value: string | number | null) => `"${String(value ?? "").replaceAll('"', '""')}"`;
  return [
    header.join(","),
    ...rows.map((row) => [
      row.operationCode,
      row.projectTitle,
      row.programme,
      row.region,
      row.nutsCode,
      row.approvedFundingEur,
      row.componentId,
      row.purchasingNeed,
      row.state,
      row.cutoffDate,
      row.relevanceBand,
    ].map(quote).join(",")),
  ].join("\n");
}

export async function GET(request: Request): Promise<Response> {
  const { accountId } = await requireAccount();
  const url = new URL(request.url);
  const scope = url.searchParams.get("scope") ?? "filtered";

  let rows: ExportRow[] = [];
  if (scope === "saved") {
    const saved = await loadSavedOpportunities(accountId);
    if (saved === null) return new Response("Saved Opportunities unavailable.", { status: 503 });
    rows = saved.map((item) => ({
      operationCode: item.operationCode,
      projectTitle: item.projectTitle,
      programme: item.programme,
      region: item.region,
      nutsCode: item.nutsCode,
      approvedFundingEur: item.approvedFundingEur,
      componentId: item.componentId,
      purchasingNeed: item.description,
      state: item.state,
      cutoffDate: item.cutoffDate,
      relevanceBand: "SAVED",
    }));
  } else if (scope === "filtered") {
    const [projects, profile] = await Promise.all([
      loadProductionProjects(),
      loadSupplierProfile(accountId),
    ]);
    if (projects === null || !profile) return new Response("Opportunity export unavailable.", { status: 503 });

    const query = (url.searchParams.get("q") ?? "").trim().toLocaleLowerCase();
    const relevance = url.searchParams.get("relevance") ?? "ALL";
    const need = url.searchParams.get("need") ?? "ALL";
    const minimumFunding = Number(url.searchParams.get("minimumFunding") ?? "0") || 0;

    const matched = rankProjectsForProfile(projects.filter((project) => project.openCount > 0), profile)
      .filter((project) => {
        const openNeeds = project.needs.filter((item) => item.state === "OPEN");
        if (relevance !== "ALL" && project.relevanceBand !== relevance) return false;
        if (need !== "ALL" && !openNeeds.some((item) => item.description === need)) return false;
        if ((project.approvedFundingEur ?? 0) < minimumFunding) return false;
        if (!query) return true;
        return [
          project.projectTitle,
          project.operationCode,
          project.programme,
          project.region,
          project.nutsCode,
          ...openNeeds.map((item) => item.description),
        ].filter(Boolean).join(" ").toLocaleLowerCase().includes(query);
      });

    rows = matched.flatMap((project) => project.needs
      .filter((item) => item.state === "OPEN")
      .flatMap((item) => item.componentIds
        .filter((componentId) => project.matchingComponentIds.includes(componentId))
        .map((componentId) => ({
          operationCode: project.operationCode,
          projectTitle: project.projectTitle,
          programme: project.programme,
          region: project.region,
          nutsCode: project.nutsCode,
          approvedFundingEur: project.approvedFundingEur,
          componentId,
          purchasingNeed: item.description,
          state: item.state,
          cutoffDate: item.cutoffDate,
          relevanceBand: project.relevanceBand,
        }))));
  } else {
    return new Response("Unsupported export scope.", { status: 400 });
  }

  return new Response(csv(rows), {
    status: 200,
    headers: {
      "Content-Type": "text/csv; charset=utf-8",
      "Content-Disposition": `attachment; filename="procrun-${scope}.csv"`,
      "Cache-Control": "private, no-store",
    },
  });
}
