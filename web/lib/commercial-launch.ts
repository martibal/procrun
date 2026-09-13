export type MerchantDisclosure = {
  legalName: string;
  geographicAddress: string;
  contactEmail: string;
  organisationNumber: string;
  registerName: string;
  vatStatus: string;
};

function required(name: string): string {
  return process.env[name]?.trim() ?? "";
}

export function merchantDisclosure(): MerchantDisclosure | null {
  const disclosure: MerchantDisclosure = {
    legalName: required("PROCRUN_MERCHANT_LEGAL_NAME"),
    geographicAddress: required("PROCRUN_MERCHANT_ADDRESS"),
    contactEmail: required("PROCRUN_MERCHANT_EMAIL"),
    organisationNumber: required("PROCRUN_MERCHANT_ORG_NUMBER"),
    registerName: required("PROCRUN_MERCHANT_REGISTER"),
    vatStatus: required("PROCRUN_MERCHANT_VAT_STATUS"),
  };

  if (Object.values(disclosure).some((value) => value.length === 0)) return null;
  return disclosure;
}

export function commercialCheckoutReady(): boolean {
  return merchantDisclosure() !== null;
}

export function requireCommercialCheckoutReady(): MerchantDisclosure {
  const disclosure = merchantDisclosure();
  if (!disclosure) {
    throw new Error(
      "commercial checkout is disabled until all mandatory merchant disclosures are configured",
    );
  }
  return disclosure;
}
