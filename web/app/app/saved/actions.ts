"use server";

import { revalidatePath } from "next/cache";

import { requireAccount } from "@/lib/auth";
import { removeSavedOpportunity, saveOpportunity } from "@/lib/saved-opportunities";

export async function saveOpportunityAction(formData: FormData): Promise<void> {
  const { accountId } = await requireAccount();
  const componentId = String(formData.get("componentId") ?? "").trim();
  if (!componentId) throw new Error("Missing component ID.");

  await saveOpportunity(accountId, componentId);
  revalidatePath("/app/saved");
}

export async function removeSavedOpportunityAction(formData: FormData): Promise<void> {
  const { accountId } = await requireAccount();
  const componentId = String(formData.get("componentId") ?? "").trim();
  if (!componentId) throw new Error("Missing component ID.");

  await removeSavedOpportunity(accountId, componentId);
  revalidatePath("/app/saved");
}
