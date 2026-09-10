import { TenantCapabilityError, tenantFromRequest } from "./tenant-capability";

export async function withTenant(
  request: Request,
  handler: (tenantKey: string) => Promise<Response>,
): Promise<Response> {
  try {
    return await handler(tenantFromRequest(request));
  } catch (error) {
    if (error instanceof TenantCapabilityError) {
      return Response.json({ error: "unauthorized" }, { status: 401 });
    }
    console.error("ProcRun API failure", error);
    return Response.json({ error: "service_unavailable" }, { status: 503 });
  }
}
