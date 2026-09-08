import { clerkMiddleware } from "@clerk/nextjs/server";
import { NextResponse, type NextFetchEvent, type NextRequest } from "next/server";

import { applySecurityHeaders } from "@/lib/security-headers";

function clerkConfigured(): boolean {
  return Boolean(
    process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY?.trim() &&
      process.env.CLERK_SECRET_KEY?.trim(),
  );
}

const clerkProxy = clerkMiddleware();

export default async function proxy(request: NextRequest, event: NextFetchEvent) {
  const response = clerkConfigured()
    ? await clerkProxy(request, event)
    : NextResponse.next();

  return applySecurityHeaders(response, request.nextUrl.pathname);
}

export const config = {
  matcher: [
    "/((?!_next|[^?]*\\.(?:html?|css|js(?!on)|jpe?g|webp|png|gif|svg|ttf|woff2?|ico|csv|docx?|xlsx?|zip|webmanifest)).*)",
    "/(api|trpc)(.*)",
    "/__clerk/(.*)",
  ],
};
