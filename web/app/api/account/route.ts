import { withTenant } from "@/lib/api-auth";
import { deleteWorkspace } from "@/lib/workspace-db";

export async function DELETE(request: Request) {
  return withTenant(request, async (tenantKey) => {
    await deleteWorkspace(tenantKey);
    return new Response(null, { status: 204 });
  });
}
