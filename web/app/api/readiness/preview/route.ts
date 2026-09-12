import { withTenant } from "@/lib/api-auth";
import { readinessPreview } from "@/lib/readiness-backend";
import { parsePreviewQuery, ReadinessInputError } from "@/lib/readiness-input";

export async function GET(request: Request): Promise<Response> {
  return withTenant(request, async () => {
    try {
      const { bandoCode, snapshotId } = parsePreviewQuery(new URL(request.url));
      return readinessPreview(bandoCode, snapshotId);
    } catch (error) {
      if (error instanceof ReadinessInputError) {
        return Response.json({ error: "invalid_request" }, { status: 400 });
      }
      throw error;
    }
  });
}
