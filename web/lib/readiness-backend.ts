type JsonObject = Record<string, unknown>;

function backendUrl(): string {
  const value = process.env.PROCRUN_READINESS_BACKEND_URL?.trim();
  if (!value) throw new Error("PROCRUN_READINESS_BACKEND_URL is required");
  return value.replace(/\/$/, "");
}

function backendToken(): string {
  const value = process.env.PROCRUN_READINESS_API_TOKEN?.trim();
  if (!value) throw new Error("PROCRUN_READINESS_API_TOKEN is required");
  return value;
}

async function decode(response: Response): Promise<JsonObject> {
  const value: unknown = await response.json();
  if (!value || typeof value !== "object" || Array.isArray(value)) {
    throw new Error("readiness backend returned a non-object response");
  }
  return value as JsonObject;
}

export async function readinessPreview(
  bandoCode: string,
  snapshotId: string,
): Promise<Response> {
  const query = new URLSearchParams({ bando_code: bandoCode, snapshot_id: snapshotId });
  const upstream = await fetch(`${backendUrl()}/v1/readiness/preview?${query}`, {
    headers: { authorization: `Bearer ${backendToken()}` },
    cache: "no-store",
  });
  return Response.json(await decode(upstream), { status: upstream.status });
}

export async function readinessPaidPost(
  path: "unlock" | "dossiers",
  tenantKey: string,
  body: JsonObject,
): Promise<Response> {
  const upstream = await fetch(`${backendUrl()}/v1/readiness/${path}`, {
    method: "POST",
    headers: {
      authorization: `Bearer ${backendToken()}`,
      "content-type": "application/json",
    },
    body: JSON.stringify({ ...body, tenant_key: tenantKey }),
    cache: "no-store",
  });
  return Response.json(await decode(upstream), { status: upstream.status });
}
