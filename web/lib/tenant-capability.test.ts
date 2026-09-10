import { describe, expect, it } from "vitest";
import { signTenantCapability, verifyTenantCapability } from "./tenant-capability";

const secret = "0123456789abcdef0123456789abcdef";
const tenant = "org_aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa";

describe("tenant capability", () => {
  it("round-trips an opaque organisation tenant without identity data", () => {
    const token = signTenantCapability(tenant, 2_000_000_000, secret);
    expect(verifyTenantCapability(token, secret, 1_900_000_000)).toBe(tenant);
    expect(token).not.toContain("@");
  });

  it("rejects tampering, expiry and identity-shaped tenant values", () => {
    const token = signTenantCapability(tenant, 2_000_000_000, secret);
    const tampered = `${token.slice(0, -1)}${token.endsWith("0") ? "1" : "0"}`;
    expect(() => verifyTenantCapability(tampered, secret, 1_900_000_000)).toThrow();
    expect(() => verifyTenantCapability(token, secret, 2_100_000_000)).toThrow();
    expect(() => signTenantCapability("martin@example.com", 2_000_000_000, secret)).toThrow();
  });
});
