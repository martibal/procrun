import { withTenant } from "@/lib/api-auth";
import { loadPublishedProjects, toOpportunities } from "@/lib/published-data";
import { rankOpportunities } from "@/lib/relevance";
import { getProfile, listSaved } from "@/lib/workspace-db";

const relevanceRank = { NOT_RELEVANT: 0, LOW: 1, MEDIUM: 2, HIGH: 3 } as const;

export async function GET(request: Request) {
  return withTenant(request, async (tenantKey) => {
    const url = new URL(request.url);
    const projects = await loadPublishedProjects();
    const profile = await getProfile(tenantKey);
    let items = rankOpportunities(toOpportunities(projects), profile);

    const state = url.searchParams.get("state");
    if (state && ["OPEN", "CLOSED", "UNRESOLVED"].includes(state)) {
      items = items.filter((item) => item.state === state);
    }
    const minRelevance = url.searchParams.get("minRelevance") as keyof typeof relevanceRank | null;
    if (minRelevance && minRelevance in relevanceRank) {
      items = items.filter((item) => relevanceRank[item.relevance] >= relevanceRank[minRelevance]);
    }
    if (url.searchParams.get("saved") === "true") {
      const saved = new Set(await listSaved(tenantKey));
      items = items.filter((item) => saved.has(item.id));
    }

    return Response.json({
      dataSurface: "customer-safe-read-model-v4",
      coverageBoundary: "TED rule-bounded matching",
      openDefinition: "No procurement match satisfying ProcRun's frozen exact-evidence rules was found in TED as of DATE.",
      outsideTedDisclaimer: "This does not establish absence of procurement outside TED or under different wording/classification.",
      items,
    });
  });
}
