import { opportunities, toCsv } from "@/lib/read-model";

export async function GET() {
  const body = toCsv(opportunities);
  return new Response(body, {
    headers: {
      "content-type": "text/csv; charset=utf-8",
      "content-disposition": 'attachment; filename="procrun-fixture-opportunities.csv"',
      "x-procrun-data-surface": "customer-safe-read-model-fixture",
    },
  });
}
