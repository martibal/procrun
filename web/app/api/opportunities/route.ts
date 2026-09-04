import { opportunities } from "@/lib/read-model";

export async function GET() {
  return Response.json({
    dataSurface: "customer-safe-read-model-fixture",
    coverageBoundary: "TED",
    openDefinition: "No relevant procurement found in TED as of DATE.",
    outsideTedDisclaimer:
      "This does not establish absence outside TED, including purely national or below-threshold procedures.",
    items: opportunities,
  });
}
