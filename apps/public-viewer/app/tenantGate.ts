import { cookies, headers } from "next/headers";
import { redirect } from "next/navigation";

export async function ensureTenantCookie(path: string) {
  const incoming = await headers();
  if (!incoming.get("x-amzn-oidc-identity")) return;
  const jar = await cookies();
  if (jar.get("dd_tenant")) return;
  const host = incoming.get("x-forwarded-host") || incoming.get("host") || "";
  redirect(`/session?return=${encodeURIComponent(`https://${host}${path}`)}`);
}
