export type Provider = "openai" | "azure" | "openrouter" | "gemini" | "local" | "bedrock";

export const PROVIDER_LABELS: Record<Provider, string> = {
  openai: "OpenAI",
  azure: "Azure",
  openrouter: "OpenRouter",
  gemini: "Gemini",
  local: "LocalLLM",
  bedrock: "Amazon Bedrock（東京リージョン）",
};

const SELECTABLE_PROVIDERS: Provider[] = ["openai", "azure", "openrouter", "gemini", "local"];

function isProvider(value: unknown): value is Provider {
  return typeof value === "string" && value in PROVIDER_LABELS;
}

// ビルド時に NEXT_PUBLIC_LLM_PROVIDER を指定すると、そのプロバイダだけを選べる。
// AWS の環境は NAT が無く外部の LLM に届かないので、bedrock を指定する。
const configuredProvider = process.env.NEXT_PUBLIC_LLM_PROVIDER;
const FIXED_PROVIDER: Provider | undefined = isProvider(configuredProvider) ? configuredProvider : undefined;

export const AVAILABLE_PROVIDERS: Provider[] = FIXED_PROVIDER ? [FIXED_PROVIDER] : SELECTABLE_PROVIDERS;

/**
 * 保存済みの設定や複製元の config にあるプロバイダを、この画面で選べる値にする。
 * プロバイダが固定されているときは常にその値。
 */
export function normalizeProvider(value: string | null | undefined, fallback: Provider): Provider {
  if (FIXED_PROVIDER) return FIXED_PROVIDER;
  return isProvider(value) ? value : fallback;
}

export function providerLabel(value: string | null | undefined): string {
  return isProvider(value) ? PROVIDER_LABELS[value] : value || "";
}

/** 埋め込みモデルをサーバー設定で決め、画面から変えないプロバイダ */
export function usesServerEmbedding(provider: string): boolean {
  return provider === "azure" || provider === "bedrock";
}
