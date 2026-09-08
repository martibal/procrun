"use server";

import { redirect } from "next/navigation";

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
