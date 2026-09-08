"use server";

import { revalidatePath } from "next/cache";

import { requireAccount } from "@/lib/auth";
import { removeSavedOpportunity, saveOpportunity } from "@/lib/saved-opportunities";

export async function saveNeedAction(formData: FormData): Promise<void> {
  const { accountId } = await requireAccount();
  const componentIds = Array.from(new Set(
    formData.getAll("componentId").map((value) => String(value).trim()).filter(Boolean),
  ));
  if (componentIds.length === 0) throw new Error("Missing component ID.");

  for (const componentId of componentIds) await saveOpportunity(accountId, componentId);
  revalidatePath("/app/saved");
}

export async function removeSavedOpportunityAction(formData: FormData): Promise<void> {
  const { accountId } = await requireAccount();
  const componentId = String(formData.get("componentId") ?? "").trim();
  if (!componentId) throw new Error("Missing component ID.");

  await removeSavedOpportunity(accountId, componentId);
  revalidatePath("/app/saved");
}
