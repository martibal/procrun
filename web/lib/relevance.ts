import type { Opportunity } from "./published-data";
import type { SupplierProfile } from "./workspace-db";

export type Relevance = "HIGH" | "MEDIUM" | "LOW" | "NOT_RELEVANT";

const rank: Record<Relevance, number> = { NOT_RELEVANT: 0, LOW: 1, MEDIUM: 2, HIGH: 3 };

export function scoreOpportunity(item: Opportunity, profile: SupplierProfile | null): Relevance {
  if (!profile) return "LOW";
  const domain = item.componentCategory?.split(":", 1)[0] ?? "";
  const domainMatch = profile.domains.length === 0 || profile.domains.includes(domain);
  const geoMatch = profile.nutsPrefixes.length === 0 || profile.nutsPrefixes.some((value) => item.geography.toUpperCase().includes(value));
  const valueMatch = profile.minProjectValueEur === 0 || (item.valueEur != null && item.valueEur >= profile.minProjectValueEur);
  const cpvMatch = profile.cpvPrefixes.length === 0 || profile.cpvPrefixes.some((prefix) => item.cpvCodes.some((code) => code.replaceAll("-", "").startsWith(prefix)));
  const score = [domainMatch, geoMatch, valueMatch, cpvMatch].filter(Boolean).length;
  return score === 4 ? "HIGH" : score === 3 ? "MEDIUM" : score === 2 ? "LOW" : "NOT_RELEVANT";
}

export function rankOpportunities(items: Opportunity[], profile: SupplierProfile | null): Array<Opportunity & { relevance: Relevance }> {
  return items
    .map((item) => ({ ...item, relevance: scoreOpportunity(item, profile) }))
    .sort((a, b) => rank[b.relevance] - rank[a.relevance] || a.id.localeCompare(b.id));
}
