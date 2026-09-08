import "server-only";

import { clerkClient } from "@clerk/nextjs/server";

import { purgeBillingIdentity } from "@/lib/billing";
import { procrunDb } from "@/lib/procrun-db";

export type DeletionPrincipal = {
  accountId: string;
  source: "development" | "session";
  userId: string | null;
  orgId: string | null;
  orgRole: string | null;
};

export function validateDeletionPrincipal(principal: DeletionPrincipal): void {
  if (principal.source === "development") return;

  if (!principal.userId) {
    throw new Error("Authenticated user identity is unavailable.");
  }

  const expectedAccountId = principal.orgId
    ? `org:${principal.orgId}`
    : `user:${principal.userId}`;
  if (expectedAccountId !== principal.accountId) {
    throw new Error("Authenticated account does not match the deletion target.");
  }

  if (principal.orgId && principal.orgRole !== "org:admin") {
    throw new Error("Only an organization administrator can delete this ProcRun workspace.");
  }
}

async function purgeIntelligenceAccount(accountId: string): Promise<void> {
  const activePool = procrunDb();
  if (!activePool) throw new Error("ProcRun database is unavailable.");

  const client = await activePool.connect();
  try {
    await client.query("BEGIN");
    await client.query("DELETE FROM procrun.accounts WHERE account_id = $1", [accountId]);

    const verification = await client.query<{
      accounts: boolean;
      matches: boolean;
      saved: boolean;
      profiles: boolean;
    }>(`
      SELECT
        EXISTS(SELECT 1 FROM procrun.accounts WHERE account_id = $1) AS accounts,
        EXISTS(SELECT 1 FROM procrun.component_matches WHERE account_id = $1) AS matches,
        EXISTS(SELECT 1 FROM procrun.saved_opportunities WHERE account_id = $1) AS saved,
        EXISTS(SELECT 1 FROM procrun.supplier_profiles WHERE account_id = $1) AS profiles
    `, [accountId]);

    const row = verification.rows[0];
    if (!row || row.accounts || row.matches || row.saved || row.profiles) {
      throw new Error("ProcRun account-data deletion could not be verified.");
    }

    await client.query("COMMIT");
  } catch (error) {
    await client.query("ROLLBACK");
    throw error;
  } finally {
    client.release();
  }
}

async function purgeClerkPrincipal(principal: DeletionPrincipal): Promise<void> {
  if (principal.source === "development") return;

  const client = await clerkClient();
  if (principal.orgId) {
    await client.organizations.deleteOrganization(principal.orgId);
    return;
  }
  if (!principal.userId) throw new Error("Authenticated user identity is unavailable.");
  await client.users.deleteUser(principal.userId);
}

export async function deleteProcRunAccount(principal: DeletionPrincipal): Promise<void> {
  validateDeletionPrincipal(principal);

  // Billing is removed first so a failed Stripe cancellation can never leave a customer
  // believing the workspace was deleted while recurring billing remains active.
  await purgeBillingIdentity(principal.accountId);
  await purgeIntelligenceAccount(principal.accountId);
  await purgeClerkPrincipal(principal);
}
