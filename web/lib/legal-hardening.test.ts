import { describe, expect, it } from "vitest";
import { OPENCOESIONE_ATTRIBUTION, TED_ATTRIBUTION } from "./source-attribution";

describe("legal hardening contract", () => {
  it("keeps explicit public-source attribution metadata", () => {
    expect(OPENCOESIONE_ATTRIBUTION.licence).toBe("CC BY 4.0");
    expect(OPENCOESIONE_ATTRIBUTION.licenceUrl).toContain("opencoesione.gov.it");
    expect(TED_ATTRIBUTION.licenceUrl).toContain("ted.europa.eu");
    expect(TED_ATTRIBUTION.note).toContain("not an official EU publication");
  });
});
