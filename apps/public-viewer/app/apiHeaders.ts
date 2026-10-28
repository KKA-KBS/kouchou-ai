export async function publicApiHeaders(): Promise<Record<string, string>> {
  const result: Record<string, string> = {
    "x-api-key": process.env.PUBLIC_API_KEY || "",
    "Content-Type": "application/json",
  };
  try {
    const { headers } = await import("next/headers");
    const incoming = await headers();
    const sub = incoming.get("x-amzn-oidc-identity");
    const tenant = incoming.get("x-tenant-id");
    if (sub) result["x-amzn-oidc-identity"] = sub;
    if (tenant) result["x-tenant-id"] = tenant;
  } catch {
    // ビルド時やリクエスト外
  }
  return result;
}
