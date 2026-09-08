"use server";

import { revalidatePath } from "next/cache";
import { redirect } from "next/navigation";

import { requireAccount } from "@/lib/auth";
import {
  loadAvailableCategories,
  saveSupplierProfile,
  type SupplierProfileInput,
} from "@/lib/supplier-profile";

function text(value: FormDataEntryValue | null): string {
  return typeof value === "string" ? value.trim() : "";
}

function parseCpv(value: string): string[] {
  if (!value.trim()) return [];
  const values = new Set<string>();
  for (const token of value.split(/[\s,;]+/).filter(Boolean)) {
    if (!/^\d{2,8}(?:-\d)?$/.test(token)) {
      throw new Error(`Invalid CPV code or family: ${token}`);
    }
    values.add(token.split("-", 1)[0]);
  }
  return Array.from(values).sort();
}

function valueRange(value: string): Pick<
  SupplierProfileInput,
  "minProjectValueEur" | "maxProjectValueEur"
> {
  switch (value) {
    case "under-1m":
      return { minProjectValueEur: null, maxProjectValueEur: 999999 };
    case "1m-5m":
      return { minProjectValueEur: 1000000, maxProjectValueEur: 5000000 };
    case "5m-plus":
      return { minProjectValueEur: 5000000, maxProjectValueEur: null };
    default:
      return { minProjectValueEur: null, maxProjectValueEur: null };
  }
}

export async function saveSupplierProfileAction(formData: FormData): Promise<void> {
  const { accountId } = await requireAccount();
  const companyName = text(formData.get("companyName"));
  if (!companyName || companyName.length > 160) {
    throw new Error("Company name is required and must be at most 160 characters.");
  }

  const targetMarket = text(formData.get("targetMarket"));
  if (targetMarket !== "LOMBARDIA") throw new Error("Unsupported target market.");

  const availableCategories = await loadAvailableCategories();
  if (availableCategories === null) throw new Error("Supplier Profile taxonomy is unavailable.");
  const allowedCategories = new Set(availableCategories);
  const categoryPrefixes = Array.from(
    new Set(
      formData
        .getAll("category")
        .map((value) => text(value))
        .filter((value) => value && allowedCategories.has(value)),
    ),
  ).sort();
  if (categoryPrefixes.length === 0) throw new Error("Select at least one product category.");

  const range = valueRange(text(formData.get("projectValue")));
  await saveSupplierProfile(accountId, {
    companyName,
    targetMarket: "LOMBARDIA",
    categoryPrefixes,
    cpvInclude: parseCpv(text(formData.get("cpvInclude"))),
    cpvExclude: parseCpv(text(formData.get("cpvExclude"))),
    ...range,
  });

  revalidatePath("/app");
  revalidatePath("/app/onboarding");
  revalidatePath("/app/profile");

  const returnTo = text(formData.get("returnTo"));
  redirect(returnTo === "/app/profile" ? "/app/profile" : "/app");
}
