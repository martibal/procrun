import { withTenant } from "@/lib/api-auth";
import { readinessPaidPost } from "@/lib/readiness-backend";
import { parsePaidBody, ReadinessInputError } from "@/lib/readiness-input";

export async function POST(request: Request): Promise<Response> {
  return withTenant(request, async (tenantKey) => {
    try {
      const body = parsePaidBody(await request.json(), false);
      return readinessPaidPost("unlock", tenantKey, body);
    } catch (error) {
      if (error instanceof ReadinessInputError || error instanceof SyntaxError) {
        return Response.json({ error: "invalid_request" }, { status: 400 });
      }
      throw error;
    }
  });
}
