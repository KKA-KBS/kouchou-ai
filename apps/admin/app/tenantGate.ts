import { cookies, headers } from "next/headers";
import { redirect } from "next/navigation";

export async function adminTenantGate(path: string): Promise<"local" | "admin" | "member"> {
  const incoming = await headers();
  if (!incoming.get("x-amzn-oidc-identity")) return "local";
  const jar = await cookies();
  const host = incoming.get("x-forwarded-host") || incoming.get("host") || "";
  if (!jar.get("dd_tenant")) {
    redirect(`/session?return=${encodeURIComponent(`https://${host}${path}`)}`);
  }
  return jar.get("dd_role")?.value === "tenant-admin" ? "admin" : "member";
}
