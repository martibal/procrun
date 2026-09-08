import "server-only";

import { createHmac, timingSafeEqual } from "node:crypto";

import { controlDb, ensureControlSchema } from "@/lib/control-db";

const STRIPE_API = "https://api.stripe.com/v1";
const ACTIVE_STATUSES = new Set(["active", "trialing", "past_due"]);

export type BillingAccount = {
  accountId: string;
  stripeCustomerId: string | null;
  stripeSubscriptionId: string | null;
  subscriptionStatus: string | null;
  currentPeriodEnd: string | null;
};

export function merchantGateOpen(): boolean {
  return process.env.PROCRUN_MERCHANT_GATE === "ENABLED";
}

export function billingConfigured(): boolean {
  return Boolean(
    merchantGateOpen()
      && process.env.STRIPE_SECRET_KEY?.trim()
      && process.env.STRIPE_PRICE_LOMBARDIA_MONTHLY?.trim()
      && process.env.STRIPE_WEBHOOK_SECRET?.trim()
      && process.env.NEXT_PUBLIC_APP_URL?.trim()
      && process.env.PROCRUN_CONTROL_DATABASE_URL?.trim(),
  );
}

function requireBillingConfiguration(): void {
  if (!billingConfigured()) {
    throw new Error("ProcRun billing is not enabled by the merchant launch gate.");
  }
}

async function stripeRequest(path: string, body: URLSearchParams): Promise<Record<string, unknown>> {
  const secret = process.env.STRIPE_SECRET_KEY?.trim();
  if (!secret) throw new Error("Stripe secret is unavailable.");

  const response = await fetch(`${STRIPE_API}${path}`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${secret}`,
      "Content-Type": "application/x-www-form-urlencoded",
    },
    body,
    cache: "no-store",
  });
  const payload = await response.json() as Record<string, unknown>;
  if (!response.ok) throw new Error("Stripe request failed.");
  return payload;
}

function appUrl(): string {
  const value = process.env.NEXT_PUBLIC_APP_URL?.trim();
  if (!value) throw new Error("Application URL is unavailable.");
  return value.replace(/\/$/, "");
}

export async function loadBillingAccount(accountId: string): Promise<BillingAccount | null> {
  if (!(await ensureControlSchema())) return null;
  const activePool = controlDb();
  if (!activePool) return null;

  const result = await activePool.query<{
    account_id: string;
    stripe_customer_id: string | null;
    stripe_subscription_id: string | null;
    subscription_status: string | null;
    current_period_end: string | null;
  }>(`
    SELECT
      account_id,
      stripe_customer_id,
      stripe_subscription_id,
      subscription_status,
      current_period_end::text
    FROM procrun_control.billing_accounts
    WHERE account_id = $1
    LIMIT 1
  `, [accountId]);

  const row = result.rows[0];
  if (!row) return null;
  return {
    accountId: row.account_id,
    stripeCustomerId: row.stripe_customer_id,
    stripeSubscriptionId: row.stripe_subscription_id,
    subscriptionStatus: row.subscription_status,
    currentPeriodEnd: row.current_period_end,
  };
}

export function hasPaidAccess(account: BillingAccount | null): boolean {
  return Boolean(account?.subscriptionStatus && ACTIVE_STATUSES.has(account.subscriptionStatus));
}

export async function createCheckoutSession(accountId: string): Promise<string> {
  requireBillingConfiguration();
  const price = process.env.STRIPE_PRICE_LOMBARDIA_MONTHLY!.trim();
  const base = appUrl();

  const body = new URLSearchParams();
  body.set("mode", "subscription");
  body.set("line_items[0][price]", price);
  body.set("line_items[0][quantity]", "1");
  body.set("success_url", `${base}/app/account?checkout=success`);
  body.set("cancel_url", `${base}/app/account?checkout=cancelled`);
  body.set("client_reference_id", accountId);
  body.set("metadata[procrun_account_id]", accountId);
  body.set("subscription_data[metadata][procrun_account_id]", accountId);
  body.set("billing_address_collection", "required");
  body.set("tax_id_collection[enabled]", "true");

  const existing = await loadBillingAccount(accountId);
  if (existing?.stripeCustomerId) body.set("customer", existing.stripeCustomerId);

  const payload = await stripeRequest("/checkout/sessions", body);
  const url = typeof payload.url === "string" ? payload.url : null;
  if (!url) throw new Error("Stripe checkout URL was not returned.");
  return url;
}

export async function createBillingPortalSession(accountId: string): Promise<string> {
  requireBillingConfiguration();
  const account = await loadBillingAccount(accountId);
  if (!account?.stripeCustomerId) throw new Error("No Stripe customer is linked to this account.");

  const body = new URLSearchParams();
  body.set("customer", account.stripeCustomerId);
  body.set("return_url", `${appUrl()}/app/account`);
  const payload = await stripeRequest("/billing_portal/sessions", body);
  const url = typeof payload.url === "string" ? payload.url : null;
  if (!url) throw new Error("Stripe billing portal URL was not returned.");
  return url;
}

function secureEqual(a: string, b: string): boolean {
  const left = Buffer.from(a);
  const right = Buffer.from(b);
  return left.length === right.length && timingSafeEqual(left, right);
}

export function verifyStripeSignature(payload: string, signatureHeader: string): boolean {
  const secret = process.env.STRIPE_WEBHOOK_SECRET?.trim();
  if (!secret) return false;

  const fields = new Map<string, string[]>();
  for (const part of signatureHeader.split(",")) {
    const [key, value] = part.split("=", 2);
    if (!key || !value) continue;
    fields.set(key, [...(fields.get(key) ?? []), value]);
  }
  const timestamp = Number(fields.get("t")?.[0]);
  if (!Number.isFinite(timestamp)) return false;
  if (Math.abs(Date.now() / 1000 - timestamp) > 300) return false;

  const expected = createHmac("sha256", secret)
    .update(`${timestamp}.${payload}`, "utf8")
    .digest("hex");
  return (fields.get("v1") ?? []).some((candidate) => secureEqual(candidate, expected));
}

function stringValue(value: unknown): string | null {
  return typeof value === "string" && value.trim() ? value : null;
}

function unixDate(value: unknown): Date | null {
  return typeof value === "number" && Number.isFinite(value) ? new Date(value * 1000) : null;
}

export async function applyStripeEvent(event: Record<string, unknown>): Promise<void> {
  if (!(await ensureControlSchema())) throw new Error("Billing control database is unavailable.");
  const activePool = controlDb();
  if (!activePool) throw new Error("Billing control database is unavailable.");

  const type = stringValue(event.type);
  const data = event.data as { object?: Record<string, unknown> } | undefined;
  const object = data?.object;
  if (!type || !object) return;

  if (type === "checkout.session.completed") {
    const metadata = object.metadata as Record<string, unknown> | undefined;
    const accountId = stringValue(metadata?.procrun_account_id) ?? stringValue(object.client_reference_id);
    const customerId = stringValue(object.customer);
    const subscriptionId = stringValue(object.subscription);
    if (!accountId || !customerId) return;

    await activePool.query(`
      INSERT INTO procrun_control.billing_accounts (
        account_id, stripe_customer_id, stripe_subscription_id, subscription_status, updated_at
      ) VALUES ($1, $2, $3, 'checkout_complete', now())
      ON CONFLICT (account_id) DO UPDATE SET
        stripe_customer_id = EXCLUDED.stripe_customer_id,
        stripe_subscription_id = COALESCE(EXCLUDED.stripe_subscription_id, procrun_control.billing_accounts.stripe_subscription_id),
        updated_at = now()
    `, [accountId, customerId, subscriptionId]);
    return;
  }

  if (type.startsWith("customer.subscription.")) {
    const metadata = object.metadata as Record<string, unknown> | undefined;
    const accountId = stringValue(metadata?.procrun_account_id);
    const customerId = stringValue(object.customer);
    const subscriptionId = stringValue(object.id);
    const status = stringValue(object.status);
    if (!accountId || !customerId || !subscriptionId || !status) return;

    await activePool.query(`
      INSERT INTO procrun_control.billing_accounts (
        account_id,
        stripe_customer_id,
        stripe_subscription_id,
        subscription_status,
        current_period_end,
        updated_at
      ) VALUES ($1, $2, $3, $4, $5, now())
      ON CONFLICT (account_id) DO UPDATE SET
        stripe_customer_id = EXCLUDED.stripe_customer_id,
        stripe_subscription_id = EXCLUDED.stripe_subscription_id,
        subscription_status = EXCLUDED.subscription_status,
        current_period_end = EXCLUDED.current_period_end,
        updated_at = now()
    `, [accountId, customerId, subscriptionId, status, unixDate(object.current_period_end)]);
  }
}
