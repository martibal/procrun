import { withTenant } from "@/lib/api-auth";
import { loadPublishedProjects, toCsv, toOpportunities } from "@/lib/published-data";
import { rankOpportunities } from "@/lib/relevance";
import { getProfile, listSaved } from "@/lib/workspace-db";

export async function GET(request: Request) {
  return withTenant(request, async (tenantKey) => {
    const url = new URL(request.url);
    const profile = await getProfile(tenantKey);
    let items = rankOpportunities(toOpportunities(await loadPublishedProjects()), profile);
    if (url.searchParams.get("saved") === "true") {
      const saved = new Set(await listSaved(tenantKey));
      items = items.filter((item) => saved.has(item.id));
    }
    const state = url.searchParams.get("state");
    if (state && ["OPEN", "CLOSED", "UNRESOLVED"].includes(state)) {
      items = items.filter((item) => item.state === state);
    }
    const body = toCsv(items);
    return new Response(body, {
      headers: {
        "content-type": "text/csv; charset=utf-8",
        "content-disposition": 'attachment; filename="procrun-opportunities.csv"',
        "x-procrun-data-surface": "customer-safe-read-model-v4",
      },
    });
  });
}
