import { createHmac, timingSafeEqual } from "node:crypto";

const TENANT_RE = /^org_[0-9a-f]{32}$/;

export class TenantCapabilityError extends Error {}

export function requireTenantKey(value: string): string {
  if (!TENANT_RE.test(value)) {
    throw new TenantCapabilityError("tenant key must be an opaque organisation identifier");
  }
  return value;
}

function signature(secret: string, tenant: string, expires: string): string {
  return createHmac("sha256", secret).update(`${tenant}.${expires}`).digest("hex");
}

export function signTenantCapability(
  tenantKey: string,
  expiresUnix: number,
  secret: string,
): string {
  const tenant = requireTenantKey(tenantKey);
  if (!secret || secret.length < 32) {
    throw new TenantCapabilityError("tenant capability secret must be at least 32 characters");
  }
  if (!Number.isSafeInteger(expiresUnix) || expiresUnix <= 0) {
    throw new TenantCapabilityError("invalid capability expiry");
  }
  const expires = String(expiresUnix);
  return `${tenant}.${expires}.${signature(secret, tenant, expires)}`;
}

export function verifyTenantCapability(
  token: string,
  secret: string,
  nowUnix = Math.floor(Date.now() / 1000),
): string {
  if (!secret || secret.length < 32) {
    throw new TenantCapabilityError("tenant capability secret is not configured safely");
  }
  const parts = token.split(".");
  if (parts.length !== 3) throw new TenantCapabilityError("invalid tenant capability");
  const [tenantRaw, expires, supplied] = parts;
  const tenant = requireTenantKey(tenantRaw);
  if (!/^\d{1,12}$/.test(expires)) throw new TenantCapabilityError("invalid capability expiry");
  const expiry = Number(expires);
  if (!Number.isSafeInteger(expiry) || expiry < nowUnix) {
    throw new TenantCapabilityError("tenant capability expired");
  }
  if (!/^[0-9a-f]{64}$/.test(supplied)) {
    throw new TenantCapabilityError("invalid capability signature");
  }
  const expected = signature(secret, tenant, expires);
  const left = Buffer.from(expected, "hex");
  const right = Buffer.from(supplied, "hex");
  if (left.length !== right.length || !timingSafeEqual(left, right)) {
    throw new TenantCapabilityError("invalid capability signature");
  }
  return tenant;
}

export function tenantFromRequest(request: Request): string {
  const authorization = request.headers.get("authorization") ?? "";
  const match = /^Bearer\s+(.+)$/i.exec(authorization);
  if (!match) throw new TenantCapabilityError("missing tenant capability");
  const secret = process.env.PROCRUN_TENANT_CAPABILITY_SECRET ?? "";
  return verifyTenantCapability(match[1], secret);
}
