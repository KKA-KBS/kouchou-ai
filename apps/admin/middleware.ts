import { type NextRequest, NextResponse } from "next/server";

function tenantGate(req: NextRequest) {
  if (!req.headers.get("x-amzn-oidc-identity")) return null;
  if (req.nextUrl.pathname === "/not-admin") return null;
  if (!req.cookies.get("dd_tenant")) {
    const host = req.headers.get("x-forwarded-host") || req.headers.get("host") || "";
    const returnTo = encodeURIComponent(`https://${host}${req.nextUrl.pathname}${req.nextUrl.search}`);
    return NextResponse.redirect(new URL(`/session?return=${returnTo}`, req.url));
  }
  if (req.cookies.get("dd_role")?.value !== "tenant-admin") {
    return NextResponse.rewrite(new URL("/not-admin", req.url));
  }
  return null;
}

export function middleware(req: NextRequest) {
  if (req.nextUrl.pathname === "/api/healthcheck") {
    return NextResponse.next();
  }

  const gated = tenantGate(req);
  if (gated) return gated;

  if (
    process.env.BASIC_AUTH_USERNAME === undefined ||
    process.env.BASIC_AUTH_PASSWORD === undefined ||
    process.env.BASIC_AUTH_USERNAME === "" ||
    process.env.BASIC_AUTH_PASSWORD === ""
  ) {
    return NextResponse.next();
  }
  const basicAuth = req.headers.get("authorization");
  if (basicAuth) {
    const authValue = basicAuth.split(" ")[1];
    const [username, password] = Buffer.from(authValue, "base64").toString().split(":");
    if (username === process.env.BASIC_AUTH_USERNAME && password === process.env.BASIC_AUTH_PASSWORD) {
      return NextResponse.next();
    }
  }
  return NextResponse.json(
    { error: "Basic Auth Required" },
    {
      headers: { "WWW-Authenticate": 'Basic realm="Secure Area"' },
      status: 401,
    },
  );
}
