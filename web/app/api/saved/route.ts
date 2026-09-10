import { withTenant } from "@/lib/api-auth";
import { loadPublishedProjects, toOpportunities } from "@/lib/published-data";
import { listSaved, setSaved } from "@/lib/workspace-db";

export async function GET(request: Request) {
  return withTenant(request, async (tenantKey) => {
    const saved = new Set(await listSaved(tenantKey));
    const items = toOpportunities(await loadPublishedProjects()).filter((item) => saved.has(item.id));
    return Response.json({ items });
  });
}

export async function POST(request: Request) {
  return withTenant(request, async (tenantKey) => {
    const body = await request.json() as { opportunityId?: unknown; saved?: unknown };
    if (typeof body.opportunityId !== "string" || typeof body.saved !== "boolean") {
      return Response.json({ error: "invalid_request" }, { status: 400 });
    }
    await setSaved(tenantKey, body.opportunityId, body.saved);
    return Response.json({ saved: body.saved });
  });
}
