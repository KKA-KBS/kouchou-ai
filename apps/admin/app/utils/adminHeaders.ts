function tenantFromCookie(cookie: string | null): string {
  if (!cookie) return "";
  for (const part of cookie.split(";")) {
    const [key, ...rest] = part.trim().split("=");
    if (key === "dd_tenant") return decodeURIComponent(rest.join("="));
  }
  return "";
}

export async function adminApiHeaders(): Promise<Record<string, string>> {
  const result: Record<string, string> = {
    "x-api-key": process.env.ADMIN_API_KEY || "",
    "Content-Type": "application/json",
  };
  try {
    const { headers } = await import("next/headers");
    const incoming = await headers();
    const sub = incoming.get("x-amzn-oidc-identity");
    const tenant = incoming.get("x-tenant-id") || tenantFromCookie(incoming.get("cookie"));
    if (sub) result["x-amzn-oidc-identity"] = sub;
    if (tenant) result["x-tenant-id"] = tenant;
  } catch {
    // リクエスト外では ALB のヘッダは付かない
  }
  return result;
}
