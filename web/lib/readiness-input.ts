const OPAQUE_RE = /^[A-Za-z0-9_.:-]{1,128}$/;
const AUTH_RE = /^v1\.\d{1,12}\.[0-9a-f]{64}$/;
const STATES = new Set([
  "CONFIRMED_BY_ADVISOR",
  "NOT_CONFIRMED",
  "PROFESSIONAL_REVIEW_REQUIRED",
]);

export class ReadinessInputError extends Error {}

function object(value: unknown): Record<string, unknown> {
  if (!value || typeof value !== "object" || Array.isArray(value)) {
    throw new ReadinessInputError("request body must be an object");
  }
  return value as Record<string, unknown>;
}

function exactKeys(value: Record<string, unknown>, allowed: Set<string>): void {
  const unknown = Object.keys(value).filter((key) => !allowed.has(key));
  if (unknown.length) throw new ReadinessInputError("unknown readiness input field");
}

function opaque(value: unknown, label: string): string {
  if (typeof value !== "string" || !OPAQUE_RE.test(value)) {
    throw new ReadinessInputError(`${label} must be an opaque identifier`);
  }
  return value;
}

function nonNegativeInt(value: unknown, label: string): number {
  if (!Number.isSafeInteger(value) || (value as number) < 0) {
    throw new ReadinessInputError(`${label} must be a non-negative integer`);
  }
  return value as number;
}

export function parsePreviewQuery(url: URL): { bandoCode: string; snapshotId: string } {
  return {
    bandoCode: opaque(url.searchParams.get("bando_code"), "bando_code"),
    snapshotId: opaque(url.searchParams.get("snapshot_id"), "snapshot_id"),
  };
}

export function parsePaidBody(value: unknown, withConfirmations: boolean): Record<string, unknown> {
  const input = object(value);
  const allowed = new Set([
    "purchase_reference",
    "purchase_authorization",
    "purchase_expires_unix",
    "bando_code",
    "benchmark_snapshot_id",
    "proposed_funding_eur",
    "proposed_duration_months",
  ]);
  if (withConfirmations) allowed.add("confirmations");
  exactKeys(input, allowed);

  const duration = input.proposed_duration_months;
  const result: Record<string, unknown> = {
    purchase_reference: opaque(input.purchase_reference, "purchase_reference"),
    bando_code: opaque(input.bando_code, "bando_code"),
    benchmark_snapshot_id: opaque(input.benchmark_snapshot_id, "benchmark_snapshot_id"),
    proposed_funding_eur: nonNegativeInt(input.proposed_funding_eur, "proposed_funding_eur"),
    proposed_duration_months:
      duration === null || duration === undefined
        ? null
        : nonNegativeInt(duration, "proposed_duration_months"),
    purchase_expires_unix: nonNegativeInt(input.purchase_expires_unix, "purchase_expires_unix"),
  };
  if (typeof input.purchase_authorization !== "string" || !AUTH_RE.test(input.purchase_authorization)) {
    throw new ReadinessInputError("invalid purchase_authorization");
  }
  result.purchase_authorization = input.purchase_authorization;

  if (withConfirmations) {
    if (!Array.isArray(input.confirmations)) {
      throw new ReadinessInputError("confirmations must be a list");
    }
    result.confirmations = input.confirmations.map((raw) => {
      const confirmation = object(raw);
      exactKeys(confirmation, new Set(["requirement_id", "state"]));
      const requirementId = opaque(confirmation.requirement_id, "requirement_id");
      if (typeof confirmation.state !== "string" || !STATES.has(confirmation.state)) {
        throw new ReadinessInputError("invalid confirmation state");
      }
      return { requirement_id: requirementId, state: confirmation.state };
    });
  }
  return result;
}
