"use server";

import { adminApiHeaders } from "@/app/utils/adminHeaders";
import { getApiBaseUrl } from "@/app/utils/api";
import type { PluginImportResult, PluginManifest, PluginPreviewResult } from "@/type.d";

/**
 * 利用可能なプラグイン一覧を取得
 */
export async function getPlugins(): Promise<PluginManifest[]> {
  const response = await fetch(`${getApiBaseUrl()}/admin/plugins`, {
    headers: {
      ...(await adminApiHeaders()),
    },
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch plugins: ${response.statusText}`);
  }

  const data = await response.json();
  return data.plugins;
}

/**
 * プラグインのソースURLを検証
 */
export async function validatePluginSource(
  pluginId: string,
  source: string,
): Promise<{ isValid: boolean; error: string | null }> {
  const encodedPluginId = encodeURIComponent(pluginId);
  const response = await fetch(`${getApiBaseUrl()}/admin/plugins/${encodedPluginId}/validate-source`, {
    method: "POST",
    headers: {
      ...(await adminApiHeaders()),
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ pluginId, source }),
  });

  if (!response.ok) {
    throw new Error(`Failed to validate source: ${response.statusText}`);
  }

  return response.json();
}

/**
 * プラグインからデータをプレビュー
 */
export async function previewPluginData(pluginId: string, source: string, limit = 10): Promise<PluginPreviewResult> {
  const encodedPluginId = encodeURIComponent(pluginId);
  const response = await fetch(`${getApiBaseUrl()}/admin/plugins/${encodedPluginId}/preview`, {
    method: "POST",
    headers: {
      ...(await adminApiHeaders()),
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ source, limit }),
  });

  if (!response.ok) {
    throw new Error(`Failed to preview data: ${response.statusText}`);
  }

  return response.json();
}

/**
 * プラグインからデータをインポート
 */
export async function importPluginData(
  pluginId: string,
  source: string,
  fileName: string,
  maxResults = 1000,
  includeReplies = false,
): Promise<PluginImportResult> {
  const encodedPluginId = encodeURIComponent(pluginId);
  const response = await fetch(`${getApiBaseUrl()}/admin/plugins/${encodedPluginId}/import`, {
    method: "POST",
    headers: {
      ...(await adminApiHeaders()),
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      source,
      fileName,
      maxResults,
      includeReplies,
    }),
  });

  if (!response.ok) {
    throw new Error(`Failed to import data: ${response.statusText}`);
  }

  return response.json();
}
