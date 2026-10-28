export async function adminApiHeaders(): Promise<Record<string, string>> {
  const result: Record<string, string> = {
    "x-api-key": process.env.ADMIN_API_KEY || "",
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
    // リクエスト外では ALB のヘッダは付かない
  }
  return result;
}
