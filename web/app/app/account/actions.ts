"use server";

import { auth } from "@clerk/nextjs/server";
import { redirect } from "next/navigation";

import { deleteProcRunAccount } from "@/lib/account-deletion";
import { requireAccount } from "@/lib/auth";
import { createBillingPortalSession, createCheckoutSession } from "@/lib/billing";

export async function startCheckoutAction(): Promise<void> {
  const { accountId } = await requireAccount();
  const url = await createCheckoutSession(accountId);
  redirect(url);
}

export async function openBillingPortalAction(): Promise<void> {
  const { accountId } = await requireAccount();
  const url = await createBillingPortalSession(accountId);
  redirect(url);
}

export async function deleteAccountAction(formData: FormData): Promise<void> {
  const confirmation = String(formData.get("confirmation") ?? "").trim();
  if (confirmation !== "DELETE") {
    throw new Error("Type DELETE exactly to confirm account deletion.");
  }

  const account = await requireAccount();
  const session = account.source === "session" ? await auth() : null;
  const principal = {
    accountId: account.accountId,
    source: account.source,
    userId: session?.userId ?? null,
    orgId: session?.orgId ?? null,
    orgRole: session?.orgRole ?? null,
  };

  await deleteProcRunAccount(principal);
  redirect("/?account=deleted");
}
