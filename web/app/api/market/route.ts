import { withTenant } from "@/lib/api-auth";
import { loadPublishedProjects } from "@/lib/published-data";

export async function GET(request: Request) {
  return withTenant(request, async () => {
    const projects = await loadPublishedProjects();
    const stateCounts = { OPEN: 0, CLOSED: 0, PARTIAL: 0, UNRESOLVED: 0 };
    let knownApprovedFundingEur = 0;
    let missingValueCount = 0;
    for (const project of projects) {
      stateCounts[project.state] += 1;
      if (project.approved_funding_eur == null) missingValueCount += 1;
      else knownApprovedFundingEur += project.approved_funding_eur;
    }
    return Response.json({
      projectCount: projects.length,
      stateCounts,
      knownApprovedFundingEur,
      missingValueCount,
      valueCoverageRatio: projects.length ? (projects.length - missingValueCount) / projects.length : 0,
      coverageBoundary: "TED rule-bounded matching",
      marketSizeClaim: false,
    });
  });
}
