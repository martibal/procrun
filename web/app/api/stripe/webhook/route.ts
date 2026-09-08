import { NextResponse } from "next/server";

import { applyStripeEvent, verifyStripeSignature } from "@/lib/billing";

export const dynamic = "force-dynamic";

export async function POST(request: Request): Promise<NextResponse> {
  const payload = await request.text();
  const signature = request.headers.get("stripe-signature") ?? "";

  if (!verifyStripeSignature(payload, signature)) {
    return NextResponse.json({ ok: false }, { status: 400 });
  }

  let event: Record<string, unknown>;
  try {
    event = JSON.parse(payload) as Record<string, unknown>;
  } catch {
    return NextResponse.json({ ok: false }, { status: 400 });
  }

  try {
    await applyStripeEvent(event);
  } catch {
    return NextResponse.json({ ok: false }, { status: 503 });
  }

  return NextResponse.json({ ok: true });
}
