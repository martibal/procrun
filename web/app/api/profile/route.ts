import { withTenant } from "@/lib/api-auth";
import { getProfile, putProfile } from "@/lib/workspace-db";

export async function GET(request: Request) {
  return withTenant(request, async (tenantKey) => Response.json({ profile: await getProfile(tenantKey) }));
}

export async function PUT(request: Request) {
  return withTenant(request, async (tenantKey) => {
    const body = await request.json();
    return Response.json({ profile: await putProfile(tenantKey, body) });
  });
}
