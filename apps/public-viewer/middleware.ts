import { type NextRequest, NextResponse } from "next/server";

export function middleware(req: NextRequest) {
  if (!req.headers.get("x-amzn-oidc-identity")) return NextResponse.next();
  if (req.cookies.get("dd_tenant")) return NextResponse.next();
  const host = req.headers.get("x-forwarded-host") || req.headers.get("host") || "";
  const returnTo = encodeURIComponent(`https://${host}${req.nextUrl.pathname}${req.nextUrl.search}`);
  return NextResponse.redirect(new URL(`/session?return=${returnTo}`, req.url));
}

export const config = {
  matcher: ["/((?!session|logout|logged-out|_next|meta).*)"],
};
