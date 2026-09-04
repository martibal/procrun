const SOURCE_URL =
  "https://opencoesione.gov.it/it/opendata/beneficiari/2021-2027/beneficiari_PR_FESR_LOMBARDIA.zip";
const MAX_BYTES = 64 * 1024 * 1024;

function hex(bytes: ArrayBuffer): string {
  return Array.from(new Uint8Array(bytes))
    .map((value) => value.toString(16).padStart(2, "0"))
    .join("");
}

Deno.serve(async (_request: Request) => {
  const upstream = await fetch(SOURCE_URL, {
    redirect: "follow",
    headers: {
      Accept: "application/zip,application/octet-stream",
      "User-Agent": "ProcRun/0.1 public-open-data-ingest",
    },
  });

  if (!upstream.ok) {
    console.error(`OpenCoesione transport failed with HTTP ${upstream.status}`);
    return new Response("upstream unavailable", { status: 502 });
  }
  if (upstream.url !== SOURCE_URL) {
    console.error("OpenCoesione redirected outside the frozen route");
    return new Response("source route drift", { status: 502 });
  }

  const contentType = (upstream.headers.get("content-type") ?? "").toLowerCase();
  if (!contentType.includes("zip") && !contentType.includes("octet-stream")) {
    console.error("OpenCoesione returned an unexpected content type");
    return new Response("source content drift", { status: 502 });
  }

  const payload = await upstream.arrayBuffer();
  if (payload.byteLength === 0 || payload.byteLength > MAX_BYTES) {
    console.error("OpenCoesione payload size is outside the frozen transport envelope");
    return new Response("source payload rejected", { status: 502 });
  }
  const prefix = new Uint8Array(payload.slice(0, 2));
  if (prefix[0] !== 0x50 || prefix[1] !== 0x4b) {
    console.error("OpenCoesione response is not a ZIP payload");
    return new Response("source payload rejected", { status: 502 });
  }

  const digest = await crypto.subtle.digest("SHA-256", payload);
  return new Response(payload, {
    status: 200,
    headers: {
      "Content-Type": "application/zip",
      "Cache-Control": "no-store",
      "X-ProcRun-Source-URL": SOURCE_URL,
      "X-ProcRun-Source-SHA256": hex(digest),
      "X-Content-Type-Options": "nosniff",
    },
  });
});
