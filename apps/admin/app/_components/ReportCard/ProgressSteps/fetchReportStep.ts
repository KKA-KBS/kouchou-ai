"use server";

import { getApiBaseUrl } from "@/app/utils/api";
import { adminApiHeaders } from "@/app/utils/adminHeaders";

export async function fetchReportStep(slug: string) {
  const response = await fetch(`${getApiBaseUrl()}/admin/reports/${encodeURIComponent(slug)}/status/step-json`, {
    headers: {
      ...(await adminApiHeaders()),
      "Cache-Control": "no-cache, no-store, must-revalidate",
      Pragma: "no-cache",
    },
  });
  if (!response.ok) {
    return { ok: false as const };
  }
  const body = (await response.json()) as {
    status?: string;
    current_step?: string;
    error_message?: string | null;
    error_log_excerpt?: string | null;
  };
  return { ok: true as const, body };
}
