import { afterEach, describe, expect, it } from "vitest";
import {
  commercialCheckoutReady,
  merchantDisclosure,
  requireCommercialCheckoutReady,
} from "./commercial-launch";

const KEYS = [
  "PROCRUN_MERCHANT_LEGAL_NAME",
  "PROCRUN_MERCHANT_ADDRESS",
  "PROCRUN_MERCHANT_EMAIL",
  "PROCRUN_MERCHANT_ORG_NUMBER",
  "PROCRUN_MERCHANT_REGISTER",
  "PROCRUN_MERCHANT_VAT_STATUS",
] as const;

afterEach(() => {
  for (const key of KEYS) delete process.env[key];
});

describe("commercial launch gate", () => {
  it("fails closed while mandatory merchant disclosures are incomplete", () => {
    process.env.PROCRUN_MERCHANT_LEGAL_NAME = "ProcRun Test AS";
    expect(merchantDisclosure()).toBeNull();
    expect(commercialCheckoutReady()).toBe(false);
    expect(() => requireCommercialCheckoutReady()).toThrow("checkout is disabled");
  });

  it("opens only when every mandatory merchant disclosure is configured", () => {
    process.env.PROCRUN_MERCHANT_LEGAL_NAME = "ProcRun Test AS";
    process.env.PROCRUN_MERCHANT_ADDRESS = "Testgata 1, 0001 Oslo, Norway";
    process.env.PROCRUN_MERCHANT_EMAIL = "legal@example.invalid";
    process.env.PROCRUN_MERCHANT_ORG_NUMBER = "999999999";
    process.env.PROCRUN_MERCHANT_REGISTER = "Register of Business Enterprises";
    process.env.PROCRUN_MERCHANT_VAT_STATUS = "Not registered for VAT";

    expect(commercialCheckoutReady()).toBe(true);
    expect(requireCommercialCheckoutReady().organisationNumber).toBe("999999999");
  });
});
