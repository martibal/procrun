import "server-only";

import { redirect } from "next/navigation";

export type AuthenticatedAccount = {
  accountId: string;
  source: "development" | "session";
};

async function resolveSessionAccountId(): Promise<string | null> {
  // Production authentication is intentionally not wired yet. The real
  // control-plane provider must replace this adapter without weakening the
  // fail-closed boundary below.
  return null;
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
