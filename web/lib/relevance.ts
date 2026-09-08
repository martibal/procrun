import type { ProductionProjectNeed, ProductionProjectSummary } from "@/lib/production-projects";
import type { SupplierProfile } from "@/lib/supplier-profile";

export type RelevanceBand = "HIGH" | "MEDIUM" | "LOW" | "NOT_RELEVANT";

export type PersonalizedProject = ProductionProjectSummary & {
  relevanceBand: "HIGH" | "MEDIUM";
  matchingComponentIds: string[];
};

type ProjectRelevance = {
  relevanceBand: RelevanceBand;
  matchingComponentIds: string[];
};

function categoryMatch(
  need: ProductionProjectNeed,
  selected: string[],
): "EXACT" | "FAMILY" | null {
  for (const category of selected) {
    if (need.category === category) return "EXACT";
  }
  for (const category of selected) {
    if (need.category.startsWith(`${category}:`)) return "FAMILY";
  }
  return null;
}

export function relevanceForProject(
  project: ProductionProjectSummary,
  profile: SupplierProfile,
): ProjectRelevance {
  if (profile.targetMarket !== "LOMBARDIA") {
    return { relevanceBand: "NOT_RELEVANT", matchingComponentIds: [] };
  }

  if (project.region?.trim().toLocaleLowerCase() !== "lombardia") {
    return { relevanceBand: "NOT_RELEVANT", matchingComponentIds: [] };
  }

  if (profile.minProjectValueEur !== null || profile.maxProjectValueEur !== null) {
    if (project.approvedFundingEur === null) {
      return { relevanceBand: "LOW", matchingComponentIds: [] };
    }
    if (
      profile.minProjectValueEur !== null
      && project.approvedFundingEur < profile.minProjectValueEur
    ) {
      return { relevanceBand: "NOT_RELEVANT", matchingComponentIds: [] };
    }
    if (
      profile.maxProjectValueEur !== null
      && project.approvedFundingEur > profile.maxProjectValueEur
    ) {
      return { relevanceBand: "NOT_RELEVANT", matchingComponentIds: [] };
    }
  }

  // The current customer-safe OPEN summary does not project CPV. A configured
  // CPV constraint therefore cannot be evaluated safely and must remain LOW
  // rather than being guessed into the standard High/Medium feed.
  if (profile.cpvInclude.length > 0 || profile.cpvExclude.length > 0) {
    return { relevanceBand: "LOW", matchingComponentIds: [] };
  }

  const openNeeds = project.needs.filter((need) => need.state === "OPEN");
  let hasExact = false;
  let hasFamily = false;
  const matchingComponentIds = new Set<string>();

  for (const need of openNeeds) {
    const match = categoryMatch(need, profile.categoryPrefixes);
    if (!match) continue;
    if (!need.scopeEvidence.trim()) continue;
    if (match === "EXACT") hasExact = true;
    if (match === "FAMILY") hasFamily = true;
    for (const componentId of need.componentIds) matchingComponentIds.add(componentId);
  }

  if (hasExact) {
    return {
      relevanceBand: "HIGH",
      matchingComponentIds: Array.from(matchingComponentIds).sort(),
    };
  }
  if (hasFamily) {
    return {
      relevanceBand: "MEDIUM",
      matchingComponentIds: Array.from(matchingComponentIds).sort(),
    };
  }
  return { relevanceBand: "NOT_RELEVANT", matchingComponentIds: [] };
}

export function rankProjectsForProfile(
  projects: ProductionProjectSummary[],
  profile: SupplierProfile,
): PersonalizedProject[] {
  const ranked: PersonalizedProject[] = [];

  for (const project of projects) {
    const relevance = relevanceForProject(project, profile);
    if (relevance.relevanceBand !== "HIGH" && relevance.relevanceBand !== "MEDIUM") continue;
    ranked.push({
      ...project,
      relevanceBand: relevance.relevanceBand,
      matchingComponentIds: relevance.matchingComponentIds,
    });
  }

  return ranked.sort((a, b) => {
    const bandRank = { HIGH: 0, MEDIUM: 1 } as const;
    return bandRank[a.relevanceBand] - bandRank[b.relevanceBand]
      || b.openCount - a.openCount
      || b.componentCount - a.componentCount
      || (a.projectTitle ?? a.operationCode).localeCompare(b.projectTitle ?? b.operationCode);
  });
}
