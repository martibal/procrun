import { TED_COVERAGE_NOTE } from "@/lib/public-copy";
import type { OpportunityState } from "@/lib/read-model";
import { getPublicShowcaseOpportunity } from "@/lib/public-showcase";

export type PublicHistoryObservation = {
  observedAt: string;
  state: OpportunityState;
  evidenceReference?: string;
  evidenceUrl?: string;
  evidenceExcerpt?: string;
  coverageNote: string;
  fixture: boolean;
};

// Development-only timeline fixtures exist solely so the append-only history UI
// is testable on localhost before production observations have accumulated.
// They are not historical claims about the showcase project.
const DEVELOPMENT_HISTORY: Record<string, readonly PublicHistoryObservation[]> = {
  "opp-led-playing-fields": [
    {
      observedAt: "2026-01-05",
      state: "OPEN",
      coverageNote: TED_COVERAGE_NOTE,
      fixture: true,
    },
    {
      observedAt: "2026-02-06",
      state: "CLOSED",
      evidenceReference: "85336-2026",
      evidenceUrl: "https://ted.europa.eu/en/notice/85336-2026/pdf",
      evidenceExcerpt: "Notice publication number: 85336-2026",
      coverageNote: TED_COVERAGE_NOTE,
      fixture: true,
    },
  ],
};

export function getPublicOpportunityHistory(
  id: string,
): readonly PublicHistoryObservation[] | undefined {
  if (!getPublicShowcaseOpportunity(id)) return undefined;
  return DEVELOPMENT_HISTORY[id] ?? [];
}
