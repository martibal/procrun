import { describe, expect, it } from "vitest";

import type {
  ReadinessAdvisorState,
  ReadinessHistoricalReference,
  ReadinessSourceState,
} from "./readiness-contract";

describe("readiness frontend contract", () => {
  it("keeps backend enum values explicit for GUI design", () => {
    const sourceStates: ReadinessSourceState[] = [
      "FRESH",
      "SOURCE_REFRESH_REQUIRED",
      "INVALIDATED",
      "INCOMPLETE",
    ];
    const historicalStates: ReadinessHistoricalReference[] = [
      "UNAVAILABLE",
      "LIMITED_REFERENCE",
      "ANALYSIS_AVAILABLE",
    ];
    const advisorStates: ReadinessAdvisorState[] = [
      "CONFIRMED_BY_ADVISOR",
      "NOT_CONFIRMED",
      "PROFESSIONAL_REVIEW_REQUIRED",
    ];

    expect(sourceStates).toHaveLength(4);
    expect(historicalStates).toHaveLength(3);
    expect(advisorStates).toHaveLength(3);
  });
});
