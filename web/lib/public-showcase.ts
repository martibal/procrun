import { getOpportunity, type Opportunity } from "@/lib/read-model";

// Public breadth is intentionally explicit and bounded. Adding an ID here is a
// release decision: the record must already be customer-safe and non-fixture.
const PUBLIC_SHOWCASE_IDS = ["opp-led-playing-fields"] as const;

export function getPublicShowcaseOpportunities(): readonly Opportunity[] {
  return PUBLIC_SHOWCASE_IDS.flatMap((id) => {
    const item = getOpportunity(id);
    return item && !item.isFixture ? [item] : [];
  });
}

export function getPublicShowcaseOpportunity(id: string): Opportunity | undefined {
  if (!(PUBLIC_SHOWCASE_IDS as readonly string[]).includes(id)) return undefined;
  const item = getOpportunity(id);
  if (!item || item.isFixture) return undefined;
  return item;
}
