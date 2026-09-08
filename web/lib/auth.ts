import "server-only";

import { auth } from "@clerk/nextjs/server";
import { redirect } from "next/navigation";

export type AuthenticatedAccount = {
  accountId: string;
  source: "development" | "session";
};

function clerkConfigured(): boolean {
  return Boolean(
    process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY?.trim() &&
      process.env.CLERK_SECRET_KEY?.trim(),
  );
}

async function resolveSessionAccountId(): Promise<string | null> {
  if (!clerkConfigured()) return null;

  try {
    const { userId, orgId } = await auth();
    if (!userId) return null;

    return orgId ? `org:${orgId}` : `user:${userId}`;
  } catch {
    console.error("ProcRun authentication control plane is unavailable");
    return null;
  }
}

export async function requireAccount(): Promise<AuthenticatedAccount> {
  const isProduction = process.env.NODE_ENV === "production";

  if (!isProduction) {
    const devAccountId = process.env.PROCRUN_DEV_ACCOUNT_ID?.trim();
    if (devAccountId) {
      return { accountId: devAccountId, source: "development" };
    }
  }

  const accountId = (await resolveSessionAccountId())?.trim();
  if (!accountId) {
    redirect("/login");
  }

  return { accountId, source: "session" };
}
