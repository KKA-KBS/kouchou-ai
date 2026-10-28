"use server";

import { getApiBaseUrl } from "@/app/utils/api";
import { adminApiHeaders } from "@/app/utils/adminHeaders";

export async function fetchModelCatalog(provider: string, address?: string) {
  const params = new URLSearchParams({ provider });
  if (provider === "local" && address) params.set("address", address.trim());
  const response = await fetch(`${getApiBaseUrl()}/admin/models?${params}`, {
    method: "GET",
    headers: await adminApiHeaders(),
  });
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  const models: unknown = await response.json();
  if (!Array.isArray(models)) throw new Error("Invalid catalog");
  return models;
}
