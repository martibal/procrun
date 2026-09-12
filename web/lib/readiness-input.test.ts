import { describe, expect, it } from "vitest";

import { parsePaidBody, parsePreviewQuery, ReadinessInputError } from "./readiness-input";

const authorization = `v1.2000000000.${"a".repeat(64)}`;

function paidBody() {
  return {
    purchase_reference: "pay_opaque_123",
    purchase_authorization: authorization,
    purchase_expires_unix: 2_000_000_000,
    bando_code: "BANDO-X",
    benchmark_snapshot_id: "snapshot-1",
    proposed_funding_eur: 250_000,
    proposed_duration_months: 12,
  };
}

describe("readiness input boundary", () => {
  it("accepts only structured paid fields", () => {
    expect(parsePaidBody(paidBody(), false)).toEqual(paidBody());
  });

  it("rejects arbitrary free text fields", () => {
    expect(() => parsePaidBody({ ...paidBody(), customer_note: "Mario Rossi" }, false)).toThrow(
      ReadinessInputError,
    );
  });

  it("allows only enum-only confirmation objects", () => {
    const result = parsePaidBody(
      {
        ...paidBody(),
        confirmations: [{ requirement_id: "dnsh-1", state: "PROFESSIONAL_REVIEW_REQUIRED" }],
      },
      true,
    );
    expect(result.confirmations).toEqual([
      { requirement_id: "dnsh-1", state: "PROFESSIONAL_REVIEW_REQUIRED" },
    ]);
    expect(() =>
      parsePaidBody(
        {
          ...paidBody(),
          confirmations: [
            { requirement_id: "dnsh-1", state: "CONFIRMED_BY_ADVISOR", note: "person name" },
          ],
        },
        true,
      ),
    ).toThrow(ReadinessInputError);
  });

  it("validates preview identifiers without accepting text payloads", () => {
    const url = new URL("https://example.test/api?bando_code=BANDO-X&snapshot_id=snapshot-1");
    expect(parsePreviewQuery(url)).toEqual({ bandoCode: "BANDO-X", snapshotId: "snapshot-1" });
  });
});
